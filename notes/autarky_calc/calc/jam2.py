"""Clumps: >=4 heads of a team within 3 of a mouth, pocket empty of that team. Count rounds + runs, both teams."""
from common import *
import collections
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']
    out = {}
    for T in 'AB':
        runs = []; cur = None; n = 0; ready = 0
        for r, S in g['rounds']:
            hit = None
            for p in range(4):
                near = [j for j, (h, L, t) in S['heads'].items() if t == T and pocket_of(h) is None and mdist(h, MOUTH[p]) <= 3]
                mine = any(any(pocket_of(s) == p for s in bd) for j, bd in S['bodies'].items() if S['heads'][j][2] == T)
                if len(near) >= 4 and not mine:
                    hit = p; n += 1
                    if sum(1 for t in S['pearls'] if pocket_of(t) == p) >= 2 and not any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): ready += 1
            if hit is not None:
                if cur and cur[1] == r - 1: cur[1] = r
                else:
                    cur = [r, r, hit]; runs.append(cur)
        out['calc' if T == c else 'opp'] = (n, ready, [tuple(x) for x in runs if x[1] - x[0] >= 2][:8])
    print(gm['gid'], gm['opp'][:8], 'calc clump-rounds %d (pocket free&>=2 pearls %d) long runs %s' % out['calc'])
    print('       opp  clump-rounds %d (free %d) long runs %s' % out['opp'])
