"""After a pump split: is the child's exit path clear? Count own heads/segments on the tiles within 2 of the mouth outside the pocket at the split round, and rounds until the next diver can enter."""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
m = realmap()
for grp in ('calc', 'US', 'oth'):
    blk = collections.Counter(); n = 0; col = []
    for gm in GAMES:
        g = sim(gm['gid']); R = dict(g['rounds'])
        for e in E:
            if e['gid'] != gm['gid'] or e['end'] != 'split': continue
            if ('calc' if e['calc'] else ('US' if e['vsus'] else 'oth')) != grp: continue
            S = R.get(e['r1'])
            if not S: continue
            n += 1
            M = MOUTH[e['p']]; out = 1 if M[1] < 9 else -1
            col_t = [(M[0], M[1] + out * k) for k in (1, 2)]
            occ = {}
            for j, bd in S['bodies'].items():
                for i, s in enumerate(bd): occ[s] = (j, i == 0)
            own_col = sum(1 for t in col_t if t in occ and S['heads'][occ[t][0]][2] == e['team'] and occ[t][0] != e['child'] and occ[t][0] != e['id'])
            blk[own_col] += 1
    print(grp, 'splits', n, 'own OTHER segments on the 2 tiles straight out of the mouth at split time:', {k: '%.0f%%' % (100 * v / n) for k, v in sorted(blk.items())})
