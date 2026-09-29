#!/usr/bin/env python3
"""Our own-move deaths (HitSelf / ally body) by length, free neighbours at death, region, round phase.
    python3 notes/forensics/schooltime/selfdeaths.py LAYOUT [W|L]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
LAY = sys.argv[1]; RES = sys.argv[2] if len(sys.argv) > 2 else 'L'
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def reg(t):
    x, y = t
    if 22 <= x <= 37 and y >= 24: return 'yard'
    if y <= 7: return 'top'
    if y <= 21: return 'maze'
    return 'low'
Ds = [D for D in G.values() if lay(D) == LAY and D['win'] == (RES == 'W')]; n = len(Ds)
for side in ('us', 'them'):
    c = collections.Counter()
    for D in Ds:
        T = D[side]
        for d in D['deaths']:
            if d['team'] != T or d['actor'] != d['id'] or d['reason'] == 'HitHeadToHead': continue
            if d['round'] >= 300: continue
            nb = d.get('nbrs', {})
            free = sum(1 for v in nb.values() if v in ('free', 'pearl'))
            pearl = sum(1 for v in nb.values() if v == 'pearl')
            c[('free%d' % min(free, 2), 'L2' if d['len'] <= 2 else 'L3' if d['len'] == 3 else 'L4+')] += 1
            c['reg_' + reg(d['head'])] += 1
            c['age<=3' if d['age'] <= 3 else 'age>3'] += 1
            c['total'] += 1
    print(side, 'n=%d r<300 own-move deaths/g %.1f' % (n, c['total'] / n))
    print('   ', ' '.join('%s %.1f' % (k, v / n) for k, v in sorted(c.items(), key=str) if k != 'total'))
