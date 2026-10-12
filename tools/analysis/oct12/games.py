#!/usr/bin/env python3
"""games.py RUN --games FILE [--jobs 5] [-v]: sandbox games, one replay each, results in work/oct12/results/RUN.jsonl.
FILE lines: tag<TAB>map<TAB>botA<TAB>botB<TAB>seed.  With -v: per-team max points per turn + max memory parsed from the
verbose transcript (not kept). Resumable (skips tags already in the jsonl)."""
import argparse, concurrent.futures as cf, json, pathlib, re, subprocess, time

ROOT = pathlib.Path("/Users/devsingh/Developer/UNSW_Battlecode")
W = ROOT / "work/oct12"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PM = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)$")
RESULT = re.compile(r"^(team [AB] wins after \d+ rounds.*|draw after \d+ rounds.*)$")
SUMMARY = re.compile(r"^team ([AB]) points per turn: p50 (\S+)\s+p99 (\S+)\s+mean (\S+)\s+max (\S+)M\s+\((\d+) turns\)")
ERR = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) (?!points|stdout:|stderr:|died: (hit|ran|walked|collided|was))(.*)$")


def play(tag, mp, a, b, seed, run, verbose):
    rp = W / "replays" / run / f"{tag}.replay"
    rp.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["unswbc", "run", str(ROOT / mp), str(ROOT / a), str(ROOT / b), "--seed", str(seed), "--sandbox",
           "-o", str(rp), "--no-logs"] + (["-v"] if verbose else [])
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT, errors="replace")
    st = {T: {"max": 0, "max_at": None, "mem": 0, "turns": 0, "n70": 0, "n100": 0, "deaths": {}} for T in "AB"}
    result, summary, other = None, {}, []
    for raw in p.stdout:
        line = ANSI.sub("", raw.rstrip("\n"))
        m = PM.match(line)
        if m:
            T = st[m.group(3)]
            pts, mem = int(m.group(4)), int(m.group(5))
            T["turns"] += 1
            T["mem"] = max(T["mem"], mem)
            T["n70"] += pts > 70_000_000
            T["n100"] += pts > 100_000_000
            if pts > T["max"]:
                T["max"], T["max_at"] = pts, (int(m.group(1)), int(m.group(2)))
            continue
        if " died: " in line and line.startswith("round "):
            mm = re.match(r"^round \d+: bot \d+ \(team ([AB])\) died: (.*)$", line)
            if mm:
                d = st[mm.group(1)]["deaths"]
                d[mm.group(2)] = d.get(mm.group(2), 0) + 1
            continue
        if RESULT.match(line):
            result = line
            continue
        s = SUMMARY.match(line)
        if s:
            summary[s.group(1)] = {"p50": s.group(2), "p99": s.group(3), "mean": s.group(4), "max": float(s.group(5)),
                                   "turns": int(s.group(6))}
            continue
        if line.startswith("round ") and (" error" in line or "timeout" in line.lower() or "invalid" in line.lower()):
            if len(other) < 20:
                other.append(line[:200])
    rc = p.wait()
    return {"tag": tag, "map": mp, "A": a, "B": b, "seed": seed, "rc": rc, "result": result, "summary": summary,
            "teams": st if verbose else None, "notes": other, "replay": str(rp.relative_to(ROOT)),
            "secs": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--games", required=True)
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    assert a.jobs <= 5
    games = [l.rstrip("\n").split("\t") for l in open(a.games) if l.strip() and not l.startswith("#")]
    out = W / "results" / f"{a.run}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["tag"] for l in open(out)} if out.exists() else set()
    todo = [g for g in games if g[0] not in done]
    with cf.ThreadPoolExecutor(a.jobs) as ex, open(out, "a") as f:
        futs = {ex.submit(play, g[0], g[1], g[2], g[3], int(g[4]), a.run, a.v): g for g in todo}
        for fut in cf.as_completed(futs):
            g = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:
                rec = {"tag": g[0], "map": g[1], "exception": repr(e)}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            sm = rec.get("summary") or {}
            extra = ""
            if rec.get("teams"):
                extra = " | " + " ".join(f"{T} {rec['teams'][T]['max'] / 1e6:.1f}M {rec['teams'][T]['mem'] / 2**20:.2f}MB"
                                         for T in "AB")
            print(f"{rec['tag']:40s} {rec.get('secs', 0):5.0f}s {(rec.get('result') or '?')[:70]}"
                  f" | maxA {sm.get('A', {}).get('max', '?')} maxB {sm.get('B', {}).get('max', '?')}{extra}", flush=True)


if __name__ == "__main__":
    main()
