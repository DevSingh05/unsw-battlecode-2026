"""Mouth blocking: share of pocket-owned rounds where the mouth tile / its 3 outside neighbours hold owner segments."""
from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
m = realmap()
acc = collections.defaultdict(collections.Counter)
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']
    X = sorted([e for e in E if e['gid'] == gm['gid']], key=lambda e: e['r0'])
    owner = {}; xi = 0
    for r, S in g['rounds']:
        while xi < len(X) and X[xi]['r0'] <= r:
            owner[X[xi]['p']] = X[xi]['team']; xi += 1
        occ = {}
        for j, bd in S['bodies'].items():
            for s in bd: occ[s] = S['heads'][j][2]
        for p, T in owner.items():
            who = 'calc' if T == c else ('US' if gm['us'] else 'oth')
            M = MOUTH[p]
            nb = [m.step(M, d) for d in 'NESW']; nb = [t for t in nb if t is not None and pocket_of(t) is None]
            k = sum(1 for t in nb if occ.get(t) == T)
            enemy_close = any(t != T and mdist(h, M) <= 4 for (h, L, t) in S['heads'].values())
            key = who + (' enemy<=4' if enemy_close else ' no enemy')
            acc[key]['n'] += 1; acc[key]['mouth own-seg'] += occ.get(M) == T; acc[key]['>=2 of 3 approach tiles own-seg'] += k >= 2
            acc[key]['all approach own-seg'] += k == len(nb)
for k, v in sorted(acc.items()):
    n = v['n']; print(k, n, {a: '%.0f%%' % (100 * b / n) for a, b in v.items() if a != 'n'})
