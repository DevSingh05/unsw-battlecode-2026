#!/usr/bin/env python3
"""Where each side eats (tile histogram, mirrored into OUR frame = we start left).  eattiles.py MAP R0 R1"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
REF = {'Devil': 'notes/maps/Devil__id13.map', 'Prisoners Dilemma': 'notes/maps/Prisoners_Dilemma__id17.map'}
for W in (False, True):
    H = {'us': collections.Counter(), 'them': collections.Counter()}; n = 0
    for g in GS:
        if not g['map'].startswith(M) or g['win'] != W: continue
        n += 1
        S = simulate(g['path']); ref = Map(open(os.path.join(ROOT, REF[g['map']])).read())
        for e in S['eats']:
            if not (r0 <= e['round'] < r1): continue
            who = 'us' if e['team'] == g['us'] else 'them'
            x, y = e['tile']
            # normalise so that the eating team's own start is on the left
            left = g['we_left'] if who == 'us' else not g['we_left']
            if not left: x = S['map'].w - 1 - x
            if g['map'].startswith('Pris') and not left: y = S['map'].h - 1 - y  # PD is 180-rotation symmetric
            H[who][(x, y)] += 1
    print('==', 'WINS' if W else 'LOSSES', n, 'games, eats per game in r%d-%d, tile in own frame (own start on the left)' % (r0, r1))
    for who in ('us', 'them'):
        print(' ', who, 'total %.1f' % (sum(H[who].values()) / n), ' top:', ', '.join('%s %.1f' % (t, c / n) for t, c in H[who].most_common(14)))
        # by x band
        band = collections.Counter()
        for (x, y), c in H[who].items(): band[x // 4] += c
        print('    by x/4 band:', ' '.join('%d-%d:%.1f' % (b * 4, b * 4 + 3, band[b] / n) for b in range(8)))
