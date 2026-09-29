"""For each dive, how many rounds the diver hovered adjacent to the mouth (dist<=1) while the pocket was empty & full, before entering."""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
def ready(S, p):
    if any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): return False
    return sum(1 for t in S['pearls'] if pocket_of(t) == p) >= 3
out = collections.defaultdict(list)
for gm in GAMES:
    g = sim(gm['gid']); R = dict(g['rounds'])
    for e in [e for e in E if e['gid'] == gm['gid']]:
        n = 0
        for r in range(e['r0'] - 1, max(0, e['r0'] - 40), -1):
            S = R.get(r)
            if not S or e['id'] not in S['heads']: break
            h = S['heads'][e['id']][0]
            if mdist(h, MOUTH[e['p']]) <= 1 and ready(S, e['p']): n += 1
            elif mdist(h, MOUTH[e['p']]) > 3: break
        out[('calc' if e['calc'] else ('US' if e['vsus'] else 'oth'), e['vsus'])].append(n)
for k, v in out.items():
    print(k, 'dives', len(v), 'loiter rounds mean %.2f' % st.mean(v), 'dist', sorted(collections.Counter(min(x, 10) for x in v).items()))
