"""Counterfactual flips over ALL our reconstructed turns: for each penalty term, would removing it from a candidate make that
candidate the argmax (i.e. did the rule change the move)?  Terms: areaP (split by POCKET reason), depthP, threatP, box.
Counts per game, and how many of the flipped turns had the flipped candidate moving into a pocket tile."""
import collections, pickle
from common import *
from parsedbg import parse
tot = collections.defaultdict(collections.Counter)
for g in GAMES:
    S = sim(g); PK = S['PK']
    L = pickle.load(open('life_%d.pkl' % g, 'rb'))
    for i, lst in L.items():
        for x in lst:
            P = parse(x['dbg']); cs = P['cands']
            if len(cs) < 2 or not (x['real'] or '').startswith('MOVE'): continue
            best = max(cs.values(), key=lambda c: c['score'])
            for d, c in cs.items():
                if c is best: continue
                for k in ('areaP', 'depthP', 'threatP', 'box'):
                    v = c.get(k, 0)
                    if k == 'box': v = -v
                    if v <= 0: continue
                    if c['score'] + v > best['score']:
                        lab = k
                        if k == 'areaP': lab = 'areaP[POCKET %s]' % (c.get('pocket') or 'none')
                        if k == 'areaP' and c.get('depthP', 0) > 0: lab += '+depth'
                        if k == 'depthP' and c.get('areaP', 0) > 0: continue
                        tot[g][lab + (' ->pocket' if c['t'] in PK else '')] += 1
                        tot[g]['turns-with-a-flip'] += 0
    tot[g]['ALL turns'] = sum(len(v) for v in L.values())
keys = sorted({k for v in tot.values() for k in v})
for k in keys: print('%-40s' % k + ''.join('%9d' % tot[g][k] for g in GAMES))
