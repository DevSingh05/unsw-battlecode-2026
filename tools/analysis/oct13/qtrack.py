#!/usr/bin/env python3
"""qtrack.py REPLAY [TEAM]: one line per 20 rounds with each queen's head tile and length, and how each queen died.
Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/qtrack.py work/oct12/replays/t33_smoke/k8a_hive_5001_A.replay"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402

o = RS.R.load(sys.argv[1])
m = RS.Map(o["map"])
body = {i: [tuple(p) for p in pts] for i, (t, pts) in enumerate(m.dragons)}
team = {i: "AB"[t] for i, (t, pts) in enumerate(m.dragons)}
alive = set(body)
q = {team[i]: i for i in (0, 1)}
rnd = 0
line = []
for e in o["events"]:
    t = e["t"]
    if t == "roundStart":
        if rnd % 20 == 0:
            line.append(f"r{rnd}: " + "  ".join(f"{T} {body[q[T]][0]} L{len(body[q[T]])}" if q[T] in alive else f"{T} dead" for T in "AB"))
        rnd = e["round"]
    elif t == "dragonUpdate":
        b = body[e["id"]]
        h = tuple(e["head"])
        if b[0] != h:
            b.insert(0, h)
        tl = tuple(e["tail"])
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif t == "dragonSplit":
        body[e["parent"]] = [tuple(x) for x in e["parentBody"]]
        body[e["child"]] = [tuple(x) for x in e["childBody"]]
        team[e["child"]] = e["team"]
        alive.add(e["child"])
    elif t == "dragonDeath":
        alive.discard(e["id"])
        if e["id"] in (0, 1):
            line.append(f"  queen {team[e['id']]} died r{rnd} at {body[e['id']][0]} L{len(body[e['id']])}: {e['reason']}")
print(m.name, "A start", m.dragons[q["A"]][1][0], "B start", m.dragons[q["B"]][1][0])
print("\n".join(line))
