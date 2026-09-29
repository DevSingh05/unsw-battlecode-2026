"""Head-on collisions and body kills near pocket mouths vs elsewhere, by initiator team."""
from common import *
import collections
tot = collections.Counter()
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']
    homes = {}
    for t, pts in g['map'].dragons:
        if len(pts) >= 10: homes['AB'[t]] = [p for p in range(4) if abs(MOUTH[p][0] - pts[0][0]) <= 1]
    cnt = collections.Counter()
    for d in g['deaths']:
        if d['reason'] == 'HitHeadToHead' and d.get('killer') is not None and d['killer_team'] != d['team']:
            # victim record (not actor)
            near = [p for p in range(4) if mdist(d['head'], MOUTH[p]) <= 4]
            where = 'open'
            if near:
                p = near[0]; where = 'calcHomeMouth' if p in homes[c] else 'oppHomeMouth'
            ini = 'calc' if d['killer_team'] == c else 'opp'
            cnt[(ini, where)] += 1
            if gm['us']: tot[(ini, where)] += 1
    print(gm['gid'], gm['opp'][:10], dict(sorted(cnt.items())))
print('vs US total (initiator, where):', dict(sorted(tot.items())))
