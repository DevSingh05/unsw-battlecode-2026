#!/usr/bin/env python3
"""Trauma: follow our two starters + our longest dragon; A-frame coords. usage: tra_king.py GAME [side]"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'midgame')); sys.path.insert(0, os.path.join(HERE, '..'))
from sim2 import simulate
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
gid = int(sys.argv[1])
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json')))}
us = led[gid]['side'] if gid in led else sys.argv[2]
G = simulate(os.path.join(ROOT, 'replays/v16/%d.replay' % gid))
A = (lambda p: p) if us == 'A' else (lambda p: (47 - p[0], 23 - p[1]))
starters = [i for i, (t, pts) in enumerate(G['map'].dragons) if 'AB'[t] == us]
print('us', us, 'starters', starters, [A(G['map'].dragons[i][1][0]) for i in starters])
for s in G['splits']:
    if s['parent'] in starters and s['round'] < 60 and s['team'] == us:
        print('  split r%d parent %d L%d k%d exits %d child %d' % (s['round'], s['parent'], s['L'], s['k'], s['exits'], s['child']))
for d in G['deaths']:
    if d['id'] in starters: print('  starter death', d['round'], d['id'], d['len'], d['reason'], A(d['head']))
snap = dict(G['rounds'])
for r in list(range(0, 60, 5)) + list(range(60, 500, 25)):
    if r not in snap: continue
    s = snap[r]
    ids = s[us]['ids']
    st = ' '.join('%d:%s@%s' % (i, ids.get(i, '-'), A(s['heads'][i][0]) if i in s['heads'] else '') for i in starters)
    k = s[us]['king']
    print('r%3d n%2d max%2d king %s L%d @%s | starters %s' % (r, s[us]['n'], s[us]['max'], k, s[us]['max'], A(s['heads'][k][0]) if k is not None else '', st))
