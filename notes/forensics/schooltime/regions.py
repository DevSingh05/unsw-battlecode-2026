#!/usr/bin/env python3
"""Where heads are and where spawn pearls are eaten, per region and phase, us vs them.
    python3 notes/forensics/schooltime/regions.py [A|B]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
LAY = sys.argv[1] if len(sys.argv) > 1 else 'B'
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def reg(t):
    x, y = t
    if 22 <= x <= 37 and y >= 24: return 'yard'
    if y <= 7: return 'top'
    if y <= 21: return 'maze'
    return 'low'
RG = ['top', 'maze', 'low', 'yard']
for res in (False, True):
    Ds = [D for D in G.values() if lay(D) == LAY and D['win'] == res]; n = len(Ds)
    print('=== layout %s %s n=%d' % (LAY, 'W' if res else 'L', n))
    print(' heads per region at r (us | them):')
    for r in (25, 50, 75, 100, 150, 200, 300):
        cu = collections.Counter(); ct = collections.Counter()
        for D in Ds:
            ks = [k for k in D['tl'] if k <= r]; hs = D['tl'][max(ks)]['heads']
            for j, (h, L, T) in hs.items():
                (cu if T == D['us'] else ct)[reg(h)] += 1
        print('  r%3d  ' % r + '  '.join('%s %4.1f|%4.1f' % (g, cu[g] / n, ct[g] / n) for g in RG))
    print(' spawn eats per region (us | them):')
    for a, b in ((0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 500)):
        cu = collections.Counter(); ct = collections.Counter()
        for D in Ds:
            for e in D['eats']:
                if e['corpse'] is None and a <= e['round'] < b:
                    (cu if e['team'] == D['us'] else ct)[reg(e['tile'])] += 1
        print('  r%3d-%3d ' % (a, b) + '  '.join('%s %4.1f|%4.1f' % (g, cu[g] / n, ct[g] / n) for g in RG))
