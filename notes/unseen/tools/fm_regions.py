#!/usr/bin/env python3
"""How much of each map can a team reach if portals are treated as kelp (what v24 does on unknown maps)?

    python3 notes/unseen/tools/fm_regions.py [folders...]   (default: gen genhold lesson + ranked)

For each map: tiles reachable from team A's starting heads walking only (portals = walls), as a fraction of all
tiles reachable with portals; the same for the pearl rate (sum of 2/(min+max) over spawning tiles) reachable.
A low fraction means the unknown-map bot is confined to part of the map until something forces a crossing.
"""
import glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import Map

RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy", "autarky", "dilemma", "slithery_fight", "trauma"]

def reach(m, starts, portals):
    seen = set(starts); q = list(starts)
    while q:
        u = q.pop()
        for d in 'NESW':
            e = m.side_edge(u, d)
            k = m.edges.get(e, (0, -1))[0]
            if k == 1: continue
            if k == 2 and not portals: continue
            v = m.step(u, d)
            if v is None or v in seen: continue
            seen.add(v); q.append(v)
    return seen

def rate(m, tiles):
    s = 0.0
    for t in tiles:
        lo, hi = m.tiles.get(t, (0, 0))
        if hi > 0: s += 2.0 / (lo + hi)
    return s

def main():
    folders = sys.argv[1:] or ['gen', 'genhold', 'lesson', 'ranked']
    rows = []
    for f in folders:
        paths = [os.path.join(ROOT, 'maps', r + '.map') for r in RANKED] if f == 'ranked' else sorted(glob.glob(os.path.join(ROOT, 'maps', f, '*.map')))
        for p in paths:
            m = Map(open(p).read())
            starts = [tuple(pts[0]) for t, pts in m.dragons if t == 0]
            allr = reach(m, starts, True); walk = reach(m, starts, False)
            ra, rw = rate(m, allr), rate(m, walk)
            # component of each start separately (islands: each dragon on its own)
            comp = min(len(reach(m, [s], False)) for s in starts)
            npor = sum(1 for k, _ in m.edges.values() if k == 2) // 2
            rows.append((f + '/' + os.path.basename(p)[:-4], m.w * m.h, npor, len(walk) / max(1, len(allr)), rw / max(1e-9, ra), comp / max(1, len(allr))))
    print('%-26s %6s %4s %8s %8s %9s' % ('map', 'tiles', 'por', 'walkFrac', 'rateFrac', 'minStart'))
    for r in sorted(rows, key=lambda r: r[4]):
        print('%-26s %6d %4d %8.2f %8.2f %9.2f' % r)
    for f in folders:
        rs = [r for r in rows if r[0].startswith(f + '/')]
        if not rs: continue
        conf = [r for r in rs if r[4] < 0.8]
        print('%-8s maps %2d  with <80%% of pearl rate walk-reachable: %d  (%s)' % (f, len(rs), len(conf), ', '.join(r[0].split('/')[1] for r in conf)))

if __name__ == '__main__':
    main()
