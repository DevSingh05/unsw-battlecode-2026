#!/usr/bin/env python3
"""Length the team's longest dragon gives away by splitting (r300-500), Portals server replays.
Run from project root: python3 notes/portals_v31/kingsplit.py replays/ab_v30kc replays/ab_kc31"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/portals_v31'))
from sim2 import simulate
from mech import side_of
agg = {k: collections.Counter() for k in 'LW'}; n = collections.Counter(); ex = []
for d in sys.argv[1:]:
    for g in json.load(open(os.path.join(ROOT, d, 'summary.json'))):
        if g['map'] != 'Portals': continue
        G = simulate(os.path.join(ROOT, d, '%d.replay' % g['id']))
        T = side_of(G, g['us']); rs = dict(G['rounds']); key = 'W' if g['win'] else 'L'; n[key] += 1
        for tag, TT in (('us', T), ('them', 'B' if T == 'A' else 'A')):
            for s in G['splits']:
                if s['team'] != TT or s['round'] < 300: continue
                snap = rs.get(s['round'] - 1)
                if not snap or snap[TT]['king'] != s['parent']: continue
                # which part is longer afterwards: child k vs parent L-k
                kept = max(s['k'], s['L'] - s['k']); lost = s['L'] - kept
                kind = 'trapped' if not s['exits'] else 'open'
                agg[key][(tag, kind, 'n')] += 1; agg[key][(tag, kind, 'lost')] += lost
                agg[key][(tag, 'kidking', 'n')] += s['k'] > s['L'] - s['k']
                if tag == 'us' and lost >= 3: ex.append((g['id'], key, s['round'], s['L'], s['k'], s['exits']))
for key in 'LW':
    f = lambda tag, kind, x: agg[key][(tag, kind, x)] / max(1, n[key])
    print('== %s (%d) per game r300-500, us / them ==' % (key, n[key]))
    for kind in ('open', 'trapped'):
        print(' king %s splits: %.1f / %.1f, length shed %.1f / %.1f' % (kind, f('us', kind, 'n'), f('them', kind, 'n'), f('us', kind, 'lost'), f('them', kind, 'lost')))
    print(' reverse splits (child takes the body): %.1f / %.1f' % (f('us', 'kidking', 'n'), f('them', 'kidking', 'n')))
print('our king splits shedding >=3:', ex)
