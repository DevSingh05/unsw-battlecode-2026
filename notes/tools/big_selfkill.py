#!/usr/bin/env python3
"""Our dragons of length >= 8 dying HitSelf: were they feeding (backward move with free
exits) or trapped? How long was the real longest ally at that moment, and how far?
    python3 notes/tools/big_selfkill.py
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
tot = collections.Counter(); lost_len = collections.Counter()
for s in summ:
    if s['end'] != 'roundLimit': continue
    g = simulate(os.path.join(DIR, f"{s['id']}.replay"))
    m = g['map']
    for d in g['deaths']:
        if d['team'] != s['side'] or d['len'] < 8 or d['reason'] != 'HitSelf': continue
        mv = d.get('move') or ''
        dest = m.step(d['body'][0], mv[d['step_failed'] - 1]) if mv else None
        back = dest == d['body'][1]
        nfree = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        k = d.get('king') or (None, 0, 99, 99)
        kind = ('feed' if back and nfree > 0 else ('trapped' if nfree == 0 else 'other'))
        bigger = k[1] >= d['len'] + 2
        tot[(kind, 'king_bigger' if bigger else 'NO_bigger_ally')] += 1
        lost_len[(kind, 'king_bigger' if bigger else 'NO_bigger_ally')] += d['len']
        print(f"{s['id']} {'W' if s['win'] else 'L'} r{d['round']} len {d['len']:2d} {kind:7s} free {nfree} longest-ally len {k[1]} dist {k[2]}")
print(dict(tot)); print('length lost', dict(lost_len))
