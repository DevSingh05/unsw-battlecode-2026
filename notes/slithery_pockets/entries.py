#!/usr/bin/env python3
"""Every dead-end pocket entry by each team in a set of games: length in, pearls eaten inside,
outcome (exited / split inside / died inside) and length at death. Pockets = tiles removed by
leaf-pruning the static tile graph (notes/tools/midgame/pockets.py)."""
import sys, json, collections, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = set(); q = [t for t, d in deg.items() if d <= 1]
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem.add(t)
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq
    return rem
games = [(int(a), b) for a, b in (x.split(':') for x in sys.argv[1:])]
agg = {'us': collections.Counter(), 'them': collections.Counter()}
lens_dead = {'us': collections.Counter(), 'them': collections.Counter()}
for gid, us in games:
    G = simulate(os.path.join(ROOT, f'replays/auto/games/{gid}.replay')); m = G['map']; pk = pockets(m)
    last = {}  # id -> (inside?, entry record)
    open_e = {}
    deaths = {d['id']: d for d in G['deaths']}
    for mv in G['moves']:
        i = mv['id']; who = 'us' if mv['team'] == us else 'them'
        h0 = mv['head']; h1 = mv.get('head_after')
        if h1 is None: continue
        if h0 not in pk and h1 in pk:
            open_e[i] = {'who': who, 'r': mv['round'], 'len': mv['len_before'], 'ate': 0}
            agg[who]['entries'] += 1; agg[who]['len_in_sum'] += mv['len_before']
        elif i in open_e and h1 in pk:
            open_e[i]['ate'] += mv['ate']
        elif i in open_e and h1 not in pk:
            e = open_e.pop(i); agg[who]['exited'] += 1; agg[who]['ate_sum'] += e['ate'] + mv['ate']
    for s in G['splits']:
        e = open_e.get(s['parent'])
        if e: agg[e['who']]['split_inside'] += 1
    for i, e in open_e.items():
        d = deaths.get(i); who = e['who']
        if d and d['head'] in pk:
            agg[who]['died_inside'] += 1; agg[who]['ate_sum'] += e['ate']; lens_dead[who][min(d['len'], 8)] += 1
            if e['ate'] == 0: agg[who]['died_inside_ate0'] += 1
        else:
            agg[who]['other_end'] += 1
    for who in agg: agg[who]['games'] += 1 if who == 'us' else 0
n = len(games)
for who in ('us', 'them'):
    a = agg[who]; E = max(1, a['entries'])
    print(f"{who:5s} entries/g {a['entries']/n:5.1f} avgLenIn {a['len_in_sum']/E:4.2f} exited {a['exited']/n:5.1f} died_inside/g {a['died_inside']/n:5.1f} (ate nothing: {a['died_inside_ate0']/n:4.1f}) splits_inside/g {a['split_inside']/n:5.1f} pearls/entry {a['ate_sum']/E:4.2f}  death-len dist {dict(sorted(lens_dead[who].items()))}")
