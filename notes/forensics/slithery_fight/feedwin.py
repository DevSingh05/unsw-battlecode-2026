#!/usr/bin/env python3
"""Feed deaths (backward-into-neck, plus NoValidAction for the opponent) per 50-round window r200-500 and the
pearls from them eaten by the final-king lineage vs anyone else.   python3 .../feedwin.py [GAME...]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
gids = [int(a) for a in sys.argv[1:]] or sorted(g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and not g['win'] and (g['opp'] in top or g['opp'] == '3.14159265'))
A = {'us': collections.Counter(), 'them': collections.Counter()}
for gid in gids:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = S['map']
    last = S['rounds'][-1][1]
    for T, lab in ((us, 'us'), (th, 'them')):
        if not last[T]['n']: continue
        k = last[T]['king']; chain = {k}; cur = k
        while True:
            sp = [s for s in S['splits'] if s['child'] == cur]
            if not sp or sp[0]['k'] < sp[0]['L'] - sp[0]['k']: break
            cur = sp[0]['parent']; chain.add(cur)
        feed = {}
        for d in S['deaths']:
            if d['team'] != T or d['round'] < 200: continue
            b = d['body']
            if (d['reason'] == 'HitSelf' and d.get('move') and len(b) > 1 and d.get('steps', 1) == 1 and m.step(b[0], d['move'][0]) == b[1]) or d['reason'] == 'NoValidAction':
                feed[d['id']] = d
                w = min((d['round'] - 200) // 50, 5)
                A[lab][(w, 'n')] += 1; A[lab][(w, 'len')] += d['len']
        for e in S['eats']:
            if e['corpse'] and e['corpse'][0] in feed:
                w = min((feed[e['corpse'][0]]['round'] - 200) // 50, 5)
                A[lab][(w, 'king' if e['id'] in chain else 'other')] += 1
n = len(gids)
for lab in ('us', 'them'):
    print(lab + ' feed deaths per game / length / pearls->final king / pearls->others, per window:')
    for w in range(6):
        c = A[lab]
        print('   r%d-%d: %5.1f  %6.1f  %5.1f  %5.1f' % (200 + 50 * w, 250 + 50 * w, c[(w, 'n')] / n, c[(w, 'len')] / n, c[(w, 'king')] / n, c[(w, 'other')] / n))
