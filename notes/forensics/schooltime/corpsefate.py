#!/usr/bin/env python3
"""Fate of a team's own corpse pearls created in [R0,R1): eaten by the team's king (longest at that
round), by another own dragon, by the enemy, or never.  python3 .../corpsefate.py LAYOUT [R0 R1]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
LAY = sys.argv[1]; R0 = int(sys.argv[2]) if len(sys.argv) > 2 else 250; R1 = int(sys.argv[3]) if len(sys.argv) > 3 else 500
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
for res in (False, True):
    Ds = [D for D in G.values() if lay(D) == LAY and D['win'] == res]; n = len(Ds)
    for side in ('us', 'them'):
        c = collections.Counter()
        for D in Ds:
            T = D[side]; kings = {r: D['tl'][r][T][3] for r in D['tl']}
            made = sum((d['len'] + 1) // 2 for d in D['deaths'] if d['team'] == T and R0 <= d['round'] < R1)
            c['made'] += made
            for e in D['eats']:
                cp = e['corpse']
                if cp is None or cp[1] != T or not (R0 <= cp[2] < R1): continue
                if e['team'] != T: c['enemy'] += 1
                elif e['id'] == kings.get(e['round'] - 1): c['king'] += 1
                else: c['own_other'] += 1
        c['never'] = c['made'] - c['king'] - c['own_other'] - c['enemy']
        print(LAY, 'W' if res else 'L', side, 'n=%d own corpse pearls r%d-%d per game: made %.0f  king %.0f  other own %.0f  enemy %.0f  uneaten %.0f' % (
            n, R0, R1, c['made'] / n, c['king'] / n, c['own_other'] / n, c['enemy'] / n, c['never'] / n))
