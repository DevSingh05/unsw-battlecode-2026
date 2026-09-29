#!/usr/bin/env python3
"""Per-team mechanism stats for local replays: eats, portal crossings, deaths right after a
crossing, deaths, final longest/total, and sealed-food LOG lines.

usage (from project root): python3 notes/levers/blocked-food/stats.py notes/levers/blocked-food/replays/*.replay
"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes/tools/midgame"))
sys.path.insert(0, str(ROOT / "notes/tools"))
from sim2 import simulate  # noqa: E402

for p in sys.argv[1:]:
    g = simulate(p)
    m = g["map"]
    st = {T: collections.Counter() for T in "AB"}
    for e in g["eats"]:
        if e["team"] in st:
            st[e["team"]]["eats"] += 1
    for a in g["moves"]:
        mv = a["act"].get("move") if isinstance(a["act"], dict) else None
        if not mv:
            continue
        pos = a["head"]
        crossed = False
        for d in mv:
            e = m.side_edge(pos, d)
            if m.edges.get(e, (0, -1))[0] == 2:
                crossed = True
            nxt = m.step(pos, d)
            if nxt is None:
                break
            pos = nxt
        if crossed:
            st[a["team"]]["cross"] += 1
            if a.get("died"):
                st[a["team"]]["crossdeath"] += 1
    for d in g["deaths"]:
        st[d.get("team", "?")]["deaths"] += 1 if d.get("team") in st else 0
    last = g["rounds"][-1][1] if g["rounds"] else {}
    res = g["result"]
    print(pathlib.Path(p).name, "result", res if not isinstance(res, dict) else {k: v for k, v in res.items() if k in ("winner", "reason", "round")}, "rounds", g["last_round"])
    for T in "AB":
        s = st[T]
        r = last.get(T, {})
        print(f"  {T}: eats {s['eats']:4d} cross {s['cross']:4d} crossdeath {s['crossdeath']:3d} deaths {s['deaths']:4d} "
              f"units {r.get('n', 0):3d} max {r.get('max', 0):3d} total {r.get('total', 0):4d}")
