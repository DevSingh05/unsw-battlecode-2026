#!/usr/bin/env python3
"""Reverse splits (k = L-2) of big dragons and reverse-split CHAINS (a reverse-split child that
reverse-splits again within GAP rounds of its birth) per game.  python3 notes/forensics/schooltime/rsplit.py [minL]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
MINL = int(sys.argv[1]) if len(sys.argv) > 1 else 15
GAP = 10
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def pool(t): x, y = t; return 27 <= x <= 34 and 32 <= y <= 39
agg = collections.defaultdict(lambda: collections.Counter())
for gid, D in sorted(G.items()):
    us = D['us']; key = (lay(D), 'W' if D['win'] else 'L')
    agg[key]['n'] += 1
    for side in ('us', 'them'):
        T = D[side]
        rs = [s for s in D['splits'] if s['team'] == T and s['k'] == s['L'] - 2 and s['L'] >= MINL]
        born = {s['child']: s['round'] for s in rs}
        chain = [s for s in rs if s['parent'] in born and s['round'] - born[s['parent']] <= GAP]
        dead0 = 0
        for s in rs:
            for d in D['deaths']:
                if d['id'] == s['child'] and d['round'] - s['round'] <= 3: dead0 += 1
        agg[key][side + '_rs'] += len(rs); agg[key][side + '_chain'] += len(chain); agg[key][side + '_dead3'] += dead0
        agg[key][side + '_chainlen'] += 2 * len(chain)
        if side == 'us' and key[1] == 'L' and chain:
            print(gid, key, D['opp'][:14], 'rsplits', len(rs), 'chain', len(chain), 'first', chain[0]['round'], 'L', [s['L'] for s in chain][:12], 'child died<=3r', dead0)
print()
for key, c in sorted(agg.items()):
    n = c['n']
    print(key, 'n=%d' % n, ' '.join('%s %.1f' % (k, v / n) for k, v in sorted(c.items()) if k != 'n'))
