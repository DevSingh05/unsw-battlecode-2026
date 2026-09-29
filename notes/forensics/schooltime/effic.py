#!/usr/bin/env python3
"""Dragon-rounds and spawn eats per 100 dragon-rounds by region and phase (us | them).
    python3 notes/forensics/schooltime/effic.py LAYOUT W|L"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
LAY = sys.argv[1]; RES = sys.argv[2]
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def reg(t):
    x, y = t
    if 22 <= x <= 37 and y >= 24: return 'yard'
    if y <= 7: return 'top'
    if y <= 21: return 'maze'
    return 'low'
RG = ['top', 'maze', 'low', 'yard']
Ds = [D for D in G.values() if lay(D) == LAY and D['win'] == (RES == 'W')]; n = len(Ds)
for a, b in ((0, 100), (100, 200), (200, 300), (300, 400)):
    dr = {s: collections.Counter() for s in ('us', 'them')}; ea = {s: collections.Counter() for s in ('us', 'them')}
    for D in Ds:
        for r in range(a, b):
            if r not in D['tl']: continue
            for j, (h, L, T) in D['tl'][r]['heads'].items():
                dr['us' if T == D['us'] else 'them'][reg(h)] += 1
        for e in D['eats']:
            if a <= e['round'] < b and e['corpse'] is None:
                ea['us' if e['team'] == D['us'] else 'them'][reg(e['tile'])] += 1
    print('r%d-%d' % (a, b), '  '.join('%s dr %5.0f|%5.0f eff %4.1f|%4.1f' % (g, dr['us'][g] / n, dr['them'][g] / n,
          100 * ea['us'][g] / max(1, dr['us'][g]), 100 * ea['them'][g] / max(1, dr['them'][g])) for g in RG))
