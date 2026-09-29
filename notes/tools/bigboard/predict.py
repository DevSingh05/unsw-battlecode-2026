#!/usr/bin/env python3
"""Which r50-r150 feature separates big-board wins from losses vs top-15 (notes/23).
    python3 notes/tools/bigboard/predict.py [maps...]
AUC of (us - them) or us/them features at a given round for predicting a win."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import GS, BIG, STRONG, tlv, mean

def auc(pos, neg):
    if not pos or not neg: return float('nan')
    s = 0
    for p in pos:
        for n in neg:
            s += 1 if p > n else (0.5 if p == n else 0)
    return s / (len(pos) * len(neg))

def eats(g, tag, a, b, f=lambda k: True):
    return sum(v for k, v in g[tag]['eats'].items() if a <= k[0] * 100 < b and f(k))

def deaths(g, tag, a, b, f=lambda d: True):
    return sum(1 for d in g[tag]['deaths'] if a <= d[0] < b and f(d))

maps = sys.argv[1:] or BIG
sub = [g for g in GS if g['map'] in maps and g['top']]
W = [g for g in sub if g['win']]; L = [g for g in sub if not g['win']]
print('maps', maps, 'W', len(W), 'L', len(L))
feats = {}
for r in (50, 75, 100, 150, 200):
    feats['units diff r%d' % r] = lambda g, r=r: tlv(g, 'us', r)[0] - tlv(g, 'them', r)[0]
    feats['total diff r%d' % r] = lambda g, r=r: tlv(g, 'us', r)[1] - tlv(g, 'them', r)[1]
    feats['tile share r%d' % r] = lambda g, r=r: g['us']['terr'].get(r, (0,))[0]
    feats['income share r%d' % r] = lambda g, r=r: g['us']['terr'].get(r, (0, 0))[1]
    feats['cover diff r%d' % r] = lambda g, r=r: g['us']['terr'].get(r, (0, 0, 0))[2] - g['them']['terr'].get(r, (0, 0, 0))[2]
    feats['nn spread us r%d' % r] = lambda g, r=r: (g['us']['zonefrac'].get(r) or (0,) * 6)[5]
    feats['far frac diff r%d' % r] = lambda g, r=r: (g['us']['zonefrac'].get(r) or (0,) * 6)[2] - (g['them']['zonefrac'].get(r) or (0,) * 6)[2]
feats['spawn eats diff r0-99'] = lambda g: eats(g, 'us', 0, 100, lambda k: k[2] == 'spawn') - eats(g, 'them', 0, 100, lambda k: k[2] == 'spawn')
feats['spawn eats diff r100-199'] = lambda g: eats(g, 'us', 100, 200, lambda k: k[2] == 'spawn') - eats(g, 'them', 100, 200, lambda k: k[2] == 'spawn')
feats['deaths diff r0-99 (neg)'] = lambda g: -(deaths(g, 'us', 0, 100) - deaths(g, 'them', 0, 100))
feats['deaths diff r100-199 (neg)'] = lambda g: -(deaths(g, 'us', 100, 200) - deaths(g, 'them', 100, 200))
feats['enemy corpse diff r0-199'] = lambda g: eats(g, 'us', 0, 200, lambda k: k[2] == 'enemy') - eats(g, 'them', 0, 200, lambda k: k[2] == 'enemy')
feats['net (eats-deathlen) diff r0-99'] = lambda g: (eats(g, 'us', 0, 100) - sum(d[1] for d in g['us']['deaths'] if d[0] < 100)) - (eats(g, 'them', 0, 100) - sum(d[1] for d in g['them']['deaths'] if d[0] < 100))
feats['far spawn eats diff r0-199'] = lambda g: eats(g, 'us', 0, 200, lambda k: k[2] == 'spawn' and not k[3]) - eats(g, 'them', 0, 200, lambda k: k[2] == 'spawn' and not k[3])
feats['near spawn eats diff r0-199'] = lambda g: eats(g, 'us', 0, 200, lambda k: k[2] == 'spawn' and k[3]) - eats(g, 'them', 0, 200, lambda k: k[2] == 'spawn' and k[3])
res = []
for k, f in feats.items():
    pw = [f(g) for g in W]; pl = [f(g) for g in L]
    res.append((auc(pw, pl), k, mean(pw), mean(pl)))
for a, k, mw, ml in sorted(res, reverse=True):
    print('%.2f  %-32s W %7.2f  L %7.2f' % (a, k, mw, ml))
