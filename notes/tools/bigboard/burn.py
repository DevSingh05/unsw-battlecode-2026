#!/usr/bin/env python3
"""Decompose self-inflicted deaths (the 'burn') by life story (notes/23).  python3 notes/tools/bigboard/burn.py
stillborn: split child that dies at age<=3 ; pump-parent: died <=5 rounds after its own split ;
young: age 4-15 ; feed: feed_* class ; old: rest.  Net cost per death = len - own re-eaten pearls."""
import collections, os, pickle
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, 'deathctx.pkl'), 'rb'))
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']
def selfinf(c): return not (c.startswith('rammed') or c.startswith('ram_enemy') or c == 'killed_other')
def story(d):
    if d['cls'].startswith('feed'): return 'feed'
    if d['born_by_split'] and d['age'] <= 3: return 'stillborn'
    if d['split5'] is not None: return 'pump-parent'
    if d['age'] <= 15: return 'young'
    return 'old'
K = ['stillborn', 'pump-parent', 'young', 'old', 'feed']
for grp, maps in (('BIG', BIG), ('STRONG', STRONG)) + tuple((m, [m]) for m in BIG + STRONG):
    for wl in (None, False):
        gs = [g for g in R if g['map'] in maps and (wl is None or g['win'] == wl)]; n = len(gs)
        if not n: continue
        row = []
        for tag in ('us', 'them'):
            c = collections.Counter(); cost = collections.Counter()
            for g in gs:
                for d in g['deaths']:
                    if d['tag'] != tag or not selfinf(d['cls']) or d['round'] >= 350: continue
                    s = story(d); c[s] += 1; cost[s] += d['len'] - d['own_re']
            row.append(c); row.append(cost)
        print('%-16s %-5s n=%2d r0-349 deaths/g (net cost/g) us | them:  %s' % (grp, 'all' if wl is None else 'L', n,
              '  '.join('%s %.0f(%.0f)|%.0f(%.0f)' % (k, row[0][k] / n, row[1][k] / n, row[2][k] / n, row[3][k] / n) for k in K)))
