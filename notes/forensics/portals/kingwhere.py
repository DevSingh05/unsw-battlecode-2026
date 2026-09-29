#!/usr/bin/env python3
"""Where does each team's longest dragon (L>=10) spend r300-500, and how often does it enter tubes / get stuck at a tube end?
   python3 notes/forensics/portals/kingwhere.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
KIND = {}
for t, g in REF.tiles.items():
    KIND[t] = 'hot' if g == (1, 1) else ('pearl' if g[1] > 0 else 'main')
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
A = collections.defaultdict(collections.Counter); N = collections.Counter()
for gid in games:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; N[grp] += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid)); R = dict(S['rounds'])
    for a in S['moves']:
        r = a['round']
        if r < 300 or r - 1 not in R: continue
        T = a['team']
        if R[r - 1][T]['king'] != a['id'] or a['len_before'] < 10: continue
        who = 'us' if T == us else 'them'
        k0 = KIND.get(a['head'], 'main'); k1 = KIND.get(a['head_after'], 'main') if a['head_after'] else 'dead'
        A[(grp, who)]['king_turns'] += 1
        A[(grp, who)]['on_' + k0] += 1
        if k0 != 'pearl' and k1 == 'pearl': A[(grp, who)]['tube_entries'] += 1
        A[(grp, who)]['ate'] += a['ate']
        if k0 == 'pearl': A[(grp, who)]['ate_in_tube'] += a['ate']
for grp in 'LW':
    n = N[grp]; print('== %s (%d games) king (longest, L>=10) r300-500, per game us / them' % (grp, n))
    for k in sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')])):
        print('  %-14s %6.1f / %6.1f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
