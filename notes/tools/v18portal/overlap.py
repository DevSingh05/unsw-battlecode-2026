#!/usr/bin/env python3
"""Deaths the warn-memo off-by-one (+1 round) would add on top of PORTAL_ECHO_GUARD, and what is left.
usage (from project root): python3 notes/tools/v18portal/overlap.py [ab_v18_Default]
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 else 'ab_v18_Default'
G = pickle.load(open(HERE / f'{name}.pkl', 'rb')); NG = len(G)
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


def fatal(r):
    return r['died'] is not None and r['died_step'] == r['k']


c = collections.Counter(); left = collections.Counter()
for g in G:
    for r in g['recs']:
        if not (r['us'] and fatal(r)):
            continue
        ps = [p for p in g['pings'].get(r['id'], []) if p['round'] == r['round'] - 1]
        e1 = len(r['move']) == 1 and r['age'] > 0 and any(p['hitKind'] in ('allyHead', 'enemyHead') for p in ps)
        e2 = len(r['move']) == 1 and r['age'] > 0 and any(p['hitKind'] in ('ally', 'allyHead', 'enemy', 'enemyHead') for p in ps)
        memo1 = False
        h = r['hit']
        if h and h[0] != 'self' and h[2] == r['team']:
            j = h[0]
            for p in g['pings'].get(j, []):
                if p['origin'] == r['exit'] and p['dir'] == OPP[r['dir']] and p['hitId'] == r['id'] and r['round'] - 12 <= p['round'] <= r['round']:
                    ok = p['round'] < r['round'] or r['id'] > j
                    if ok and r['round'] <= p['round'] + p['len']:
                        memo1 = True
        c['memo+1 saves'] += memo1
        c['memo+1 saves, not echo-heads'] += memo1 and not e1
        c['memo+1 saves, not echo-any'] += memo1 and not e2
        if not e2 and not memo1:
            hc = 'self' if (h and h[0] == 'self') else ('?' if not h else ('ally' if h[2] == r['team'] else 'enemy'))
            why = 'sprint' if len(r['move']) > 1 else 'newborn' if r['age'] == 0 else 'clean echo' if ps else 'no ray'
            left[(hc, why)] += 1
print(name, {k: round(v / NG, 1) for k, v in c.items()})
print('left after echo-any + memo+1:', {k: round(v / NG, 1) for k, v in left.most_common()})
