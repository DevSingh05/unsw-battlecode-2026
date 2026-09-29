#!/usr/bin/env python3
"""Devil center control: per game, heads (and body tiles) of each side inside x 12..19 every 10 rounds,
and center eats per 20-round window.  python3 notes/tools/devdil/center.py [MAP] [x0 x1]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1] if len(sys.argv) > 1 else 'Devil'
x0, x1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (12, 19)
for g in sorted([g for g in GS if g['map'].startswith(M)], key=lambda g: (g['win'], g['game'])):
    S = simulate(g['path']); us = g['us']
    snaps = dict(S['rounds'])
    row = []
    for r in (5, 10, 15, 20, 25, 30, 40, 50, 60, 80):
        s = snaps.get(r)
        if not s: row.append('  -  '); continue
        c = collections.Counter()
        for j, (h, L, T) in s['heads'].items():
            if x0 <= h[0] <= x1: c['us' if T == us else 'them'] += 1
        row.append('%2d/%-2d' % (c['us'], c['them']))
    ce = collections.Counter()
    for e in S['eats']:
        if e['round'] < 60 and x0 <= e['tile'][0] <= x1: ce['us' if e['team'] == us else 'them'] += 1
    print('%d %s %-22s heads in x%d-%d @5..80: %s | center eats r<60 %d/%d' % (g['game'], 'W' if g['win'] else 'L', g['opp'][:22], x0, x1, ' '.join(row), ce['us'], ce['them']))
