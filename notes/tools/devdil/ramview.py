#!/usr/bin/env python3
"""For every ram WE initiated (we moved into an enemy head): exact board before our move, heads the bot
could see (Chebyshev <= 3 of our head), team units, and the corpse-pearl harvest that followed.
Buckets by what RAM_GUARD's local test would have said (others >= enemies-in-view incl. target).
    python3 notes/tools/devdil/ramview.py MAP"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1]
B = collections.defaultdict(lambda: collections.Counter())
out = []
for g in GS:
    if not g['map'].startswith(M): continue
    S = simulate(g['path']); us = g['us']; m = S['map']
    eaten = collections.defaultdict(collections.Counter)
    for e in S['eats']:
        if e['corpse']: eaten[e['corpse'][0]]['us' if e['team'] == us else 'them'] += 1
    for d in S['deaths']:
        if d['reason'] != 'HitHeadToHead' or 'victim' not in d or d['team'] != us or d['victim_team'] == us: continue
        st = simulate(g['path'], stop=(d['round'], d['id']))
        if 'act' not in st: continue
        me = st['body'][d['id']][0]
        others = sum(1 for j, b in st['body'].items() if j != d['id'] and st['team'][j] == us and m.cheb(b[0], me) <= 3)
        enem = sum(1 for j, b in st['body'].items() if st['team'][j] != us and m.cheb(b[0], me) <= 3)
        units = sum(1 for j in st['body'] if st['team'][j] == us)
        eunits = sum(1 for j in st['body'] if st['team'][j] != us)
        local_ok = others >= enem
        eu = eaten[d['id']]['us'] + eaten[d['victim']]['us']; et = eaten[d['id']]['them'] + eaten[d['victim']]['them']
        even = d['victim_len'] < d['len'] + 2
        key = ('W' if g['win'] else 'L', 'local_ok' if local_ok else 'local_OUT', 'units>=8' if units >= 8 else 'units<8')
        b = B[key]; b['n'] += 1; b['eu'] += eu; b['et'] += et; b['even'] += even
        out.append((g['game'], g['win'], d['round'], d['len'], d['victim_len'], others, enem, units, eunits, eu, et))
ng = collections.Counter('W' if g['win'] else 'L' for g in GS if g['map'].startswith(M))
print('bucket (result, local test, units)          rams/g   corpse pearls eaten per ram us/them   net')
for k in sorted(B):
    b = B[k]; n = b['n']
    print('%-40s %5.1f   %.2f / %.2f   %+.2f   (n=%d, even-trade share %.0f%%)' % (k, n / ng[k[0]], b['eu'] / n, b['et'] / n, (b['eu'] - b['et']) / n, n, 100 * b['even'] / n))
tot = collections.Counter()
for k, b in B.items():
    tot[k[1], 'n'] += b['n']; tot[k[1], 'eu'] += b['eu']; tot[k[1], 'et'] += b['et']
for lk in ('local_ok', 'local_OUT'):
    n = tot[lk, 'n']
    if n: print('ALL %-9s n=%d  us %.2f them %.2f net %+.2f' % (lk, n, tot[lk, 'eu'] / n, tot[lk, 'et'] / n, (tot[lk, 'eu'] - tot[lk, 'et']) / n))
pickle.dump(out, open(os.path.join(HERE, 'ramview_%s.pkl' % M[:3]), 'wb'))
