#!/usr/bin/env python3
"""Deaths of big dragons (L>=MINL) per game, classified:
  ram_small : head-on with an enemy of length <= 4 (we lose L, they lose <=4)
  ram_big   : head-on with a longer enemy
  newborn   : reverse-split child (k=L-2 of a parent) dying within 3 rounds of birth, on its own move
  self      : other deaths on our own move (HitSelf / ally body / wall)
  hit_enemy_body / other
    python3 notes/forensics/schooltime/bigdeaths.py [MINL]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
MINL = int(sys.argv[1]) if len(sys.argv) > 1 else 15
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def classify(D, d, T):
    rs = {s['child']: s for s in D['splits'] if s['team'] == T and s['k'] == s['L'] - 2}
    if d['id'] in rs and d['round'] - rs[d['id']]['round'] <= 3 and d['actor'] == d['id'] and d['reason'] != 'HitHeadToHead':
        return 'newborn'
    if d['reason'] == 'HitHeadToHead':
        kl = d.get('killer_len') or d.get('victim_len') or 0
        kt = d.get('killer_team') or d.get('victim_team')
        if kt == T: return 'h2h_ally'
        return 'ram_small' if kl <= 4 else 'ram_big'
    if d['actor'] == d['id']:
        h = d.get('hit')
        if h and h['team'] != T: return 'hit_enemy_body'
        return 'self'
    return 'other'
agg = collections.defaultdict(collections.Counter)
for gid, D in G.items():
    key = (lay(D), 'W' if D['win'] else 'L'); agg[key]['n'] += 1
    for side in ('us', 'them'):
        T = D[side]
        for d in D['deaths']:
            if d['team'] != T or d['len'] < MINL: continue
            c = classify(D, d, T)
            agg[key][side + ':' + c] += 1; agg[key][side + ':' + c + '_len'] += d['len']
for key, c in sorted(agg.items()):
    n = c['n']
    for side in ('us', 'them'):
        items = sorted(k.split(':')[1] for k in c if k.startswith(side + ':') and not k.endswith('_len'))
        print(key, side, 'n=%d' % n, '  '.join('%s %.2f (%.0f)' % (k, c[side + ':' + k] / n, c[side + ':' + k + '_len'] / n) for k in items))
