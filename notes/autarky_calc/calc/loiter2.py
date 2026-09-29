"""Rounds a diver spent within 2 of the mouth while the pocket was empty+ready, before entering (scan back until it was >4 away)."""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
def ready(S, p):
    if any(any(pocket_of(s) == p for s in bd) for bd in S['bodies'].values()): return False
    return sum(1 for t in S['pearls'] if pocket_of(t) == p) >= 3
out = collections.defaultdict(list)
for gm in GAMES:
    g = sim(gm['gid']); R = dict(g['rounds'])
    homes = {}
    for t, pts in g['map'].dragons:
        if len(pts) >= 10: homes['AB'[t]] = [p for p in range(4) if abs(MOUTH[p][0] - pts[0][0]) <= 1]
    X = sorted([e for e in E if e['gid'] == gm['gid']], key=lambda e: e['r0'])
    prev_team = {}
    for e in X:
        n = 0; enemy_near_rounds = 0
        for r in range(e['r0'] - 1, max(0, e['r0'] - 60), -1):
            S = R.get(r)
            if not S or e['id'] not in S['heads']: break
            h = S['heads'][e['id']][0]
            if mdist(h, MOUTH[e['p']]) > 4: break
            if mdist(h, MOUTH[e['p']]) <= 2 and ready(S, e['p']):
                n += 1
                if any(T != e['team'] and mdist(hh, MOUTH[e['p']]) <= 4 for (hh, L, T) in S['heads'].values()): enemy_near_rounds += 1
        who = 'calc' if e['calc'] else ('US' if e['vsus'] else 'oth')
        where = 'home' if e['p'] in homes[e['team']] else 'away'
        takeover = prev_team.get(e['p']) not in (None, e['team'])
        prev_team[e['p']] = e['team']
        out[(who, where, 'takeover' if takeover else 'continuing')].append((n, enemy_near_rounds))
for k in sorted(out):
    v = out[k]
    print(k, 'dives', len(v), 'loiter mean %.2f' % st.mean(a for a, b in v), ' >=4 rounds: %.0f%%' % (100 * sum(a >= 4 for a, b in v) / len(v)), ' mean loiter-rounds with enemy head<=4: %.2f' % st.mean(b for a, b in v))
