#!/usr/bin/env python3
"""Eats by each team's current longest dragon in rounds 300-500, by pearl source.
    python3 notes/tools/king_eats.py
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
agg = collections.defaultdict(collections.Counter)
for s in summ:
    if s['end'] != 'roundLimit': continue
    key = 'W' if s['win'] else 'L'
    us = s['side']; them = 'B' if us == 'A' else 'A'
    g = simulate(os.path.join(DIR, f"{s['id']}.replay"))
    snap = dict(g['rounds'])
    c = {'us': collections.Counter(), 'them': collections.Counter()}
    for e in g['eats']:
        if e['round'] < 300: continue
        sn = snap.get(e['round'] - 1)
        if not sn: continue
        for k, T in (('us', us), ('them', them)):
            if e['id'] == sn[T]['king']:
                src = 'spawn' if not e['corpse'] else ('own' if e['corpse'][1] == T else 'enemy')
                c[k][src] += 1; c[k]['all'] += 1
    for k in c: agg[key + '_' + k] += c[k]
    agg[key]['n'] += 1
    print(s['id'], key, g['map'].name[:14].ljust(14), 'us', dict(c['us']), '| them', dict(c['them']))
for k in ('L', 'W'):
    n = agg[k]['n']
    print(k, 'avg king eats r300+: us', {a: round(b / n, 1) for a, b in agg[k + '_us'].items()}, 'them', {a: round(b / n, 1) for a, b in agg[k + '_them'].items()})
