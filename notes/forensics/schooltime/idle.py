#!/usr/bin/env python3
"""Hunger: share of dragon-turns (r0-R1) whose dragon hasn't eaten for >= 30 / 60 rounds (since birth or last eat),
and net displacement over 20 rounds (oscillation), us vs them.  python3 .../idle.py LAYOUT W|L [R1]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
LAY = sys.argv[1]; RES = sys.argv[2]; R1 = int(sys.argv[3]) if len(sys.argv) > 3 else 250
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
Ds = [D for D in G.values() if lay(D) == LAY and D['win'] == (RES == 'W')]
c = {s: collections.Counter() for s in ('us', 'them')}
for D in Ds:
    last = dict(D['born'])
    for e in sorted(D['eats'], key=lambda e: e['round']):
        pass
    eat_rounds = collections.defaultdict(list)
    for e in D['eats']: eat_rounds[e['id']].append(e['round'])
    pos = collections.defaultdict(dict); tm = {}
    for m in D['moves']:
        if m['round'] >= R1: continue
        side = 'us' if m['team'] == D['us'] else 'them'
        i = m['id']; r = m['round']
        prev = [x for x in eat_rounds[i] if x < r]
        since = r - (max(prev) if prev else D['born'].get(i, 0))
        c[side]['turns'] += 1
        c[side]['h30'] += since >= 30; c[side]['h60'] += since >= 60
        pos[i][r] = m['head']; tm[i] = side
    m = D['map'] if 'map' in D else None
    for i, pr in pos.items():
        side = tm[i]
        for r, h in pr.items():
            if r + 20 in pr:
                h2 = pr[r + 20]
                dist = abs(h[0] - h2[0]) + abs(h[1] - h2[1])
                c[side]['w20'] += 1; c[side]['stuck20'] += dist <= 4
for s in ('us', 'them'):
    x = c[s]
    print(LAY, RES, s, 'turns/g %.0f  hungry>=30 %.0f%%  >=60 %.0f%%  within 4 tiles after 20 rounds %.0f%%' % (
        x['turns'] / len(Ds), 100 * x['h30'] / x['turns'], 100 * x['h60'] / x['turns'], 100 * x['stuck20'] / max(1, x['w20'])))
