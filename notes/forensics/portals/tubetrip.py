#!/usr/bin/env python3
"""Every tube trip by a dragon of L>=MIN (enters a [1,10] pearl tile from the main area): pearls eaten, outcome
(clean exit / reverse split at the end / death), per team.  python3 notes/forensics/portals/tubetrip.py [MIN]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
PEARL = {t for t, g in REF.tiles.items() if g[1] > 0 and g != (1, 1)}
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 8
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
A = collections.defaultdict(collections.Counter); N = collections.Counter()
for gid in games:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; N[grp] += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    byid = collections.defaultdict(list)
    for a in S['moves']: byid[a['id']].append(('m', a['round'], a))
    for s in S['splits']: byid[s['parent']].append(('s', s['round'], s))
    for d in S['deaths']: byid[d['id']].append(('d', d['round'], d))
    for i, evs in byid.items():
        evs.sort(key=lambda e: (e[1], {'m': 0, 's': 0, 'd': 1}[e[0]]))
        T = S['team'][i]; who = 'us' if T == us else 'them'
        trip = None
        for kind, r, e in evs:
            if r < 200: continue
            if kind == 'm':
                h0, h1 = e['head'], e.get('head_after')
                if trip is None and h0 not in PEARL and h1 in PEARL and e['len_before'] >= MIN:
                    trip = {'L': e['len_before'], 'ate': e['ate'], 'r': r}
                elif trip is not None:
                    trip['ate'] += e['ate']
                    if h1 is None or h1 not in PEARL:
                        out = 'died' if h1 is None else 'clean'
                        A[(grp, who)]['trip_' + out] += 1; A[(grp, who)]['ate_' + out] += trip['ate']
                        trip = None
            elif kind == 's' and trip is not None:
                A[(grp, who)]['trip_split'] += 1; A[(grp, who)]['ate_split'] += trip['ate']; A[(grp, who)]['split_len'] += e['L']
                kk = e['k']; LL = e['L']
                A[(grp, who)]['split_k=L-2(reverse)' if kk >= LL - 2 else ('split_k<=3(peel)' if kk <= 3 else 'split_k_mid')] += 1
                trip = None
            elif kind == 'd' and trip is not None:
                A[(grp, who)]['trip_died'] += 1; A[(grp, who)]['died_len'] += e['len']; trip = None
for grp in 'LW':
    n = N[grp]; print('== %s (%d games): tube trips of L>=%d dragons r200+, per game us / them' % (grp, n, MIN))
    for k in sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')])):
        print('  %-12s %6.2f / %6.2f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
