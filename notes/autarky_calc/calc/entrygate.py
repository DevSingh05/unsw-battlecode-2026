"""Calc entry gate: for calc heads adjacent to (<=1 from) a ready, empty pocket mouth, P(enter next move) by nearest enemy head distance to the mouth, and own diver/queue state."""
from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
for grp in ('calc', 'US'):
    A = collections.defaultdict(lambda: [0, 0])
    for gm in GAMES:
        if grp == 'US' and gm['us'] is None: continue
        g = sim(gm['gid']); R = dict(g['rounds']); c = gm['calc']
        starts = {(e['r0'], e['id']) for e in E if e['gid'] == gm['gid']}
        for mv in g['moves']:
            T = mv['team']
            if (T == c) != (grp == 'calc'): continue
            S = R.get(mv['round'] - 1)
            if not S: continue
            h = mv['head']
            for p in range(4):
                if h != MOUTH[p]: continue   # standing ON the mouth tile, pocket tile is 1 step in
                if any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): continue
                pe = sum(1 for t in S['pearls'] if pocket_of(t) == p)
                if pe < 2: continue
                en = min((mdist(hh, MOUTH[p]) for (hh, L, TT) in S['heads'].values() if TT != T), default=99)
                b = str(en) if en <= 7 else '8+'
                A[b][0] += 1; A[b][1] += (mv['round'], mv['id']) in starts
    print(grp, 'head on mouth tile, pocket empty & >=2 pearls: P(enter) by nearest enemy head dist to mouth')
    for k in sorted(A, key=lambda x: (len(x), x)):
        n, y = A[k]; print('   enemy d=%s: n=%d enter %.0f%%' % (k, n, 100 * y / n))
