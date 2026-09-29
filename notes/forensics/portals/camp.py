#!/usr/bin/env python3
"""Tube-mouth camping: dragons circling in a 2x2 loop (head(t)==head(t-4), head(t)!=head(t-2)) and their distance to the
nearest tube mouth tile (entry e or exit x of a tube, own team's tubes). Us vs them, per game.
   python3 notes/forensics/portals/camp.py [GAME...]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = [int(a) for a in sys.argv[1:]] or sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
# mouths: main tiles e with a step into a [1,10] tile
PEARL = {t for t, g in REF.tiles.items() if g[1] > 0 and g != (1, 1)}
MOUTH = set()
for x in range(REF.w):
    for y in range(REF.h):
        if REF.tiles.get((x, y), (0, 0))[1] > 0: continue
        for d in 'NESW':
            v = REF.step((x, y), d)
            if v in PEARL: MOUTH.add((x, y))
A = collections.defaultdict(collections.Counter)
for gid in games:
    g = led[gid]; us = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    hist = collections.defaultdict(dict)
    for a in S['moves']:
        hist[a['id']][a['round']] = a['head']
    grp = 'W' if g['win'] else 'L'
    for i, h in hist.items():
        who = 'us' if S['team'][i] == us else 'them'
        for r, p in h.items():
            if r < 150: continue
            ph = 'r150-300' if r < 300 else 'r300-450' if r < 450 else 'r450+'
            A[(grp, who)]['dragon_rounds ' + ph] += 1
            if h.get(r - 4) == p and h.get(r - 2) not in (None, p):
                near = min(REF.dist(p, q) for q in MOUTH)
                A[(grp, who)]['loop ' + ph] += 1
                if near <= 1: A[(grp, who)]['loop@mouth ' + ph] += 1
    A[(grp, 'n')]['g'] += 1
for grp in 'LW':
    n = A[(grp, 'n')]['g']
    print('== %s (%d games), per game' % (grp, n))
    for k in sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')])):
        print('  %-26s us %7.1f   them %7.1f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
