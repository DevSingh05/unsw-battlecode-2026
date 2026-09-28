#!/usr/bin/env python3
"""Split children that die on their birth turn by stepping back through a portal into their own neck
(the neck is across the portal, out of the child's 7x7 view, so a fresh process thinks the tile is free).
    python3 notes/tools/v16diag/newborn_portal.py replays/v16
"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'midgame')); sys.path.insert(0, os.path.join(HERE, '..'))
from sim2 import simulate
d0 = sys.argv[1]
led = json.load(open(os.path.join(d0, 'ledger.json')))
per = collections.defaultdict(lambda: [0, 0, 0, 0])  # map -> games, ours, theirs, our straddling births
for g in led:
    p = os.path.join(d0, '%d.replay' % g['game'])
    if not os.path.exists(p): continue
    G = simulate(p); m = G['map']; us = g['side']
    per[g['map']][0] += 1
    for d in G['deaths']:
        if d['reason'] != 'HitSelf' or not d.get('move') or d['age'] != 0: continue
        k = d.get('step_failed', 1) - 1; s = d['move'][k]
        if m.edges.get(m.side_edge(d['head'], s), (0, -1))[0] != 2: continue
        if len(d['body']) > 1 and m.step(d['head'], s) == d['body'][1]:
            per[g['map']][1 if d['team'] == us else 2] += 1
for mp, (n, a, b, _) in sorted(per.items()):
    print('%-18s games %2d  our newborn portal-neck deaths %.1f/game  theirs %.1f/game' % (mp, n, a / n, b / n))
