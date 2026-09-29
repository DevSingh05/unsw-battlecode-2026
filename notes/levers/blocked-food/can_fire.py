#!/usr/bin/env python3
"""Static check: on which maps can UNK_SEALED_FOOD's evidence rule ever fire?

For each team's spawn heads, BFS the portal-free component (portals = kelp, full map knowledge,
i.e. the most evidence a dragon could ever collect from that region). Report the sealed spawner
count, the sealed share of the spawn rate and the per-tile richness ratio, and whether the
default thresholds (MIN 4, FRAC 0.2, RICH 1.0) pass. On maps where it cannot pass, the flag
leaves v28 behaviour unchanged except inside rooms < 32 tiles (split guard / crowd exit).

usage (from project root): python3 notes/levers/blocked-food/can_fire.py maps/*.map maps/gen/*.map ...
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tools"))
from genmaps import parse  # noqa: E402

MIN, FRAC, RICH, ROOM = 4, 0.2, 1.0, 32
fire_maps = 0
rows = []
for p in sys.argv[1:]:
    m = parse(pathlib.Path(p))
    W, H, nxt = m["w"], m["h"], m["nxt"]
    N = W * H

    def plain(t, d):
        x, y = t % W, t // W
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][d]
        return ((y + dy) % H) * W + (x + dx) % W

    def walk(t, d):
        v = nxt[t * 4 + d]
        return v if v == plain(t, d) else -1  # portal or kelp -> blocked

    has_portal = any(nxt[t * 4 + d] not in (-1, plain(t, d)) for t in range(N) for d in range(4))
    rate = [2.0 / (m["gmin"][t] + m["gmax"][t]) if m["gmax"][t] > 0 else 0 for t in range(N)]
    # all portal-free components; for each component that holds a spawn head, evaluate
    comp = [-1] * N
    sizes = []
    for s in range(N):
        if comp[s] >= 0:
            continue
        cid = len(sizes)
        comp[s] = cid
        q = [s]
        for u in q:
            for d in range(4):
                v = walk(u, d)
                if v >= 0 and comp[v] < 0:
                    comp[v] = cid
                    q.append(v)
        sizes.append(len(q))
    small_rooms = sum(1 for c in sizes if c < ROOM and any(rate[t] > 0 for t in range(N) if comp[t] == sizes.index(c))) if False else sum(1 for c in sizes if c < ROOM)
    heads = []
    for team, pts in m["dragons"]:
        x, y = pts[0]
        heads.append(y * W + x)
    best = None
    for h in heads:
        c = comp[h]
        sN = sum(1 for t in range(N) if rate[t] > 0 and comp[t] != c)
        rN = sum(1 for t in range(N) if rate[t] > 0 and comp[t] == c)
        sR = sum(rate[t] for t in range(N) if comp[t] != c)
        rR = sum(rate[t] for t in range(N) if comp[t] == c)
        frac = sR / (sR + rR) if sR + rR > 0 else 0
        rich = (sR / max(1, sN)) / (rR / max(1, rN)) if rR > 0 and sN > 0 else (99 if sN else 0)
        ok = has_portal and sN >= MIN and frac >= FRAC and rich >= RICH
        cand = (ok, sN, frac, rich)
        if best is None or cand > best:
            best = cand
    ok, sN, frac, rich = best
    fire_maps += ok
    rows.append((pathlib.Path(p).stem, has_portal, sN, frac, rich, ok, small_rooms))
print(f"{'map':22s} portals sealedSpawners rateShare richness FIRES smallRooms(<{ROOM})")
for r in rows:
    print(f"{r[0]:22s} {str(r[1]):7s} {r[2]:14d} {r[3]:9.2f} {r[4]:8.2f} {'YES' if r[5] else '-':5s} {r[6]}")
print(f"can fire on {fire_maps}/{len(rows)} maps")
