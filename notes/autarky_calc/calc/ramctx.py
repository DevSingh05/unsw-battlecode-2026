from common import *
import collections, statistics as st
for grp in ('us', 'oth'):
    ctx = collections.defaultdict(list)
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'us'): continue
        g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
        for d in g['deaths']:
            if d['reason'] == 'HitHeadToHead' and d.get('killer') is not None and d['killer_team'] != d['team']:
                S = R.get(d['round'] - 1)
                if not S: continue
                K = d['killer_team']; h = d['head']
                own = sum(1 for j, (hh, L, T) in S['heads'].items() if T == K and mdist(hh, h) <= 5) - 1
                en = sum(1 for j, (hh, L, T) in S['heads'].items() if T != K and mdist(hh, h) <= 5) - 1
                uK = sum(1 for v in S['heads'].values() if v[2] == K); uV = sum(1 for v in S['heads'].values() if v[2] != K)
                ctx['calc' if K == c else 'opp'].append((own, en, uK, uV, d['round']))
    for k, v in ctx.items():
        print(grp, k, 'initiated', len(v), 'own heads within5 (excl) mean %.2f, enemy within5 (excl victim) %.2f; local ahead %.0f%% even %.0f%% behind %.0f%%; global units ahead %.0f%%' % (
            st.mean(a for a, b, c_, d_, r in v), st.mean(b for a, b, c_, d_, r in v), 100 * sum(a > b for a, b, *_ in v) / len(v), 100 * sum(a == b for a, b, *_ in v) / len(v), 100 * sum(a < b for a, b, *_ in v) / len(v), 100 * sum(c_ > d_ for a, b, c_, d_, r in v) / len(v)))
