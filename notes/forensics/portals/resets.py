#!/usr/bin/env python3
"""Both teams: splits by a dragon of L>=6 whose head is on a tube/pocket pearl tile (gap [1,10]) = a trapped tube/pocket
end split, and whether the splitter was its team's longest. Plus L>=8 deaths by class. Per-team means.
   python3 notes/forensics/portals/resets.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
TUBE = {t for t, g in REF.tiles.items() if g == (1, 10)}
HOT = {t for t, g in REF.tiles.items() if g == (1, 1)}
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
A = collections.defaultdict(collections.Counter)
for gid in games:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    R = dict(S['rounds'])
    grp = 'L' if not g['win'] else 'W'
    for s in S['splits']:
        if s['L'] < 6 or s['round'] < 200: continue
        who = 'us' if s['team'] == us else 'them'
        snap = R.get(s['round'] - 1) or R.get(s['round'])
        longest = snap[s['team']]['max'] <= s['L'] + 1
        # head of parent at split time: parent's body head is unchanged by the split
        # (sim2 splits record has no head; approximate by child tail... use parentBody via moves)
        A[(grp, who)]['splits_L6+'] += 1
        if s['exits'] == 0: A[(grp, who)]['trapped_splits_L6+'] += 1
        if s['exits'] == 0 and longest: A[(grp, who)]['trapped_split_of_longest'] += 1
    for d in S['deaths']:
        if d['len'] < 8 or d['round'] < 200: continue
        who = 'us' if d['team'] == us else 'them'
        A[(grp, who)]['deaths_L8+'] += 1; A[(grp, who)]['deathlen_L8+'] += d['len']
        if d['head'] in TUBE: A[(grp, who)]['deaths_L8+_on_tube_tile'] += 1
    A[(grp, 'n')]['games'] += 1
for grp in 'LW':
    n = A[(grp, 'n')]['games']
    print('== %s (%d games)' % (grp, n))
    keys = sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')]))
    for k in keys: print('  %-28s us %5.2f  them %5.2f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
