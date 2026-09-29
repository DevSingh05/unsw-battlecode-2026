#!/usr/bin/env python3
"""What blocks our self-inflicted deaths (notes/23).  python3 notes/tools/bigboard/trapped.py"""
import collections, os, pickle
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, 'deathctx.pkl'), 'rb'))
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']
def selfinf(c): return not (c.startswith('rammed') or c.startswith('ram_enemy') or c == 'killed_other')
for grp, maps in (('BIG', BIG), ('STRONG', STRONG)) + tuple((m, [m]) for m in BIG + STRONG):
    gs = [g for g in R if g['map'] in maps]; n = len(gs)
    print('== %s n=%d' % (grp, n))
    for tag in ('us', 'them'):
        si = [d for g in gs for d in g['deaths'] if d['tag'] == tag and selfinf(d['cls'])]
        # blocker composition over the 4 neighbours
        c = collections.Counter(x for d in si for x in d['nbrs'])
        tot = sum(c.values()) or 1
        cls = collections.Counter(d['cls'].split('_')[0] for d in si)
        allyN = sum(d['ally_near'] <= 2 for d in si) / max(1, len(si))
        enN = sum(d['enemy_near'] <= 3 for d in si) / max(1, len(si))
        phase = collections.Counter(min(3, d['round'] // 100) for d in si)
        print('  %-4s selfinf/g %6.1f | nbrs: %s | cls %s | ally head<=2 %.2f enemy head<=3 %.2f | by 100r %s' % (
            tag, len(si) / n, {k: round(v / tot, 2) for k, v in c.most_common()}, {k: round(v / n, 1) for k, v in cls.most_common(5)},
            allyN, enN, [round(phase[i] / n, 1) for i in range(4)]))
