#!/usr/bin/env python3
"""Value of head-on rams: for each cross-team head-to-head (mover = rammer), who eats the
pearls both corpses drop (within 30 rounds), plus unit counts at the time. Also how our
last dragons die in elimination losses.
    python3 notes/tools/ram_value.py
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
G = collections.defaultdict(lambda: collections.Counter())
lastd = collections.Counter()
for s in summ:
    key = 'W' if s['win'] else ('L-elim' if s['end'] == 'teamEliminated' else 'L-round')
    us = s['side']
    g = simulate(os.path.join(DIR, f"{s['id']}.replay"))
    snap = dict(g['rounds'])
    deaths = g['deaths']
    pair_of = {}
    for i, d in enumerate(deaths):
        if d['reason'] == 'HitHeadToHead' and 'victim' in d and d['victim_team'] != d['team']:
            ram = 'us' if d['team'] == us else 'them'
            pair_of[d['id']] = (ram, d['round']); pair_of[d['victim']] = (ram, d['round'])
            sn = snap.get(d['round'] - 1) or snap[min(snap)]
            nu, nt = sn[us]['n'], sn['B' if us == 'A' else 'A']['n']
            G[key][f'{ram}_rams'] += 1
            G[key][f'{ram}_rams_' + ('ahead' if (nu > nt) == (ram == 'us') else 'behind_or_even')] += 1
    for e in g['eats']:
        c = e['corpse']
        if c and c[0] in pair_of:
            ram, r = pair_of[c[0]]
            if e['round'] - r <= 30:
                G[key][f'{ram}_ram_pearls_eaten_by_' + ('us' if e['team'] == us else 'them')] += 1
    # last 3 deaths of our team in eliminations
    if key == 'L-elim':
        ours = [d for d in deaths if d['team'] == us][-5:]
        for d in ours:
            r = d['reason']
            if r == 'HitHeadToHead':
                r += '-' + ('rammed-by-them' if 'killer' in d and d['killer_team'] != us else ('we-rammed' if 'victim' in d and d['victim_team'] != us else 'friendly'))
            lastd[r] += 1
for k, c in G.items():
    n = sum(1 for s in summ if ('W' if s['win'] else ('L-elim' if s['end'] == 'teamEliminated' else 'L-round')) == k)
    print(k, {a: round(b / n, 1) for a, b in sorted(c.items())})
print('our last 5 deaths in elim losses:', dict(lastd))
