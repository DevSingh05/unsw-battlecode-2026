"""Pump cycles in these 4 games, both teams: a head steps from outside onto a pocket tile (entry L); follow that dragon while it is
in the pocket: pearls eaten, splits (child L), end (death L or walked out L). net = sum(child L) + (L out if it walks out) - entry L."""
import collections
from common import *
for g in GAMES:
    S = sim(g); PK = S['PK']; us = GAMES[g]
    R = dict(S['rounds'])
    ate = collections.Counter((e['id'], e['round']) for e in S['eats'] if e['tile'] in PK)
    splits = collections.defaultdict(list)
    for s in S['splits']: splits[(s['parent'], s['round'])].append(s['k'])
    deaths = {d['id']: d for d in S['deaths']}
    res = {T: [] for T in 'AB'}
    prevhead = {}
    for r in sorted(R):
        for j, (t, L, T) in R[r]['heads'].items():
            p = prevhead.get(j)
            if t in PK and p is not None and p not in PK:
                # entry at round r with length before = L - ate
                entry = L - ate[(j, r)]
                kids = []; out = None; eats = 0; rr = r; last = None
                while True:
                    eats += ate[(j, rr)]
                    kids += splits.get((j, rr), [])
                    st = R.get(rr)
                    if st is None or j not in st['heads']:
                        out = ('died', deaths[j]['len'] if j in deaths else 0); break
                    if st['heads'][j][0] not in PK:
                        out = ('out', st['heads'][j][1]); break
                    rr += 1
                    if rr > r + 30: out = ('stuck', 0); break
                net = sum(kids) + (out[1] if out[0] == 'out' else 0) - entry
                res[T].append((entry, tuple(kids), out, net))
        prevhead = {j: v[0] for j, v in R[r]['heads'].items()}
    for T in (us, 'B' if us == 'A' else 'A'):
        xs = res[T]; n = len(xs)
        if not n: continue
        shapes = collections.Counter((e, k, o[0], o[1]) for e, k, o, _ in xs)
        print(g, 'us  ' if T == us else 'calc', 'dives %3d  net/dive %+.2f  total %+d  died-inside %.0f%%  top shapes %s' % (
            n, sum(x[3] for x in xs) / n, sum(x[3] for x in xs), 100.0 * sum(1 for x in xs if x[2][0] == 'died') / n,
            shapes.most_common(4)))
