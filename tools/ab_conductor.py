#!/usr/bin/env python3
"""Unattended server A/B queue runner. It UPLOADS builds (unswbc submit), so start it only on purpose.

usage (run from the project root):
  python3 tools/ab_conductor.py --dry-run              # print what it would do; no upload, no state/log writes
  python3 tools/ab_conductor.py --dry-run --preflight  # also stage + compile + one local sandbox game for the
                                                       # next pending candidate (local only)
  nohup python3 tools/ab_conductor.py >> replays/ab_stage/conductor.log 2>&1 &      # the real thing
  options: --poll 600   seconds between checks      --once   one pass, then exit
           --hold-lock  create codex-battlecode/coord/SERVER_LOCK while running (the challenge loop then needs
                        --ignore-lock); without it the conductor only waits while someone else's lock exists
  stop:    touch replays/ab_stage/STOP   (it restores the last accepted build if a candidate is live, then exits)

Queue / state file notes/ab_queue.json (rewritten atomically; edit it while the conductor sleeps, it is re-read
before every change):
  {"baseline": {"name": "v61", "dir": "variants/v61", "flags": [], "since": null},
   "accepted_flags": [],
   "rules": {...optional overrides of RULES below...},
   "queue": [{"name": "c1", "flags": ["SPLIT_NEEDS_EXIT=1", ...],
              "mech": {"stat": "stillborn_by_r100", "direction": "down", "min_rel_change": 0.2},
              "maps": null}]}
  maps = list of map names for a map-specific candidate (judged on those maps only). mech.stat is any stat of
  tools/ab_mech.py. The conductor adds "status" (pending -> running -> accepted | rejected | aborted), "base",
  "stage1", "stage2", "decision" to each candidate and a top-level "state".

Per candidate:
  1. stage: copy bot/ (without .unswbc-build, *.orig) to replays/ab_stage/<name>/ and put `#define FLAG VALUE`
     lines (accepted_flags + candidate flags) at the top of params.hpp. Every flag must have an #ifndef guard.
  2. pre-flight: compile + one sandbox game vs variants/v61 on maps/sprint/australia.map; needs a result line,
     no error text and max points/turn < 38M. Otherwise the candidate is aborted (nothing uploaded).
  3. upload with `unswbc submit <stage> -n <name> -d <desc>` and wait until the server shows it active.
     A candidate whose name is already the active submission is picked up as running (no upload).
  4. every --poll seconds, with n = candidate games (on its maps if map-specific):
     stage 1 at n >= 50 (25): tools/ab_mech.py stat must move the right way by min_rel_change relative to the
       comparison build AND the total length ratio at r100 must not be down more than 10%. Else REJECT.
     stage 2 (tools/ab_server.py --adjusted): at n >= 120 REJECT if P(better) < 0.10 (all-maps candidates);
       at n >= 250 (60) ACCEPT if the adjusted contrast >= -1 pp (>= 0 pp for map-specific) and stage 1
       passed, else REJECT.
  ACCEPT: flags join accepted_flags; the build stays live and becomes the base of the next stage.
  REJECT: the previous live build is restored by uploading its identical stage dir (variants/v61 if nothing was
     accepted yet) and the conductor waits until it is active.
  Comparison build ("base" of a candidate) = the build that was live before it (rules.compare_to = "previous",
  default) or always the baseline (rules.compare_to = "baseline").
Safety: at most 10 uploads per hour (server limit 12), counted from the server's own submission list; pauses
if the active submission is not the one it expects (someone uploaded by hand) or while a foreign SERVER_LOCK
exists; never prints the API key. Events are appended to notes/ab_queue_log.md.
"""
import argparse
import contextlib
import datetime as dt
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ab_mech  # noqa: E402
import ab_server  # noqa: E402
import api  # noqa: E402

QUEUE = ROOT / "notes" / "ab_queue.json"
LOGF = ROOT / "notes" / "ab_queue_log.md"
STAGE = ROOT / "replays" / "ab_stage"
STOP = STAGE / "STOP"
LOCK = ROOT / "codex-battlecode" / "coord" / "SERVER_LOCK"
ARCHIVE = ROOT / "archive" / "ab_stage"
PF_MAP = "maps/sprint/australia.map"
PF_OPP = "variants/v61"

RULES = {
    "stage1_games": 50, "stage1_games_maps": 25,
    "early_games": 120, "early_p_better": 0.10,
    "decide_games": 250, "decide_games_maps": 60,
    "accept_pp": -1.0, "accept_pp_maps": 0.0,
    "len_ratio_floor": 0.90,          # candidate / base total length ratio at r100
    "mech_base_limit": 120,           # replays analysed for the comparison build
    "mech_cand_limit": 150,
    "max_points_m": 38.0,
    "uploads_per_hour": 10,
    "compare_to": "previous",
}
DRY = False


def now():
    return dt.datetime.now(dt.timezone.utc)


def stamp():
    t = now()
    e = t - dt.timedelta(hours=4)
    return f"{t:%Y-%m-%d %H:%M} UTC ({e:%-I:%M %p} EDT)"


def scrub(text):
    """Remove the API key from any text before it is printed or logged."""
    try:
        k = api.key()
        if k:
            text = text.replace(k, "<key>")
    except Exception:  # noqa: BLE001
        pass
    return text


def say(msg):
    print(f"{now():%H:%M:%S} {scrub(msg)}", flush=True)


def logmd(msg):
    msg = scrub(msg)
    say(("[dry-run] " if DRY else "") + msg)
    if DRY:
        return
    new = not LOGF.exists()
    with open(LOGF, "a") as f:
        if new:
            f.write("# A/B queue log (tools/ab_conductor.py)\n\n")
        f.write(f"- {stamp()}: {msg}\n")


def load_q():
    q = json.loads(QUEUE.read_text())
    q.setdefault("accepted_flags", [])
    q.setdefault("queue", [])
    q.setdefault("state", {})
    for c in q["queue"]:
        c.setdefault("status", "pending")
    return q


def save_q(q):
    if DRY:
        return
    tmp = QUEUE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(q, indent=1) + "\n")
    tmp.replace(QUEUE)


def update(name, **kw):
    """Re-read the queue file, change one candidate (and/or top-level keys given as _key), write it back."""
    q = load_q()
    for k, v in kw.items():
        if k.startswith("_"):
            q[k[1:]] = v
    c = next((c for c in q["queue"] if c["name"] == name), None)
    if c is not None:
        c.update({k: v for k, v in kw.items() if not k.startswith("_")})
    save_q(q)
    return q


def rules(q):
    return {**RULES, **(q.get("rules") or {})}


def merge_flags(*lists):
    d = {}
    for fl in lists:
        for f in fl or []:
            k, _, v = f.partition("=")
            d[k.strip()] = v.strip() or "1"
    return [f"{k}={v}" for k, v in d.items()]


def last_good(q):
    return q["state"].get("last_good") or {"name": q["baseline"]["name"], "dir": q["baseline"]["dir"]}


# ---------------------------------------------------------------- server helpers
def subs_sorted():
    return sorted(api.get("/api/v1/submissions"), key=lambda s: s["uploadedAt"])


def active_sub(subs=None):
    subs = subs or subs_sorted()
    act = [s for s in subs if s.get("status") == "active"]
    return act[-1] if act else None


def uploads_last_hour(subs):
    cut = now() - dt.timedelta(hours=1)
    return sum(ab_server.parse_t(s["uploadedAt"]) >= cut for s in subs)


def foreign_lock():
    if not LOCK.exists():
        return False
    try:
        return "ab_conductor" not in LOCK.read_text()
    except Exception:  # noqa: BLE001
        return True


# ---------------------------------------------------------------- stage / pre-flight / submit
def do_stage(name, flags):
    """Fresh stage dir from bot/ with the flags forced at the top of params.hpp. Returns (dir, error)."""
    d = STAGE / name
    if d.exists():
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d), str(ARCHIVE / f"{name}_{now():%Y%m%dT%H%M%S}"))
    d.mkdir(parents=True)
    r = subprocess.run(["rsync", "-a", "--exclude", ".unswbc-build", "--exclude", "*.orig",
                        str(ROOT / "bot") + "/", str(d) + "/"], capture_output=True, text=True)
    if r.returncode:
        return d, f"rsync failed: {r.stderr[-300:]}"
    src = "".join(p.read_text(errors="replace") for p in list(d.glob("*.hpp")) + list(d.glob("*.cpp")))
    lines = []
    for f in flags:
        k, _, v = f.partition("=")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) or not re.fullmatch(r"[-+.A-Za-z0-9_]+", v):
            return d, f"bad flag {f!r}"
        if not re.search(rf"#\s*ifndef\s+{k}\b", src):
            return d, f"flag {k} has no #ifndef guard in bot/ (unknown flag?)"
        lines.append(f"#define {k} {v}")
    p = d / "params.hpp"
    txt = p.read_text()
    block = "// --- forced by tools/ab_conductor.py ---\n" + "\n".join(lines) + "\n// ---\n"
    if txt.startswith("#pragma once"):
        head, _, rest = txt.partition("\n")
        txt = head + "\n" + block + rest
    else:
        txt = block + txt
    p.write_text(txt)
    return d, None


def preflight(d, max_m):
    """One sandbox game vs PF_OPP. Returns (ok, text summary)."""
    rp = STAGE / f"{d.name}_preflight.replay"
    try:
        r = subprocess.run(["unswbc", "run", PF_MAP, str(d), PF_OPP, "--seed", "1", "--no-logs", "--sandbox",
                            "-o", str(rp)], cwd=ROOT, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return False, "pre-flight timed out (900 s)"
    txt = r.stdout + "\n" + r.stderr
    res = [ln for ln in txt.splitlines() if re.search(r"team [AB] wins|draw", ln)]
    cpu = re.search(r"team A points per turn:.*max ([0-9.]+)M", txt)
    bad = [ln for ln in txt.splitlines() if re.search(
        r"(?i)\b(error|crash|exception|segfault|signal|timed out|time limit|invalid|forfeit|could not|failed)\b", ln)]
    if r.returncode or not res or not cpu:
        return False, f"pre-flight failed (exit {r.returncode}): {' | '.join(txt.strip().splitlines()[-3:])[:400]}"
    m = float(cpu.group(1))
    summ = f"{res[-1].strip()}; max {m:.1f}M points/turn"
    if bad:
        return False, f"pre-flight error text: {bad[0][:200]} ({summ})"
    if m >= max_m:
        return False, f"pre-flight CPU too high ({summ}, limit {max_m}M)"
    return True, summ


def wait_budget(q):
    lim = rules(q)["uploads_per_hour"]
    while True:
        n = uploads_last_hour(subs_sorted())
        if n < lim:
            return
        say(f"{n} uploads in the last hour (limit {lim}); waiting 5 min")
        time.sleep(300)


def submit(d, name, desc, q):
    """Upload d as `name` and wait until it is active. Returns the submission dict or None."""
    while foreign_lock():
        say("foreign SERVER_LOCK present; waiting 2 min before uploading")
        time.sleep(120)
    wait_budget(q)
    before = max((s["id"] for s in subs_sorted()), default=0)
    r = subprocess.run(["unswbc", "submit", str(d), "-n", name, "-d", desc], cwd=ROOT, capture_output=True, text=True)
    tail = " | ".join((r.stdout + r.stderr).strip().splitlines()[-3:])[:300]
    if r.returncode:
        logmd(f"upload of {name} failed (exit {r.returncode}): {tail}")
        return None
    t0 = time.time()
    while time.time() - t0 < 1500:
        time.sleep(20)
        try:
            new = [s for s in subs_sorted() if s["id"] > before and s["name"] == name]
        except Exception as e:  # noqa: BLE001
            say(f"submissions poll failed: {e}")
            continue
        if not new:
            if time.time() - t0 > 180:
                logmd(f"upload of {name}: no new submission on the server after 3 min ({tail})")
                return None
            continue
        s = new[-1]
        st = str(s.get("status"))
        if st == "active":
            return s
        if re.search(r"(?i)fail|error|reject", st):
            logmd(f"upload of {name}: server build status {st}")
            return None
    logmd(f"upload of {name}: not active after 25 min")
    return None


def submit_retry(d, name, desc, q, tries=3):
    for k in range(tries):
        s = submit(d, name, desc, q)
        if s:
            return s
        if k + 1 < tries:
            time.sleep(600)
    return None


# ---------------------------------------------------------------- evaluation
def evaluate(q, c):
    """Returns (decision, reason, patch): decision in (None, 'accept', 'reject'); patch = fields to store."""
    R = rules(q)
    name, maps = c["name"], c.get("maps") or None
    base = c.get("base") or q["baseline"]["name"]
    since = [f"{q['baseline']['name']}={q['baseline']['since']}"] if q["baseline"].get("since") else []
    labels = [base, name]
    with contextlib.redirect_stderr(io.StringIO()):
        C = ab_server.collect(labels, since=since, context=True)
    rows = C["rows"]
    if maps:
        rows = {k: [r for r in v if r["map"] in maps] for k, v in rows.items()}
    n = len(rows[name])
    patch = {"games": n}
    s1_at = R["stage1_games_maps" if maps else "stage1_games"]
    dec_at = R["decide_games_maps" if maps else "decide_games"]
    acc_pp = R["accept_pp_maps" if maps else "accept_pp"]
    scope = f" on {'/'.join(maps)}" if maps else ""
    say(f"{name}: {n} games{scope} (stage 1 at {s1_at}, decision at {dec_at}); base {base} {len(rows[base])} games")

    # ---- stage 1: mechanism gate (evaluated once it is measurable)
    s1 = c.get("stage1")
    if n >= s1_at and not (s1 and s1.get("done")):
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            mb = ab_mech.summarise(ab_mech.mech_rows(base, rows[base], R["mech_base_limit"], quiet=True))
            mc = ab_mech.summarise(ab_mech.mech_rows(name, rows[name], R["mech_cand_limit"], quiet=True))
        s1 = {"done": False, "at_games": n, "n_base": mb["win"]["n"], "n_cand": mc["win"]["n"]}
        lb, lc = mb["len_ratio_r100"], mc["len_ratio_r100"]
        ok_len, len_txt = None, "length ratio r100 not measurable yet"
        if lb["v"] and lc["v"]:
            rel = lc["v"] / lb["v"]
            ok_len = rel >= R["len_ratio_floor"]
            s1.update(len_base=round(lb["v"], 3), len_cand=round(lc["v"], 3), len_rel=round(rel, 3))
            len_txt = f"length ratio r100 {lb['v']:.2f} -> {lc['v']:.2f} (x{rel:.2f}, floor x{R['len_ratio_floor']})"
        m = c.get("mech") or {}
        ok_stat, stat_txt = True, "no mechanism stat set"
        if m.get("stat"):
            if m["stat"] not in ab_mech.STATS:
                ok_stat, stat_txt = False, f"unknown mech stat {m['stat']}"
            else:
                vb, vc = mb[m["stat"]]["v"], mc[m["stat"]]["v"]
                up = m.get("direction", "up") == "up"
                need = float(m.get("min_rel_change", 0))
                if vb is None or vc is None:
                    ok_stat, stat_txt = None, f"{m['stat']} not measurable yet"
                else:
                    if vb == 0:
                        rel = 0.0 if vc == 0 else (float("inf") if vc > 0 else float("-inf"))
                    else:
                        rel = (vc - vb) / abs(vb)
                    ok_stat = (rel >= need) if up else (rel <= -need)
                    s1.update(stat=m["stat"], stat_base=round(vb, 4), stat_cand=round(vc, 4),
                              stat_rel=None if rel in (float("inf"), float("-inf")) else round(rel, 3))
                    stat_txt = (f"{m['stat']} {vb:.3f} -> {vc:.3f} ({rel:+.0%}; needs "
                                f"{'+' if up else '-'}{need:.0%})")
        if ok_len is None or ok_stat is None:
            say(f"{name}: stage 1 waiting: {stat_txt}; {len_txt}")
        else:
            s1["done"] = True
            s1["passed"] = bool(ok_len and ok_stat)
            logmd(f"{name} stage 1 at {n} games{scope} vs {base} ({s1['n_cand']} / {s1['n_base']} replays): "
                  f"{stat_txt}; {len_txt} -> {'PASS' if s1['passed'] else 'FAIL'}")
        patch["stage1"] = s1
        if s1.get("done") and not s1["passed"]:
            return "reject", "stage 1 mechanism gate failed", patch

    # ---- stage 2: adjusted win-rate model
    if n >= min(R["early_games"], dec_at):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = ab_server.adjusted(labels, rows, C["ctx"])
        if not res:
            return None, "", patch
        a = res[0]
        s2 = {"at_games": n, "pp": round(a["pp"], 2), "lo": round(a["lo"], 2), "hi": round(a["hi"], 2),
              "p_better": round(a["p_better"], 3), "n_base": a["n_base"], "base": base}
        patch["stage2"] = s2
        txt = (f"{name} vs {base}{scope}: adjusted {a['pp']:+.1f} pp (95% CI {a['lo']:+.1f}..{a['hi']:+.1f}), "
               f"P(better) {a['p_better']:.2f}, n = {a['n_base']} / {n}")
        if n >= dec_at:
            if not (s1 and s1.get("done")):
                return "reject", f"{txt}; stage 1 never became measurable", patch
            if a["pp"] >= acc_pp:
                return "accept", f"{txt}; at least {acc_pp:+.1f} pp and stage 1 passed", patch
            return "reject", f"{txt}; below {acc_pp:+.1f} pp", patch
        if not maps and n >= R["early_games"] and a["p_better"] < R["early_p_better"]:
            return "reject", f"{txt}; P(better) below {R['early_p_better']:.2f} at {n} games", patch
        say(txt + " (no decision yet)")
    return None, "", patch


def restore(q, why):
    """Upload the last accepted build again (identical dir). Returns True when it is active."""
    lg = last_good(q)
    act = active_sub()
    if act and act["name"] == lg["name"]:
        return True
    d = ROOT / lg["dir"]
    logmd(f"restoring {lg['name']} from {lg['dir']} ({why})")
    if DRY:
        return True
    s = submit_retry(d, lg["name"], f"restore: {why}"[:120], q)
    if not s:
        logmd(f"RESTORE OF {lg['name']} FAILED. Conductor stops; upload {lg['dir']} by hand.")
        return False
    logmd(f"{lg['name']} active again (submission {s['id']})")
    q = load_q()
    q["state"]["live"] = {"name": lg["name"], "dir": lg["dir"], "sub_id": s["id"]}
    save_q(q)
    return True


def start_candidate(q, c, do_preflight=True):
    """Stage, pre-flight and upload. Returns 'running', 'aborted' or 'failed'."""
    name = c["name"]
    R = rules(q)
    flags = merge_flags(q["baseline"].get("flags"), q["accepted_flags"], c.get("flags"))
    base = last_good(q)["name"] if R["compare_to"] == "previous" else q["baseline"]["name"]
    if DRY and not do_preflight:
        say(f"[dry-run] would stage bot/ -> replays/ab_stage/{name}/ with {flags}; pre-flight vs {PF_OPP} on "
            f"{PF_MAP} (max < {R['max_points_m']}M); unswbc submit replays/ab_stage/{name} -n {name}; "
            f"then compare with {base}")
        return "running"
    d, err = do_stage(name, flags)
    if err:
        logmd(f"{name} ABORTED at staging: {err}")
        update(name, status="aborted", decision={"at": stamp(), "why": err})
        return "aborted"
    ok, txt = preflight(d, R["max_points_m"])
    if not ok:
        logmd(f"{name} ABORTED at pre-flight: {txt}")
        update(name, status="aborted", decision={"at": stamp(), "why": txt})
        return "aborted"
    logmd(f"{name} staged with {flags}; pre-flight ok ({txt})")
    if DRY:
        say(f"[dry-run] would now run: unswbc submit replays/ab_stage/{name} -n {name}; compare with {base}")
        return "running"
    s = submit_retry(d, name, ("A/B: " + " ".join(flags))[:120], q)
    if not s:
        logmd(f"{name}: upload failed three times; conductor stops (candidate stays pending)")
        return "failed"
    logmd(f"{name} uploaded and active (submission {s['id']}); comparing with {base}")
    q = update(name, status="running", base=base, dir=f"replays/ab_stage/{name}", sub_id=s["id"])
    q["state"]["live"] = {"name": name, "dir": f"replays/ab_stage/{name}", "sub_id": s["id"]}
    save_q(q)
    return "running"


def step(a):
    """One pass. Returns seconds to sleep, or None to exit."""
    q = load_q()
    R = rules(q)
    subs = subs_sorted()
    act = active_sub(subs)
    actn = act["name"] if act else None
    lg = last_good(q)
    c = next((c for c in q["queue"] if c["status"] in ("pending", "running")), None)

    if STOP.exists():
        logmd("STOP file found")
        if actn != lg["name"]:
            restore(q, "STOP requested")
            if c and c["status"] == "running":
                update(c["name"], status="pending", note="interrupted by STOP; games so far stay under this name")
        return None
    if c is None:
        say(f"queue empty; live = {actn}, last accepted = {lg['name']}")
        return None if (a.once or a.exit_when_empty) else a.poll

    name = c["name"]
    if c["status"] == "pending":
        if actn == name:
            base = lg["name"] if R["compare_to"] == "previous" else q["baseline"]["name"]
            logmd(f"{name} is already the active submission ({act['id']}, uploaded {act['uploadedAt'][:16]} UTC): "
                  f"picked up as running, not re-uploaded; comparing with {base}")
            q = update(name, status="running", base=base, sub_id=act["id"], adopted=True)
            q["state"]["live"] = {"name": name, "dir": None, "sub_id": act["id"]}
            save_q(q)
            if DRY:
                c = dict(c, status="running", base=base)
            else:
                return 5
        elif actn != lg["name"]:
            say(f"active submission is {actn}, expected {lg['name']} before starting {name}: waiting "
                f"(someone uploaded by hand?)")
            return a.poll
        else:
            r = start_candidate(q, c, do_preflight=not DRY or a.preflight)
            if DRY:
                return None
            return {"running": a.poll, "aborted": 5}.get(r)

    # running
    if actn != name:
        say(f"{name} is marked running but the active submission is {actn}: waiting (someone uploaded by hand?)")
        return a.poll
    dec, why, patch = evaluate(q, c)
    if dec is None:
        update(name, **patch)
        return a.poll
    patch["decision"] = {"at": stamp(), "result": dec, "why": why}
    if dec == "accept":
        logmd(f"{name} ACCEPTED: {why}. Flags {c.get('flags')} join accepted_flags; {name} stays live.")
        if DRY:
            return None
        q = update(name, status="accepted", **patch)
        d = c.get("dir")
        if not d:
            # adopted build without a stage dir: rebuild one so it can be restored later
            sd, err = do_stage(name, merge_flags(q["baseline"].get("flags"), q["accepted_flags"], c.get("flags")))
            d = f"replays/ab_stage/{name}"
            logmd(f"{name} had no stage dir (picked up live); rebuilt {d} from the current bot/"
                  + (f" (problem: {err})" if err else ""))
        q = load_q()
        q["accepted_flags"] = merge_flags(q["accepted_flags"], c.get("flags"))
        q["state"]["last_good"] = {"name": name, "dir": d}
        save_q(q)
        return 5
    logmd(f"{name} REJECTED: {why}")
    if DRY:
        say(f"[dry-run] would restore {lg['name']} from {lg['dir']}")
        return None
    update(name, status="rejected", **patch)
    if not restore(load_q(), f"{name} rejected"):
        return None
    return 5


def main():
    global DRY
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--preflight", action="store_true", help="with --dry-run: really stage + run the local pre-flight")
    ap.add_argument("--poll", type=int, default=600)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--exit-when-empty", action="store_true")
    ap.add_argument("--hold-lock", action="store_true")
    a = ap.parse_args()
    DRY = a.dry_run
    if not QUEUE.exists():
        sys.exit(f"missing {QUEUE}")
    STAGE.mkdir(parents=True, exist_ok=True)
    if a.hold_lock and not DRY:
        if foreign_lock():
            sys.exit("a foreign SERVER_LOCK exists")
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        LOCK.write_text(f"ab_conductor since {now().isoformat()}\n")
    say(f"conductor start{' (dry-run)' if DRY else ''}; queue {QUEUE.relative_to(ROOT)}")
    try:
        while True:
            try:
                nap = step(a)
            except Exception as e:  # noqa: BLE001
                say(f"cycle error: {type(e).__name__}: {e}")
                nap = min(a.poll, 300)
            if nap is None or a.once or DRY:
                break
            time.sleep(nap)
    finally:
        if a.hold_lock and not DRY and LOCK.exists() and not foreign_lock():
            dst = ROOT / "archive" / "locks"
            dst.mkdir(parents=True, exist_ok=True)
            shutil.move(str(LOCK), str(dst / f"SERVER_LOCK_{now():%Y%m%dT%H%M%S}"))
    say("conductor exit")


if __name__ == "__main__":
    main()
