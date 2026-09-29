from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
agg = collections.Counter()
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; last = g['last_round']
    own = collections.Counter(); dv = collections.Counter(); eat = collections.Counter()
    for p in range(4):
        X = sorted([e for e in E if e['gid'] == gm['gid'] and e['p'] == p], key=lambda e: e['r0'])
        cur = None; i = 0
        for r in range(1, last + 1):
            while i < len(X) and X[i]['r0'] <= r:
                cur = 'calc' if X[i]['calc'] else 'opp'; dv[cur] += 1; i += 1
            if cur: own[cur] += 1
    for e_ in g['eats']:
        if pocket_of(e_['tile']) is not None: eat['calc' if e_['team'] == c else 'opp'] += 1
    tot = own['calc'] + own['opp']
    grp = 'US' if gm['us'] else 'oth'
    for k in ('calc', 'opp'):
        agg[(grp, k, 'own')] += own[k]; agg[(grp, k, 'dv')] += dv[k]; agg[(grp, k, 'eat')] += eat[k]
    print('%d %-10s pocket-rounds owned calc %.0f%%  dives/100 owned rounds calc %.1f opp %.1f  pocket eats per owned round calc %.2f opp %.2f' % (gm['gid'], gm['opp'][:10], 100 * own['calc'] / tot, 100 * dv['calc'] / max(1, own['calc']), 100 * dv['opp'] / max(1, own['opp']), eat['calc'] / max(1, own['calc']), eat['opp'] / max(1, own['opp'])))
for grp in ('US', 'oth'):
    print(grp, 'dives/100 owned: calc %.1f opp %.1f ; eats/owned round calc %.2f opp %.2f' % (100 * agg[(grp, 'calc', 'dv')] / agg[(grp, 'calc', 'own')], 100 * agg[(grp, 'opp', 'dv')] / agg[(grp, 'opp', 'own')], agg[(grp, 'calc', 'eat')] / agg[(grp, 'calc', 'own')], agg[(grp, 'opp', 'eat')] / agg[(grp, 'opp', 'own')]))
