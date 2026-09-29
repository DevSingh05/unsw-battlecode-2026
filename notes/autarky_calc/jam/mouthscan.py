"""Per round: our heads within BFS<=3 of each mouth / inside the pocket, pocket pearls, eats in pocket by us/them."""
import sys, collections
from common import *
from jtl import mouths, bfsd
g = int(sys.argv[1]); thr = int(sys.argv[2]) if len(sys.argv) > 2 else 3
S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
MO = mouths(m, PK); MD = [bfsd(m, x, 3) for x in MO]
pocket_of = {u: min(range(len(MO)), key=lambda i: m.dist(u, MO[i])) for u in PK}
R = dict(S['rounds'])
pe = collections.Counter()
for e in S['eats']:
    if e['tile'] in PK: pe[(e['round'], pocket_of[e['tile']], e['team'] == us)] += 1
for r in sorted(R):
    for i, D in enumerate(MD):
        H = {j: (t, L) for j, (t, L, T) in R[r]['heads'].items() if T == us and (t in D or pocket_of.get(t) == i)}
        E = {j: (t, L) for j, (t, L, T) in R[r]['heads'].items() if T != us and (t in D or pocket_of.get(t) == i)}
        if len(H) >= thr:
            pp = sorted(p for p in R[r]['pearls'] if pocket_of.get(p) == i)
            print('r%d mouth%s us=%d %s | them=%d %s | pocket pearls %s | eats us/them %d/%d' % (r, MO[i], len(H), ' '.join('%d@%s L%d' % (j, t, L) for j, (t, L) in sorted(H.items())), len(E), ' '.join('%d@%s' % (j, t) for j, (t, L) in sorted(E.items())), pp, pe[(r, i, True)], pe[(r, i, False)]))
