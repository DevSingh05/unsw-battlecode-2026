"""Pump-cycle yield per team in local replays (same method as jam/cycles.py).  python3 selfcycles.py REPLAY TEAM_A_NAME TEAM_B_NAME"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../jam'))
from common import *
path_, names = sys.argv[1], {'A': sys.argv[2], 'B': sys.argv[3]}
S = simj.simulate(path_); PK = pockets(S['map']); R = dict(S['rounds'])
ate = collections.Counter((e['id'], e['round']) for e in S['eats'] if e['tile'] in PK)
splits = collections.defaultdict(list)
for s in S['splits']: splits[(s['parent'], s['round'])].append(s['k'])
deaths = {d['id']: d for d in S['deaths']}
res = {T: [] for T in 'AB'}; prevhead = {}; peat = collections.Counter()
for e in S['eats']:
    if e['tile'] in PK: peat[e.get('team') or '?'] += 1
for r in sorted(R):
    for j, (t, L, T) in R[r]['heads'].items():
        p = prevhead.get(j)
        if t in PK and p is not None and p not in PK:
            entry = L - ate[(j, r)]; kids = []; out = None; rr = r
            while True:
                kids += splits.get((j, rr), []); st = R.get(rr)
                if st is None or j not in st['heads']: out = ('died', 0); break
                if st['heads'][j][0] not in PK: out = ('out', st['heads'][j][1]); break
                rr += 1
                if rr > r + 30: out = ('stuck', 0); break
            res[T].append((entry, tuple(kids), out[0], sum(kids) + (out[1] if out[0] == 'out' else 0) - entry))
    prevhead = {j: v[0] for j, v in R[r]['heads'].items()}
last = R[max(R)]
for T in 'AB':
    xs = res[T]; n = len(xs) or 1
    print('%-9s dives %3d net/dive %+.2f total %+4d  final units %2d total len %3d  shapes %s' % (
        names[T], len(xs), sum(x[3] for x in xs) / n, sum(x[3] for x in xs), last[T]['n'], last[T]['total'],
        collections.Counter((e, k) for e, k, o, _ in xs).most_common(3)))
