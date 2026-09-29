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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-hour", type=int, default=40)
    ap.add_argument("--range", type=int, default=5)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--cycle", type=int, default=900)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    k = 0
    while not (OUT / "STOP").exists():
        try:
            if LOCK.exists():
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
            near = [t for t in L if t["name"] != US and abs(t["rank"] - me["rank"]) <= a.range and t.get("hasBot", True)]
            near.sort(key=lambda t: t["rank"])  # higher-ranked first
            top = [t for t in L if t["name"] != US and t["rank"] <= a.top and t.get("hasBot", True)]
            # ranked series first (user: more ranked games vs +-RANGE), unranked vs top-N with what's left
            plan = [("ranked", near[(i + k) % len(near)]) for i in range(len(near))]
            plan += [("unranked", top[(i + k) % len(top)]) for i in range(len(top))]
            for kind, t in plan:
                if room < 5:
                    break
                if t["id"] in busy:
                    continue
                body = {"teamId": t["id"], "ranked": kind == "ranked"}
                if kind == "unranked":
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
            k += 1
        except Exception as e:  # noqa: BLE001
            log(f"cycle error: {e}")
        time.sleep(a.cycle)
    log("STOP file found - exiting")


if __name__ == "__main__":
    main()
