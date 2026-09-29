"""Idle-while-ready runs: pocket empty (no segment of anyone), >=3 pearls, and >=1 head of team T within 2 of the mouth.
Run = consecutive such rounds; ends when someone enters. Report per team the distribution of run lengths and who ends it."""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
for grp in ('US', 'oth'):
    L = collections.defaultdict(list); ender = collections.Counter()
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'US'): continue
        g = sim(gm['gid']); c = gm['calc']
        starts = {}
        for e in E:
            if e['gid'] == gm['gid']: starts[(e['r0'], e['p'])] = e['team']
        for T in 'AB':
            who = 'calc' if T == c else grp
            for p in range(4):
                run = 0
                for r, S in g['rounds']:
                    empty = not any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values())
                    ok = empty and sum(1 for t in S['pearls'] if pocket_of(t) == p) >= 3 and any(t == T and mdist(h, MOUTH[p]) <= 2 for (h, LL, t) in S['heads'].values())
                    if ok: run += 1
                    elif run:
                        L[who].append(run); run = 0
                    if (r + 1, p) in starts and run:
                        L[who].append(run); ender[(who, 'self' if starts[(r + 1, p)] == T else 'enemy')] += 1; run = 0
    for k, v in L.items():
        print(grp, k, 'runs', len(v), 'mean %.2f' % st.mean(v), 'dist', sorted(collections.Counter(min(x, 8) for x in v).items()), 'rounds wasted total/game %.0f' % (sum(x - 1 for x in v) / (4 if grp == 'US' else 9)))
    print(grp, 'ended by', dict(ender))
