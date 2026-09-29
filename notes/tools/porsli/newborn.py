#!/usr/bin/env python3
"""All maps (replays/v28): our dragons of L>=10 that die within 3 rounds of being born from a split
(nearly always a reverse split of a long dragon: child = parent's rear L-2).  Classified by the fatal move:
backward into own neck (= feed suicide, the child obeys a stale king broadcast), other own-body hit with a
free neighbour (chose), no free neighbour (trapped), rammed, portal.
    python3 notes/tools/porsli/newborn.py"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.dirname(__file__))
from sim2 import simulate
from collect import classify
C = collections.Counter(); Ln = collections.Counter(); n = collections.Counter(); ex = collections.defaultdict(list)
for g in json.load(open(os.path.join(ROOT, 'replays/v28/ledger.json'))):
    p = os.path.join(ROOT, 'replays/v28/%d.replay' % g['game'])
    if not os.path.exists(p): continue
    S = simulate(p); m = S['map']; T = g['side']; n[g['map']] += 1
    rs = dict(S['rounds'])
    for d in S['deaths']:
        if d['team'] != T or d['len'] < 10 or d['age'] > 3 or d['id'] not in S['parent_of']: continue
        mv = d.get('move') or ''
        c = classify(S, d)
        if d['actor'] == d['id'] and len(mv) == 1 and len(d['body']) > 1 and m.step(d['head'], mv) == d['body'][1]:
            c = 'backward_into_neck'
        prev = rs.get(d['round'] - 1, rs.get(d['round']))[T]
        wasmax = d['len'] >= max([L for i, L in prev['ids'].items() if i != d['id'] and i != S['parent_of'][d['id']]] + [0])
        key = (g['map'], c, 'team-longest' if wasmax else 'not-longest')
        C[key] += 1; Ln[key] += d['len']
        if wasmax and len(ex[key]) < 4: ex[key].append('%d r%d L%d %s' % (g['game'], d['round'], d['len'], 'W' if g['win'] else 'L'))
tot = collections.Counter()
for k in sorted(C):
    print('%-18s %-22s %-12s n=%3d (%.2f/g) length %4d  %s' % (k[0], k[1], k[2], C[k], C[k] / n[k[0]], Ln[k], ex.get(k, '')))
    tot[k[2]] += C[k]; tot[k[2] + '_len'] += Ln[k]
print(dict(tot), 'games', sum(n.values()))
