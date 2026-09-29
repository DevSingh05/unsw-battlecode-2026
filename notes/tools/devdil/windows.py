#!/usr/bin/env python3
"""Per-window (default 10 rounds) summary of one game: units, eats (hot/spawn/corpse), splits, deaths by cause.
    python3 notes/tools/devdil/windows.py GAME [W=10] [r0] [r1]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
GS = {g['game']: g for g in pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))}
REF = {'Devil': 'notes/maps/Devil__id13.map', 'Prisoners Dilemma': 'notes/maps/Prisoners_Dilemma__id17.map'}
a = sys.argv[1:]; g = GS[int(a[0])]; W = int(a[1]) if len(a) > 1 else 10
r0 = int(a[2]) if len(a) > 2 else 0; r1 = int(a[3]) if len(a) > 3 else 501
S = simulate(g['path']); us = g['us']; ref = Map(open(os.path.join(ROOT, REF[g['map']])).read())
snaps = dict(S['rounds'])
ab = {'ram_enemy': 'R', 'rammed_by_enemy': 'r', 'self_trapped': 's', 'self': 'S', 'ally_body_trapped': 'a', 'ally_body': 'A',
      'wall_trapped': 'w', 'wall': 'W', 'nva': 'n', 'enemy_body_trapped': 'e', 'enemy_body': 'E', 'headon_ally': 'h'}
print(g['game'], g['map'], g['opp'], 'W' if g['win'] else 'L', 'deaths: R=we rammed r=got rammed s/S=self(trapped) a/A=ally body w/W=wall n=nva e/E=enemy body h=ally headon')
print('window   units u/t  tot u/t  max u/t | eats us h/s/c   them h/s/c | splits u/t | deaths us / them')
for w0 in range(r0, min(r1, S['last_round'] + 1), W):
    w1 = w0 + W
    s = snaps.get(min(w1, S['last_round']))
    e = collections.Counter()
    for x in S['eats']:
        if w0 <= x['round'] < w1:
            k = 'c' if x['corpse'] else ('h' if ref.tiles.get(tuple(x['tile']), (0, 0)) == (1, 1) else 's')
            e[('us' if x['team'] == us else 'them', k)] += 1
    sp = collections.Counter('us' if x['team'] == us else 'them' for x in S['splits'] if w0 <= x['round'] < w1)
    dd = {'us': '', 'them': ''}
    for d in g['dl']:
        if w0 <= d['round'] < w1:
            dd[d['who']] += ab.get(d['cat'], '?') + ('%d' % d['len'] if d['len'] >= 4 else '')
    print('%3d-%3d  %2d/%2d   %3d/%3d  %2d/%2d  | %2d/%2d/%2d   %2d/%2d/%2d | %2d/%2d | %s / %s' % (
        w0, w1, s[us]['n'], s['B' if us == 'A' else 'A']['n'], s[us]['total'], s['B' if us == 'A' else 'A']['total'], s[us]['max'], s['B' if us == 'A' else 'A']['max'],
        e[('us', 'h')], e[('us', 's')], e[('us', 'c')], e[('them', 'h')], e[('them', 's')], e[('them', 'c')], sp['us'], sp['them'], dd['us'], dd['them']))
