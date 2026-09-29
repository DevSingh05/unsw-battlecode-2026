#!/usr/bin/env python3
"""For feed deaths (backward-into-neck or NoValidAction) r300-500 whose corpse the final king ate: dead length,
Manhattan distance to the king head at death and 10/20 rounds earlier (did the feeder travel toward it?),
and the dead dragon's age.  Both teams.   python3 .../approach.py GAME..."""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
for gid in map(int, sys.argv[1:]):
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = S['map']; snap = dict(S['rounds'])
    last = S['rounds'][-1][1]
    for T, lab in ((us, 'us'), (th, 'them')):
        k = last[T]['king']; chain = {k}; cur = k
        while True:
            sp = [s for s in S['splits'] if s['child'] == cur]
            if not sp or sp[0]['k'] < sp[0]['L'] - sp[0]['k']: break
            cur = sp[0]['parent']; chain.add(cur)
        ate = collections.Counter(e['corpse'][0] for e in S['eats'] if e['corpse'] and e['id'] in chain)
        rows = []
        for d in S['deaths']:
            if d['team'] != T or d['round'] < 300 or d['id'] not in ate: continue
            b = d['body']
            if not ((d['reason'] == 'HitSelf' and d.get('move') and len(b) > 1 and m.step(b[0], d['move'][0]) == b[1]) or d['reason'] == 'NoValidAction'): continue
            def kd(r):
                s = snap.get(r)
                if not s or d['id'] not in s['heads']: return None
                kh = [s['heads'][j][0] for j in chain if j in s['heads']]
                return abs(s['heads'][d['id']][0][0] - kh[0][0]) + abs(s['heads'][d['id']][0][1] - kh[0][1]) if kh else None
            rows.append((d['round'], d['len'], d['age'], kd(d['round'] - 1), kd(d['round'] - 10), kd(d['round'] - 20), ate[d['id']], d['reason'][:6]))
        print(gid, lab, len(rows), 'feeds that reached the king: (round, len, age, dist@-1, dist@-10, dist@-20, pearls eaten, how)')
        for r in rows[:40]: print('   ', r)
