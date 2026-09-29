"""P(ram) for a head that starts its turn with an enemy head at Manhattan 1 or 2, by team and global unit ratio."""
from common import *
import collections
for grp in ('us', 'oth'):
    A = collections.defaultdict(lambda: [0, 0])
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'us'): continue
        g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
        rammed = {(d['round'], d['killer']) for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d.get('killer') is not None and d['killer_team'] != d['team']}
        for mv in g['moves']:
            S = R.get(mv['round'] - 1)
            if not S or mv['id'] not in S['heads']: continue
            h, L, T = S['heads'][mv['id']]
            if L > 4: continue
            dmin = min((mdist(h, hh) for j, (hh, LL, TT) in S['heads'].items() if TT != T), default=99)
            if dmin > 2: continue
            uK = sum(1 for v in S['heads'].values() if v[2] == T); uV = sum(1 for v in S['heads'].values() if v[2] != T)
            ratio = uK / max(1, uV)
            b = '<0.8' if ratio < 0.8 else ('0.8-1.25' if ratio <= 1.25 else ('1.25-2' if ratio <= 2 else '>2'))
            who = 'calc' if T == c else 'opp'
            A[(who, dmin, b)][0] += 1
            if (mv['round'], mv['id']) in rammed: A[(who, dmin, b)][1] += 1
    for k in sorted(A):
        n, r = A[k]
        if n >= 20: print(grp, k, 'n=%d ram=%.1f%%' % (n, 100 * r / n))
