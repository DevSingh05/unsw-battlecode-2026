#!/usr/bin/env python3
"""Non-combat deaths on Devil (HitSelf / HitOtherBody on an ally / HitWall / NoValidAction), classified:
  tube-jam : head inside a 1-wide tube (kelp both sides) with an ALLY head or body blocking the only way on
  pocket   : head in a dead-end pocket (Ctop/Cbot 15-16 x y0-2/13-15), no free neighbour
  stillborn: age 0-1 (a split child with no exit)
  other
Per game us/them and length lost.
    python3 notes/forensics/devil/jams.py
"""
import collections
from common import games, sim, REFMAP as m


def one_wide(t):
    x, y = t
    kw = m.edges.get(('V', x, y), (0,))[0] == 1; ke = m.edges.get(('V', (x + 1) % m.w, y), (0,))[0] == 1
    kn = m.edges.get(('H', x, y), (0,))[0] == 1; ks = m.edges.get(('H', x, (y + 1) % m.h), (0,))[0] == 1
    return (kw and ke) or (kn and ks)


def classify(d):
    nb = d['nbrs']
    if d['age'] <= 1: return 'stillborn'
    x, y = d['head']
    if x in (15, 16) and (y <= 2 or y >= 13): return 'pocket'
    if one_wide(d['head']) and any(isinstance(v, tuple) and v[0] == 'ally' for v in nb.values()): return 'tube-jam'
    if any(isinstance(v, tuple) and v[0] == 'ally' and v[1] for v in nb.values()): return 'ally-head-block'
    return 'other'


tot = collections.defaultdict(collections.Counter)
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']
    c = collections.Counter(); ln = collections.Counter()
    for d in S['deaths']:
        if d['round'] > 150: break
        if d['reason'] == 'HitHeadToHead': continue
        if d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] != d['team']: continue  # hit enemy body
        k = (d['team'] == us, classify(d))
        c[k] += 1; ln[k] += d['len']
    res = 'W' if g['win'] else 'L'
    for k, v in c.items(): tot[res][k] += v; tot[res + 'len'][k] += ln[k]
    print(g['game'], g['opp'][:12].ljust(12), res, ' '.join('%s:%d/%d' % (cl, c[(True, cl)], c[(False, cl)]) for cl in ('tube-jam', 'pocket', 'stillborn', 'ally-head-block', 'other')))
ng = collections.Counter('W' if g['win'] else 'L' for g in games())
for res in 'LW':
    print(res, 'per game us/them (mean len):', ' '.join('%s %.1f/%.1f (L%.1f/%.1f)' % (cl, tot[res][(True, cl)] / ng[res], tot[res][(False, cl)] / ng[res],
          tot[res + 'len'][(True, cl)] / max(1, tot[res][(True, cl)]), tot[res + 'len'][(False, cl)] / max(1, tot[res][(False, cl)]))
          for cl in ('tube-jam', 'pocket', 'stillborn', 'ally-head-block', 'other')))
