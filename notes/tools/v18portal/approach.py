#!/usr/bin/env python3
"""Do teams condition their crossing on what their own ray through the portal saw?
For every ray cast from a portal mouth tile through the portal (first step of the ray crosses a portal),
P(the sender crosses that portal on its next turn), split by what the ray hit.  Also: how many turns
dragons end on a mouth tile vs cross.
usage (from project root): python3 notes/tools/v18portal/approach.py [ab_v18_Default]
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 else 'ab_v18_Default'
G = pickle.load(open(HERE / f'{name}.pkl', 'rb'))
NG = len(G)
W = H = 32
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}

for us in (True, False):
    c = collections.Counter(); tot = collections.Counter()
    for g in G:
        T = g['side'] if us else ('B' if g['side'] == 'A' else 'A')
        cross = {(r['id'], r['round'], r['ent'], r['dir']) for r in g['recs'] if r['us'] == us}
        for s, ps in g['pings'].items():
            if g['team'].get(s) != T:
                continue
            for p in ps:
                if not p['path']:
                    continue
                o = p['origin']; dx, dy = DV[p['dir']]
                plain = ((o[0] + dx) % W, (o[1] + dy) % H)
                if p['path'][0] == plain:
                    continue  # not a ray through a portal
                exit_ = p['path'][0]
                hk = p['hitKind'] or 'none'
                if hk in ('ally', 'allyHead', 'enemy', 'enemyHead'):
                    k = hk + (' AT exit' if p['end'] == exit_ else ' beyond')
                else:
                    k = 'clean'
                tot[k] += 1
                if (s, p['round'] + 1, o, p['dir']) in cross:
                    c[k] += 1
    print(f"== {'us' if us else 'them'}: rays through a portal from a mouth tile, and P(sender crosses there next turn)")
    for k in sorted(tot):
        print(f'   {k:22s} rays {tot[k] / NG:7.1f}/g   crossed next turn {100 * c[k] / tot[k]:5.1f}%')

# ---- loitering: turns ending on a mouth tile, P(cross next turn), and pre-crossing dwell near the entrance
mouth = set()
for g in G:
    for r in g['recs']:
        mouth.add(r['ent'])


def md(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


print()
for us in (True, False):
    endm = crossn = 0; dwell = collections.Counter(); nturn = 0
    for g in G:
        T = g['side'] if us else ('B' if g['side'] == 'A' else 'A')
        cross = collections.defaultdict(set)
        for r in g['recs']:
            if r['us'] == us:
                cross[r['id']].add(r['round'])
        for i, hh in g['headhist'].items():
            if g['team'].get(i) != T:
                continue
            for (rd, hd, ns) in hh:
                nturn += 1
                if hd in mouth and ns >= 0:
                    endm += 1
                    crossn += (rd + 1) in cross[i]
        for r in g['recs']:
            if r['us'] != us or len(r['move']) != 1:
                continue
            hh = g['headhist'].get(r['id'], [])
            near = sum(1 for (rd, hd, ns) in hh if r['round'] - 6 <= rd <= r['round'] - 2 and md(hd, r['ent']) <= 1)
            dwell[min(near, 3)] += 1
    tot = sum(dwell.values())
    print(f"{'us' if us else 'them'}: turns ending on a mouth tile {endm / NG:.0f}/g ({100 * endm / nturn:.1f}% of head-turns), crossed next turn {100 * crossn / max(1, endm):.0f}%;"
          f" rounds r-6..r-2 spent within 1 of the entrance before crossing: " + ', '.join(f'{k}{"+" if k == 3 else ""}: {100 * v / tot:.0f}%' for k, v in sorted(dwell.items())))
