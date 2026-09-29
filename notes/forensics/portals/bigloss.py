#!/usr/bin/env python3
"""Every loss of an L>=8 dragon of ours on Portals (auto/games): death or split-trap, with category, and the
counterfactual final longest (what we'd have had if that dragon had kept its length to r500).
   python3 notes/forensics/portals/bigloss.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
C = collections.Counter(); CL = collections.Counter(); out = []
for gid in games:
    g = led[gid]; T = g['side']; th = 'B' if T == 'A' else 'A'
    S = simulate(os.path.join(GD, '%d.replay' % gid)); m = S['map']
    fin = dict(S['rounds'])[max(dict(S['rounds']))]
    us_f, th_f = fin[T]['max'], fin[th]['max']
    for d in S['deaths']:
        if d['team'] != T or d['len'] < 8: continue
        mv = d.get('move') or ''
        age = d['age']
        back = False
        if mv and d['actor'] == d['id']:
            # backward move = into own neck
            b = d['body']
            if len(b) > 1 and m.step(b[0], mv[0]) == b[1]: back = True
        if d['actor'] != d['id']: cat = 'killed_by_other'
        elif back and age <= 3: cat = 'newborn_backward(M3)'
        elif back: cat = 'backward_feed'
        elif d['reason'] == 'HitSelf': cat = 'hitself'
        elif d['reason'] == 'HitHeadToHead': cat = 'headon'
        elif d['reason'] == 'HitOtherBody': cat = 'hit_other(portal?)' if m.edges.get(m.side_edge(d['head'], mv[0]) if mv else None, (0,))[0] == 2 else 'hit_other'
        else: cat = d['reason']
        C[cat] += 1; CL[cat] += d['len']
        flip = (not g['win']) and d['len'] > th_f and d['round'] >= 440
        out.append((gid, 'W' if g['win'] else 'L', d['round'], d['id'], d['len'], cat, 'age%d' % age, 'final %d v %d' % (us_f, th_f), 'FLIP?' if flip else ''))
n = len(games)
for k in C: print('%-24s %3d deaths  %.2f/game  %.1f len/game' % (k, C[k], C[k] / n, CL[k] / n))
for r in out:
    if r[4] >= 15 or r[-1]: print(*r)
