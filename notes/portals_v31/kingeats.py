#!/usr/bin/env python3
"""King intake on Portals server replays: eats by the team's current longest dragon per window, by source,
vs all team eats and dead mass. Run from project root: python3 notes/portals_v31/kingeats.py replays/ab_v30kc replays/ab_kc31"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/portals_v31'))
from sim2 import simulate
from mech import side_of
W = [(250, 350), (350, 400), (400, 450), (450, 500)]
agg = {k: collections.Counter() for k in ('L', 'W')}; n = collections.Counter()
for d in sys.argv[1:]:
    for g in json.load(open(os.path.join(ROOT, d, 'summary.json'))):
        if g['map'] != 'Portals': continue
        G = simulate(os.path.join(ROOT, d, '%d.replay' % g['id']))
        T = side_of(G, g['us']); rs = dict(G['rounds'])
        key = 'W' if g['win'] else 'L'; n[key] += 1
        for tag, TT in (('us', T), ('them', 'B' if T == 'A' else 'A')):
            for e in G['eats']:
                if e['team'] != TT: continue
                w = next((i for i, (a, b) in enumerate(W) if a <= e['round'] < b), None)
                if w is None: continue
                snap = rs.get(e['round'] - 1)
                king = snap and snap[TT]['king'] == e['id']
                big = e['len'] is not None and e['len'] >= 6
                src = 'corpse' if e['corpse'] else 'spawn'
                agg[key][(tag, w, 'all', src)] += 1
                if king: agg[key][(tag, w, 'king', src)] += 1
                elif big: agg[key][(tag, w, 'mid', src)] += 1
            for dd in G['deaths']:
                if dd['team'] != TT: continue
                w = next((i for i, (a, b) in enumerate(W) if a <= dd['round'] < b), None)
                if w is not None: agg[key][(tag, w, 'deadmass', '')] += (dd['len'] + 1) // 2
for key in ('L', 'W'):
    print('== %s (%d) per game, us / them ==' % (key, n[key]))
    for w, (a, b) in enumerate(W):
        f = lambda tag, who, src: agg[key][(tag, w, who, src)] / n[key]
        print(' r%d-%d: king corpse %.1f / %.1f, king spawn %.1f / %.1f | mid(L>=6 non-king) corpse %.1f / %.1f | all corpse %.1f / %.1f, all spawn %.1f / %.1f | pearls dropped by deaths %.1f / %.1f | king share of corpse eats %.2f / %.2f' % (
            a, b, f('us', 'king', 'corpse'), f('them', 'king', 'corpse'), f('us', 'king', 'spawn'), f('them', 'king', 'spawn'), f('us', 'mid', 'corpse'), f('them', 'mid', 'corpse'),
            f('us', 'all', 'corpse'), f('them', 'all', 'corpse'), f('us', 'all', 'spawn'), f('them', 'all', 'spawn'), f('us', 'deadmass', ''), f('them', 'deadmass', ''),
            f('us', 'king', 'corpse') / max(.01, f('us', 'all', 'corpse')), f('them', 'king', 'corpse') / max(.01, f('them', 'all', 'corpse'))))
