#!/usr/bin/env python3
"""Ally heads within Manhattan 3 of a declared king's head: at crown drops (split while king) vs at all king turns.
   python3 notes/forensics/portals/crowd.py"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
from crownwhere import cls
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
H = collections.defaultdict(collections.Counter)
for gid in games:
    g = led[gid]; T = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid)); m = S['map']; R = dict(S['rounds'])
    kr = collections.defaultdict(set)
    for s in S['sonars']:
        if s['team'] != T: continue
        x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
        if hop == 0 and kid == (s['id'] & 1023) and L >= 2: kr[s['id']].add(s['round'])
    drops = {(s['round'], s['parent']) for s in S['splits'] if s['team'] == T}
    for r, snap in S['rounds']:
        if r < 250: continue
        heads = snap['heads']
        for i in kr:
            if r not in kr[i] or i not in heads: continue
            h = heads[i][0]
            if cls(h) != 'main': continue
            near = sum(1 for j, (hj, Lj, Tj) in heads.items() if j != i and Tj == T and m.dist(h, hj) <= 3)
            key = 'drop_next_round' if (r + 1, i) in drops else 'king_turn'
            H[key][min(near, 5)] += 1
for k, c in H.items():
    n = sum(c.values()); mean = sum(a * b for a, b in c.items()) / n
    print('%-16s n=%5d mean ally heads within 3: %.2f  dist %s' % (k, n, mean, {a: '%.0f%%' % (100 * b / n) for a, b in sorted(c.items())}))
