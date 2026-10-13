#!/usr/bin/env python3
"""by_build.py [--ranked|--unranked] [--maps "A,B"] [--opp NAME]: record per build and map from the cached series.

Reads work/oct12/watch/*.json (written by build_watch.py) and the submissions list (GET) for upload times.
A game belongs to the build that was uploaded last before the series started. Cell = W-L (win% minus Elo-expected%).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/by_build.py --ranked"""
import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "analysis" / "oct12"))
import api  # noqa: E402
from build_watch import rows_of, W  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranked", action="store_true")
    ap.add_argument("--unranked", action="store_true")
    ap.add_argument("--maps", default="")
    ap.add_argument("--opp", default="")
    ap.add_argument("--builds", default="km4,km5,km6")
    ap.add_argument("--min-opp", type=int, default=0)
    a = ap.parse_args()
    subs = sorted((s["uploadedAt"][:19], s["name"]) for s in api.get("/api/v1/submissions") if s["name"].startswith(("km", "qf1")))
    rows = []
    for p in W.glob("*.json"):
        rows += rows_of(json.loads(p.read_text()))
    want = [x.strip() for x in a.maps.split(",") if x.strip()]
    builds = a.builds.split(",")
    T = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        if a.ranked and not r["ranked"] or a.unranked and r["ranked"]:
            continue
        if a.opp and r["opp"] != a.opp or r["opp_elo"] < a.min_opp:
            continue
        b = [n for t, n in subs if t <= r["at"][:19]]
        if not b or b[-1] not in builds:
            continue
        e = 1 / (1 + 10 ** ((r["opp_elo"] - r["our_elo"]) / 400))
        for key in ((b[-1], r["map"]), (b[-1], "ALL")):
            T[key][0] += 1
            T[key][1] += r["win"]
            T[key][2] += e
    maps = sorted({m for _, m in T if m != "ALL"}) + ["ALL"]
    print("| map | " + " | ".join(builds) + " |")
    print("|---|" + "---|" * len(builds))
    for m in maps:
        if want and m not in want and m != "ALL":
            continue
        cells = []
        for b in builds:
            n, w, e = T.get((b, m), (0, 0, 0.0))
            cells.append(f"{w}-{n - w} ({100 * (w - e) / n:+.0f})" if n else "-")
        print(f"| {m} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
