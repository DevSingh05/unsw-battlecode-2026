#!/usr/bin/env python3
"""Where does the longest dragon's length go? r300-500, per team: sum of positive steps of max-length (growth)
and of negative steps, attributed to: king split (trapped / open), king death, king sprint, other.
   python3 notes/forensics/portals/kingloss.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
A = collections.defaultdict(collections.Counter); N = collections.Counter()
for gid in games:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; N[grp] += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid)); R = dict(S['rounds'])
    ev = collections.defaultdict(list)
    for s in S['splits']: ev[(s['round'], s['parent'])].append(('split_trapped' if s['exits'] == 0 else 'split_open', s['L'] - s['k']))
    for d in S['deaths']: ev[(d['round'], d['id'])].append(('death', d['len']))
    for a in S['moves']:
        if a.get('steps', 0) >= 2: ev[(a['round'], a['id'])].append(('sprint', a['steps'] - 1))
    for T in 'AB':
        who = 'us' if T == us else 'them'
        for r in range(301, 500):
            if r not in R or r - 1 not in R: continue
            k0 = R[r - 1][T]['king']; m0 = R[r - 1][T]['max']; m1 = R[r][T]['max']
            dm = m1 - m0
            if dm > 0: A[(grp, who)]['growth'] += dm
            elif dm < 0:
                cause = 'other'
                for c, v in ev.get((r, k0), []):
                    cause = c
                A[(grp, who)]['drop_' + cause] += -dm
                A[(grp, who)]['n_' + cause] += 1
for grp in 'LW':
    n = N[grp]; print('== %s (%d games): longest-dragon length r300-500, per game (us / them)' % (grp, n))
    for k in sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')])):
        print('  %-20s %6.1f / %6.1f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
