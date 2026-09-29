#!/usr/bin/env python3
"""Rounds where a team's longest dragon length drops by >= 4 (king death, cascade, big split).
    python3 notes/tools/porsli/drops.py Portals|Slithery [v28|old|all]
Prints each drop (round, max before -> after, and what happened: deaths of L>=6 / splits of the longest that round)."""
import collections, json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
sys.path.insert(0, os.path.dirname(__file__))
from collect import classify
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
from board import path_of
tot = {k: collections.Counter() for k in ('LOSS', 'WIN')}; n = collections.Counter()
for g in sorted(gs, key=lambda g: (g['win'], g['game'])):
    S = simulate(path_of(g['game']))
    grp = 'WIN' if g['win'] else 'LOSS'; n[grp] += 1
    for tag, T in (('us', g['side']), ('them', 'B' if g['side'] == 'A' else 'A')):
        prev = None; out = []
        for rn, sn in S['rounds']:
            mx = sn[T]['max']
            if prev is not None and prev - mx >= 4 and rn >= 250:
                ds = [d for d in S['deaths'] if d['round'] == rn and d['team'] == T and d['len'] >= 6]
                why = ','.join('L%d:%s' % (d['len'], classify(S, d)) for d in ds)
                nsp = sum(1 for s in S['splits'] if s['round'] == rn and s['team'] == T and s['L'] >= 8)
                out.append('r%d %d->%d [%s%s]' % (rn, prev, mx, why, ' splits%d' % nsp if nsp else ''))
                tot[grp][tag + '_n'] += 1; tot[grp][tag + '_len'] += prev - mx
                c = ds[0] and classify(S, max(ds, key=lambda d: d['len'])) if ds else 'split-only'
                tot[grp][tag + ':' + c] += prev - mx
            prev = mx
        if tag == 'us' or out:
            print(g['game'], grp[0], tag, g['opp'][:12], ' | '.join(out))
for grp in ('LOSS', 'WIN'):
    if n[grp]:
        print('==', grp, n[grp], {k: round(v / n[grp], 2) for k, v in sorted(tot[grp].items())})
