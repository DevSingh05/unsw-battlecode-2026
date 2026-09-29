#!/usr/bin/env python3
"""Per game: round our/their longest first reaches 8/12/20, units at r400, king resets; sorted by result.
   python3 notes/forensics/portals/timing.py"""
import json, os, sys, collections, pickle
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
rows = []
for gid in games:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(GD, '%d.replay' % gid)); R = dict(S['rounds'])
    def first(T, L):
        for r in sorted(R):
            if R[r][T]['max'] >= L: return r
        return 999
    rows.append(dict(game=gid, opp=g['opp'], win=g['win'], us=[first(us, L) for L in (8, 12, 20)], th=[first(th, L) for L in (8, 12, 20)],
                     u400=(R[400][us]['n'], R[400][th]['n']), m400=(R[400][us]['total'], R[400][th]['total']), fin=(R[max(R)][us]['max'], R[max(R)][th]['max'])))
pickle.dump(rows, open(os.path.join(os.path.dirname(__file__), 'timing.pkl'), 'wb'))
for w in (False, True):
    rs = [r for r in rows if r['win'] == w]
    print('==', 'WINS' if w else 'LOSSES', len(rs))
    for r in sorted(rs, key=lambda r: r['us'][1]):
        print('%d %-16s us L8/12/20 @r%s  them @r%s  units400 %d/%d mass400 %d/%d final %d v %d' % (r['game'], r['opp'][:16], r['us'], r['th'], *r['u400'], *r['m400'], *r['fin']))
    import statistics as st
    for k in (0, 1, 2):
        print('  median reach L%d: us r%d them r%d' % ((8, 12, 20)[k], st.median(r['us'][k] for r in rs), st.median(r['th'][k] for r in rs)))
