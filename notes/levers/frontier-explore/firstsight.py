#!/usr/bin/env python3
"""Per-dragon first-sight pearl rate vs global pearl density, from replays.

usage (from project root): python3 notes/levers/frontier-explore/firstsight.py REPLAY...
For every dragon, a tile is 'first seen' the first turn it enters that dragon's 7x7 view
(children start with empty memory, like the bot). We record whether a pearl lay there.
Printed per 100-round bucket: first-sight pearl fraction (the empirical P(pearl | never seen
by me)), global density of pearls over all tiles, and v28's unseen prior 0.5*min(1,0.001*r).
"""
import collections, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "notes" / "tools"))
from replay_decode import load

def run(path, agg):
    o = load(path)
    W = H = 0
    team = {}
    i = 0
    for line in o["map"].splitlines():
        f = line.split()
        if not f: continue
        if f[0] == "MAP": W, H = int(f[1]), int(f[2])
        if f[0] == "DRAGON": team[i] = "AB"[int(f[1])]; i += 1
    pearl = set()
    seen = collections.defaultdict(set)
    rnd = 0
    cur = None
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
            b = rnd // 100
            agg["dens"][b] += len(pearl) / (W * H); agg["densn"][b] += 1
        elif t == "tileChange":
            if e["hasPearl"]: pearl.add(tuple(e["tile"]))
            else: pearl.discard(tuple(e["tile"]))
        elif t == "dragonSplit":
            team[e["child"]] = e["team"]
        elif t == "turnStart":
            cur = e["id"]
        elif t == "dragonUpdate":
            # view at start of the NEXT turn is around this head; approximate with it now
            hx, hy = e["head"]
            s = seen[e["id"]]
            b = rnd // 100
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    p = ((hx + dx) % W, (hy + dy) % H)
                    if p not in s:
                        s.add(p)
                        if len(s) > 49:  # skip the birth view (counted separately)
                            agg["fs"][b] += p in pearl; agg["fsn"][b] += 1

agg = {k: collections.Counter() for k in ("fs", "fsn", "dens", "densn")}
for p in sys.argv[1:]:
    try: run(p, agg)
    except Exception as ex: print("skip", p, ex)
print("bucket  firstSightPearl  samples  globalDensity  v28prior(mid)")
for b in range(5):
    if agg["fsn"][b]:
        print(f"r{b*100:3d}-{b*100+99:3d}  {agg['fs'][b]/agg['fsn'][b]:.4f}  {agg['fsn'][b]:8d}  {agg['dens'][b]/max(1,agg['densn'][b]):.4f}  {0.5*min(1,0.001*(b*100+50)):.3f}")
