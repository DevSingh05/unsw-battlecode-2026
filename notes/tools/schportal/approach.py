#!/usr/bin/env python3
"""Schooltime version of v18portal/approach.py (notes/20): do teams condition crossing on what their own
ray through the portal saw; how often dragons end a turn on a mouth tile; re-cross (ping-pong) rate;
safe alternatives at crossing time; crossings per portal id.
usage (from project root): python3 notes/tools/schportal/approach.py [ab_v22_Schooltime]
"""
import collections
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import load, fatal, DV  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 else 'ab_v22_Schooltime'
G, m = load(name)
NG = len(G)

for us in (True, False):
    c = collections.Counter(); tot = collections.Counter()
    for g in G:
        T = g['side'] if us else ('B' if g['side'] == 'A' else 'A')
        cross = {(r['id'], r['round'], r['ent'], r['dir']) for r in g['recs'] if r['us'] == us}
        for s, ps in g['pings'].items():
            if g['team'].get(s) != T:
                continue
            for p in ps:
                if not p['thru']:
                    continue
                exit_ = p['path'][0]
                hk = p['hitKind'] or 'none'
                if hk in ('ally', 'allyHead', 'enemy', 'enemyHead'):
                    k = hk + (' AT exit' if p['end'] == exit_ else ' beyond')
                else:
                    k = 'clean'
                tot[k] += 1
                if (s, p['round'] + 1, p['origin'], p['dir']) in cross:
                    c[k] += 1
    print(f"== {'us' if us else 'them'}: rays through a portal, and P(sender crosses there next turn)")
    for k in sorted(tot):
        print(f'   {k:22s} rays {tot[k] / NG:7.1f}/g   crossed next turn {100 * c[k] / tot[k]:5.1f}%')

mouth = set()
for g in G:
    for r in g['recs']:
        mouth.add(r['ent'])

print()
for us in (True, False):
    endm = crossn = 0; nturn = 0; rc = collections.Counter(); alts = collections.Counter(); pid = collections.Counter()
    for g in G:
        T = g['side'] if us else ('B' if g['side'] == 'A' else 'A')
        cross = collections.defaultdict(set)
        seq = collections.defaultdict(list)
        for r in g['recs']:
            if r['us'] == us:
                cross[r['id']].add(r['round'])
                seq[r['id']].append(r['round'])
                a = sum(1 for d, x in r['alts'].items() if d != r['dir'] and x['st'] == 'free')
                alts[min(a, 3)] += 1
                pid[r['pid']] += 1
        for i, rr in seq.items():
            for a, b in zip(rr, rr[1:]):
                rc['back<=2' if b - a <= 2 else 'back<=4' if b - a <= 4 else 'later'] += 1
        for i, hh in g['headhist'].items():
            if g['team'].get(i) != T:
                continue
            for (rd, hd, ns) in hh:
                nturn += 1
                if hd in mouth and ns >= 0:
                    endm += 1
                    crossn += (rd + 1) in cross[i]
    n = sum(alts.values())
    print(f"{'us' if us else 'them'}: head-turns ending on a mouth tile {endm / NG:.0f}/g ({100 * endm / nturn:.1f}%), crossed next turn {100 * crossn / max(1, endm):.0f}%;"
          f" re-cross gap: " + ', '.join(f'{k} {100 * v / max(1, sum(rc.values())):.0f}%' for k, v in sorted(rc.items())))
    print('   safe alternatives at crossing: ' + ', '.join(f'{k}{"+" if k == 3 else ""}: {100 * v / n:.0f}%' for k, v in sorted(alts.items())))
    print('   crossings/g by portal id: ' + ', '.join(f'{k}: {v / NG:.0f}' for k, v in sorted(pid.items())))
