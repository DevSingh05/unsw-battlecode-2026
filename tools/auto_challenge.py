#!/usr/bin/env python3
"""Keep the challenge budget busy with useful games (user-approved 2026-09-29).

Every CYCLE seconds, tops the games WE launched in the last hour up to --per-hour (default 40 of the
60/hour limit, leaving room for version tests):
  - ranked 5-game series vs teams within +-RANGE ranks of us (higher-ranked first)
  - unranked 5-map series vs the top-N teams, maps rotating, weighted to our weak maps
Pauses while codex-battlecode/coord/SERVER_LOCK exists (a test version is active: games would be
misattributed). Skips opponents with a pending battle. Backs off on HTTP 429.
Stop it by creating replays/auto/STOP.

usage: auto_challenge.py [--per-hour 40] [--range 5] [--top 10] [--cycle 900]
       --unranked-only          launch no ranked series (use while an A/B candidate is live)
       --panel "TeamA,TeamB"    fixed opponent panel by leaderboard name, rotated evenly (pointer kept in
                                replays/auto/panel_state.json). Replaces the near/top-N targets. Ranked series
                                unless --unranked-only; unranked panel series rotate evenly through all
                                active maps (5 per series).
       --ignore-lock            keep running while SERVER_LOCK exists (the A/B conductor holds it)
Log: replays/auto/launched.jsonl (one line per battle launched). Download replays later with
  python3 tools/ledger.py --since <time> --download replays/auto/games
"""
import argparse
import datetime as dt
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

US = "Cache me outside"
OUT = ROOT / "replays" / "auto"
LOCK = ROOT / "codex-battlecode" / "coord" / "SERVER_LOCK"
MAP_IDS = {"Schooltime": 9, "Portals": 20, "Slithery Fight": 21, "Queen Of Spades": 7, "Default": 4,
           "Trophy": 11, "Prisoners Dilemma": 17, "Autarky": 19, "Devil": 13, "Trauma": 15}
WEAK = ["Portals", "Slithery Fight", "Autarky"]  # updated by hand from the ranked record


def now():
    return dt.datetime.now(dt.timezone.utc)


def log(msg):
    print(f"{now():%H:%M:%S} {msg}", flush=True)


def launched_last_hour():
    f = OUT / "launched.jsonl"
    if not f.exists():
        return 0
    cut = now() - dt.timedelta(hours=1)
    n = 0
    for line in f.read_text().splitlines():
        r = json.loads(line)
        if dt.datetime.fromisoformat(r["at"]) >= cut:
            n += r["games"]
    return n


def pending_opponents():
    busy = set()
    for b in api.get("/api/v1/battles?limit=100"):
        if b["outcome"] in ("queued", "live"):
            busy.add(b["opponentId"])
    return busy


def map_rotation(k):
    # 5 maps per unranked series: the weak maps plus two rotating others
    others = [m for m in MAP_IDS if m not in WEAK]
    pick = WEAK + [others[(2 * k) % len(others)], others[(2 * k + 1) % len(others)]]
    return [MAP_IDS[m] for m in pick]


def load_state():
    f = OUT / "panel_state.json"
    try:
        return json.loads(f.read_text())
    except Exception:  # noqa: BLE001
        return {"i": 0, "m": 0}


def save_state(st):
    f = OUT / "panel_state.json"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(st))
    tmp.replace(f)


def all_map_ids():
    """Ids of every active public map (for the even panel rotation); falls back to MAP_IDS."""
    try:
        ms = [m for m in api.get("/api/v1/maps") if m.get("active", True) and not m.get("private")]
        ids = sorted(m["id"] for m in ms)
        if len(ids) >= 5:
            return ids
    except Exception as e:  # noqa: BLE001
        log(f"maps list failed ({e}); using the built-in map ids")
    return sorted(MAP_IDS.values())


def resolve_panel(names, L):
    """Leaderboard teams for the panel names (case-insensitive exact match), in panel order."""
    by = {t["name"].strip().casefold(): t for t in L}
    out, missing = [], []
    for n in names:
        t = by.get(n.casefold())
        if t and t["name"] != US and t.get("hasBot", True):
            out.append(t)
        else:
            missing.append(n)
    return out, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-hour", type=int, default=40)
    ap.add_argument("--range", type=int, default=5)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--cycle", type=int, default=900)
    # ranked targets by Elo band BELOW us (user 2026-09-30: sweeps vs lower teams earn ~3x more Elo per
    # series than coin-flips vs peers); 0 = use --range ranks instead
    ap.add_argument("--band-lo", type=int, default=0, help="min Elo below us, e.g. 150")
    ap.add_argument("--band-hi", type=int, default=0, help="max Elo below us, e.g. 350")
    ap.add_argument("--unranked-only", action="store_true", help="launch no ranked series")
    ap.add_argument("--panel", default="", help="comma-separated team names: fixed opponent panel, rotated evenly")
    ap.add_argument("--ignore-lock", action="store_true", help="do not pause while SERVER_LOCK exists")
    ap.add_argument("--maps", default="", help="with --panel --unranked-only: only these map names (comma-separated)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    k = 0
    panel = [x.strip() for x in a.panel.split(",") if x.strip()]
    panel_maps = all_map_ids() if panel and a.unranked_only else []
    if panel_maps and a.maps:
        want = {x.strip().lower() for x in a.maps.split(",") if x.strip()}
        named = {m["name"].lower(): m["id"] for m in api.get("/api/v1/maps")}
        missing = want - set(named)
        if missing:
            raise SystemExit(f"unknown map names: {sorted(missing)}")
        panel_maps = sorted(named[n] for n in want)
    warned = set()
    while not (OUT / "STOP").exists():
        try:
            if LOCK.exists() and not a.ignore_lock:
                log("test version active (SERVER_LOCK) - waiting")
                time.sleep(120)
                continue
            room = a.per_hour - launched_last_hour()
            if room < 5:
                time.sleep(a.cycle)
                continue
            L = [t for t in api.get("/api/v1/leaderboard") if isinstance(t.get("rank"), int)]
            me = next(t for t in L if t["name"] == US)
            busy = pending_opponents()
            if a.band_hi > 0:
                near = [t for t in L if t["name"] != US and t.get("hasBot", True) and
                        a.band_lo <= me["elo"] - t["elo"] <= a.band_hi]
                near.sort(key=lambda t: -t["elo"])  # strongest in the band first
            else:
                near = [t for t in L if t["name"] != US and abs(t["rank"] - me["rank"]) <= a.range and t.get("hasBot", True)]
                near.sort(key=lambda t: t["rank"])  # higher-ranked first
            top = [t for t in L if t["name"] != US and t["rank"] <= a.top and t.get("hasBot", True)]
            # ranked series first (user: more ranked games vs +-RANGE), unranked vs top-N with what's left
            plan = [] if a.unranked_only else [("ranked", near[(i + k) % len(near)]) for i in range(len(near))]
            plan += [("unranked", top[(i + k) % len(top)]) for i in range(len(top))]
            st = None
            if panel:
                st = load_state()
                p0 = st["i"]
                teams, missing = resolve_panel(panel, L)
                for n in missing:
                    if n not in warned:
                        warned.add(n)
                        log(f"panel team not on the leaderboard (skipped): {n}")
                kind = "unranked" if a.unranked_only else "ranked"
                # one pass over the panel starting at the saved pointer
                plan = [(kind, teams[(p0 + i) % len(teams)], i) for i in range(len(teams))] if teams else []
            for item in plan:
                kind, t = item[0], item[1]
                if room < 5:
                    break
                if t["id"] in busy:
                    continue
                body = {"teamId": t["id"], "ranked": kind == "ranked"}
                if kind == "unranked":
                    if panel_maps:
                        body["mapIds"] = [panel_maps[(st["m"] + j) % len(panel_maps)] for j in range(5)]
                    else:
                        body["mapIds"] = map_rotation(k)
                try:
                    r = api.post("/api/v1/battles", body)
                except Exception as e:  # noqa: BLE001
                    log(f"launch failed vs {t['name']}: {e}")
                    if "429" in str(e):
                        break
                    continue
                busy.add(t["id"])
                room -= 5
                rec = {"at": now().isoformat(), "kind": kind, "team": t["name"], "teamId": t["id"],
                       "rank": t["rank"], "elo": t["elo"], "games": 5, "resp": r}
                with open(OUT / "launched.jsonl", "a") as f:
                    f.write(json.dumps(rec) + "\n")
                log(f"launched {kind} vs #{t['rank']} {t['name']} ({t['elo']})")
                if st is not None:
                    # pointer moves past the team just played; maps advance by 5 per unranked series
                    st["i"] = (p0 + item[2] + 1) % len(teams)
                    if panel_maps:
                        st["m"] = (st["m"] + 5) % len(panel_maps)
                    save_state(st)
            k += 1
        except Exception as e:  # noqa: BLE001
            log(f"cycle error: {e}")
        time.sleep(a.cycle)
    log("STOP file found - exiting")


if __name__ == "__main__":
    main()
