#!/usr/bin/env python3
"""All deliberate feed suicides (our HitSelf backward move with a free exit, round >= 330):
distance to the real longest ally, feeder length, and where the pearls went.
    python3 notes/tools/feed_eff.py
"""
import collections, json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
C = collections.Counter(); distb = collections.Counter(); lenb = collections.Counter()
for s in summ:
    if s['end'] != 'roundLimit': continue
    us = s['side']
    g = simulate(os.path.join(DIR, f"{s['id']}.replay")); m = g['map']
    feeders = {}
    for d in g['deaths']:
        if d['team'] != us or d['reason'] != 'HitSelf' or d['round'] < 330: continue
        mv = d.get('move') or ''
        if not mv or m.step(d['body'][0], mv[d['step_failed'] - 1]) != d['body'][1]: continue
        if not any(v in ('free', 'pearl') for v in d['nbrs'].values()): continue
        k = d.get('king') or (None, 0, 99, 99)
        feeders[d['id']] = (k[0], d['len'], k[2])
        C['feeders'] += 1; C['feeder_len'] += d['len']; C['drop'] += math.ceil(d['len'] / 2)
        distb['<=4' if k[2] <= 4 else ('5-8' if k[2] <= 8 else '>8')] += 1
        lenb['2-3' if d['len'] <= 3 else ('4-7' if d['len'] <= 7 else '8+')] += 1
    for e in g['eats']:
        c = e['corpse']
        if c and c[0] in feeders and e['round'] - c[2] <= 40:
            C['eaten_by_' + ('king' if e['id'] == feeders[c[0]][0] else ('ally' if e['team'] == us else 'enemy'))] += 1
print(dict(C)); print('dist to real longest ally', dict(distb)); print('feeder length', dict(lenb))
