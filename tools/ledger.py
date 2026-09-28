#!/usr/bin/env python3
"""Per-map / per-kind record of every game we've played since a given time, with replays cached.

usage: ledger.py [--since 2026-09-27T06:40] [--download DIR]
"""
import argparse
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import api  # noqa: E402

US = "Cache me outside"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="")
    ap.add_argument("--download", default="")
    a = ap.parse_args()
    if a.download:
        pathlib.Path(a.download).mkdir(parents=True, exist_ok=True)
    rows = []
    for b in api.get("/api/v1/battles?limit=200"):
        if b["at"] < a.since or b["outcome"] in ("queued", "live"):
            continue
        d = api.get(f"/api/v1/battles/{b['id']}")
        us_a = d["teamAName"] == US
        for g in d["games"]:
            if g["status"] != "completed":
                continue
            won = (g["winner"] == "a") == us_a if g["winner"] else None
            rows.append({"game": g["id"], "battle": b["id"], "ranked": b["ranked"], "opp": b["opponent"],
                         "oppElo": b["opponentElo"], "map": g["mapName"], "win": won, "side": "A" if us_a else "B",
                         "at": b["at"]})
            if a.download:
                p = pathlib.Path(a.download) / f"{g['id']}.replay"
                if not p.exists():
                    try:
                        api.download_replay(g["id"], p)
                    except Exception as e:  # noqa: BLE001
                        print("replay fail", g["id"], e)
    pathlib.Path(a.download or ".").mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(a.download or ".") / "ledger.json"
    out.write_text(json.dumps(rows, indent=1))
    for kind in (True, False):
        by = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            if r["ranked"] == kind:
                by[r["map"]][0] += bool(r["win"])
                by[r["map"]][1] += 1
        tot = [sum(v[0] for v in by.values()), sum(v[1] for v in by.values())]
        print("RANKED" if kind else "UNRANKED", f"{tot[0]}/{tot[1]}")
        for k, v in sorted(by.items(), key=lambda x: x[1][0] / x[1][1]):
            print(f"   {k:18s} {v[0]}/{v[1]}")


if __name__ == "__main__":
    main()
