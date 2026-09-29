"""Decision points for a diver inside a pocket with L>=4: split or move? Features: depth, L, pearls deeper than head, pocket occupancy."""
from common import *
import collections, sys
PKT = pockets()
res = collections.Counter()
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
    acts = {}
    for mv in g['moves']: acts[(mv['round'], mv['id'])] = ('move', mv)
    for s in g['splits']: acts[(s['round'], s['parent'])] = ('split', s)
    for (r, i), (k, x) in acts.items():
        S = R.get(r - 1)
        if not S or i not in S['bodies']: continue
        bd = S['bodies'][i]; h = bd[0]; p = pocket_of(h)
        if p is None or len(bd) < 4: continue
        T = S['heads'][i][2]
        who = 'calc' if T == c else ('US' if gm['us'] else 'oth')
        d = PKT[h]
        deeper = [t for t in S['pearls'] if pocket_of(t) == p and PKT[t] < d]
        tail_out = sum(1 for s in bd if pocket_of(s) is None)
        # pearls that will spawn? ignore
        a = 'split%d' % x['k'] if k == 'split' else 'move'
        res[(who, len(bd), d, len(deeper), tail_out, a)] += 1
for who in ('calc', 'US', 'oth'):
    print('==', who, ' (L, depth, pearls deeper, segs outside pocket) -> action counts')
    keys = sorted(set(k[1:5] for k in res if k[0] == who))
    for kk in keys:
        acts = {k[5]: v for k, v in res.items() if k[0] == who and k[1:5] == kk}
        if sum(acts.values()) >= 3: print('  L%d depth%d deeper=%d out=%d  %s' % (kk + (acts,)))
