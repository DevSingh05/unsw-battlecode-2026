#!/usr/bin/env python3
"""Mechanism metrics per team from replays: eats (r<100, r<300, all), team-union map
coverage (share of tiles ever inside any own head's 7x7 view) at r50/100/200, units and
longest at r500 or end, and the result line.

usage (from project root): python3 notes/levers/frontier-explore/metrics.py REPLAY...
"""
import collections, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "notes" / "tools"))
from replay_decode import load

def run(path):
    o = load(path)
    W = H = 0; team = {}; i = 0
    for line in o["map"].splitlines():
        f = line.split()
        if not f: continue
        if f[0] == "MAP": W, H = int(f[1]), int(f[2])
        if f[0] == "DRAGON": team[i] = "AB"[int(f[1])]; i += 1
    eats = {k: [0, 0, 0] for k in "AB"}
    seen = {k: set() for k in "AB"}
    cov = {k: {} for k in "AB"}
    length = {}; alive = {k: True for k in team}
    rnd = 0; cur = None
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
            for r in (50, 100, 200):
                if rnd == r:
                    for k in "AB": cov[k][r] = len(seen[k]) / (W * H)
        elif t == "turnStart": cur = e["id"]
        elif t == "tileChange" and not e["hasPearl"] and cur is not None:
            k = team.get(cur)
            if k:
                eats[k][2] += 1
                if rnd < 300: eats[k][1] += 1
                if rnd < 100: eats[k][0] += 1
                length[cur] = length.get(cur, 0) + 1
        elif t == "dragonSplit":
            team[e["child"]] = e["team"]; alive[e["child"]] = True
        elif t == "dragonDeath": alive[e["id"]] = False
        elif t == "dragonUpdate":
            k = team.get(e["id"]); hx, hy = e["head"]
            if k:
                s = seen[k]
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        s.add(((hx + dx) % W, (hy + dy) % H))
    units = {k: sum(1 for d, a in alive.items() if a and team[d] == k) for k in "AB"}
    return o, eats, cov, units

for p in sys.argv[1:]:
    o, eats, cov, units = run(p)
    res = o["result"]
    print(pathlib.Path(p).name, "| winner", res.get("winner"), res.get("endReason"))
    for k in "AB":
        c = " ".join(f"c{r}={cov[k].get(r, float('nan')):.2f}" for r in (50, 100, 200))
        print(f"   {k} {pathlib.Path(str(o.get('bot'+k, ''))).name[-22:]:22s} longest={res.get(k, {}).get('longest')} eats<100={eats[k][0]:4d} <300={eats[k][1]:4d} all={eats[k][2]:4d} {c} units_end={units[k]}")
