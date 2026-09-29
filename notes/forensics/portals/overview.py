#!/usr/bin/env python3
"""Portals games in replays/auto/games: per-game timeline (us/them) -> overview.pkl
   python3 notes/forensics/portals/overview.py   (from project root)"""
import json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
L = [g for g in json.load(open(os.path.join(GD, 'ledger.json'))) if g['map'] == 'Portals']
out = {}
CH = [50, 100, 200, 300, 350, 400, 425, 450, 475, 499]
for g in sorted(L, key=lambda g: g['game']):
    p = os.path.join(GD, '%d.replay' % g['game'])
    if not os.path.exists(p):
        print('missing', g['game']); continue
    G = simulate(p)
    us = g['side']; th = 'B' if us == 'A' else 'A'
    R = dict(G['rounds'])
    row = {}
    for c in CH:
        s = R.get(c) or R[max(R)]
        row[c] = {T: (s[T]['max'], s[T]['n'], s[T]['total']) for T in (us, th)}
    out[g['game']] = dict(g, G=None, row=row, us=us, th=th)
    f = row[499]
    print(g['game'], g['opp'][:14].ljust(14), 'W' if g['win'] else 'L', us, 'final %2d v %2d' % (f[us][0], f[th][0]),
          ' | '.join('r%d %d/%d(%du)' % (c, row[c][us][0], row[c][th][0], row[c][us][1]) for c in (300, 400, 450)), flush=True)
pickle.dump(out, open(os.path.join(os.path.dirname(__file__), 'overview.pkl'), 'wb'))
