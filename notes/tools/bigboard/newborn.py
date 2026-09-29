#!/usr/bin/env python3
"""Self-inflicted deaths by age and team unit count (notes/23).  python3 notes/tools/bigboard/newborn.py"""
import collections, os, pickle
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, 'deathctx.pkl'), 'rb'))
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']
def selfinf(c): return not (c.startswith('rammed') or c.startswith('ram_enemy') or c == 'killed_other')
UB = [(0, 30), (30, 50), (50, 60), (60, 65)]
for grp, maps in (('BIG', BIG), ('STRONG', STRONG)) + tuple((m, [m]) for m in BIG + STRONG):
    gs = [g for g in R if g['map'] in maps]; n = len(gs)
    print('== %s n=%d' % (grp, n))
    for tag in ('us', 'them'):
        si = [d for g in gs for d in g['deaths'] if d['tag'] == tag and selfinf(d['cls'])]
        age = collections.Counter('0-2' if d['age'] <= 2 else ('3-10' if d['age'] <= 10 else ('11-30' if d['age'] <= 30 else '>30')) for d in si)
        ub = collections.Counter(next(i for i, (a, b) in enumerate(UB) if a <= (d['units'] or 0) < b) for d in si)
        sp = [s for g in gs for s in g['splits'] if s['tag'] == tag]
        spu = collections.Counter(next(i for i, (a, b) in enumerate(UB) if a <= (s['units'] or 0) < b) for s in sp)
        print('  %-4s selfinf/g %6.1f age %s | by units %s | splits by units %s' % (
            tag, len(si) / n, {k: round(age[k] / n, 1) for k in ('0-2', '3-10', '11-30', '>30')},
            {'%d-%d' % UB[i]: round(ub[i] / n, 1) for i in range(4)}, {'%d-%d' % UB[i]: round(spu[i] / n, 1) for i in range(4)}))
