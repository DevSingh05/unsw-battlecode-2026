"""Hesitation: pocket empty & >=3 pearls ('ready'), team has >=1 L<=3 head within 2 of the mouth, and no dive starts next round."""
from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
tot = collections.Counter()
for gm in GAMES:
    g = sim(gm['gid']); R = dict(g['rounds']); c = gm['calc']
    starts = {(e['r0'], e['p']) for e in E if e['gid'] == gm['gid']}
    cnt = collections.Counter()
    for r, S in g['rounds']:
        for p in range(4):
            if any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): continue
            if sum(1 for t in S['pearls'] if pocket_of(t) == p) < 3: continue
            for T in 'AB':
                k = sum(1 for j, (h, L, t) in S['heads'].items() if t == T and mdist(h, MOUTH[p]) <= 2)
                if k == 0: continue
                who = 'calc' if T == c else 'opp'
                cnt[(who, 'ready rounds w/ own head<=2')] += 1
                if (r + 1, p) not in starts:
                    cnt[(who, 'no entry next round')] += 1
                    if k >= 2: cnt[(who, 'no entry, >=2 own heads<=2')] += 1
                    if k >= 3: cnt[(who, 'no entry, >=3 own heads<=2')] += 1
    print(gm['gid'], gm['opp'][:10], ' '.join('%s:%s=%d' % (a, b, v) for (a, b), v in sorted(cnt.items())))
