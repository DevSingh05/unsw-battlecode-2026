#!/usr/bin/env python3
"""Round-limit games: our peak longest length vs final, vs their final; round our max
first reached 8/15; growth of the longest dragon per 50 rounds (us/them).
    python3 notes/tools/king_peak.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
flip = 0
for s in summ:
    if s['end'] != 'roundLimit': continue
    us = s['side']; them = 'B' if us == 'A' else 'A'
    g = simulate(os.path.join(DIR, f"{s['id']}.replay"))
    rs = g['rounds']
    mu = [(r, x[us]['max']) for r, x in rs]; mt = [(r, x[them]['max']) for r, x in rs]
    pr, pk = max(mu, key=lambda t: (t[1], -t[0]))
    fu, ft = mu[-1][1], mt[-1][1]
    first = lambda arr, L: next((r for r, v in arr if v >= L), None)
    would = pk >= ft and fu < ft
    flip += would and not s['win']
    print(f"{s['id']} {'W' if s['win'] else 'L'} {g['map'].name[:15]:15s} final us {fu:2d} them {ft:2d} | our peak {pk:2d}@r{pr} "
          f"{'PEAK>=THEIR FINAL' if would else ''} | reach8 us r{first(mu,8)} them r{first(mt,8)} reach15 us r{first(mu,15)} them r{first(mt,15)}")
print('losses where our peak >= their final length:', flip)
