#!/usr/bin/env python3
"""Portals: how the big dragons (L>=10) use tubes/pockets/sock, per team, W/L.
    python3 notes/tools/porsli/kingtube.py [v28|old|all]
Counts per game for dragons with L>=10 at the time: moves by tile kind, eats by tile kind (spawn vs corpse),
tube entries, and deaths whose fatal step entered/left a structure."""
import collections, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.dirname(__file__))
from sim2 import simulate, Map
from board import path_of
M = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
kind = {t: ('hot' if g == (1, 1) else 'struct') if g[1] > 0 else 'main' for t, g in M.tiles.items()}
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
ver = sys.argv[1] if len(sys.argv) > 1 else 'v28'
gs = [g for g in G if g['map'] == 'Portals' and (ver == 'all' or g['ver'] == ver)]
A = {k: collections.Counter() for k in 'LW'}; n = collections.Counter()
for g in gs:
    S = simulate(path_of(g['game'])); grp = 'W' if g['win'] else 'L'; n[grp] += 1
    for tag, T in (('us', g['side']), ('them', 'B' if g['side'] == 'A' else 'A')):
        C = A[grp]
        for mv in S['moves']:
            if mv['team'] != T or mv['len_before'] < 10 or mv.get('suicide'):
                continue
            k0 = kind.get(mv['head'], 'main')
            C[tag + '_moves'] += 1
            C[tag + '_in_' + k0] += 1
            if mv.get('head_after') and k0 == 'main' and kind.get(mv['head_after'], 'main') != 'main':
                C[tag + '_entries'] += 1
        for e in S['eats']:
            if e['team'] == T and (e['len'] or 0) >= 10:
                C[tag + '_eat_%s_%s' % (kind.get(e['tile'], 'main'), 'c' if e['corpse'] else 's')] += 1
for grp in 'LW':
    if not n[grp]: continue
    C = A[grp]
    print('== Portals %s %s (%d games): per game, dragons with L>=10' % (ver, grp, n[grp]))
    for tag in ('us', 'them'):
        f = lambda k: C[tag + '_' + k] / n[grp]
        mv = max(1, C[tag + '_moves'])
        print('  %-4s moves %.0f (in structures %.0f%%) | tube entries %.1f | eats: struct %.1f, hot %.1f, main spawn %.1f, corpse %.1f' % (
            tag, f('moves'), 100 * (C[tag + '_in_struct'] + C[tag + '_in_hot']) / mv, f('entries'), f('eat_struct_s'), f('eat_hot_s'), f('eat_main_s'),
            f('eat_main_c') + f('eat_struct_c') + f('eat_hot_c')))
