"""Per head-on corpse pearl: nearest calc head vs nearest opp head distance at drop; who eats it (or nobody within 20 rounds)."""
from common import *
import collections
for grp in ('US', 'oth'):
    acc = collections.defaultdict(collections.Counter)
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'US'): continue
        g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
        eat_at = {}
        for e in g['eats']:
            if e['corpse']: eat_at[(e['corpse'][0], e['tile'])] = e
        for d in g['deaths']:
            if d['round'] > 350 or d['reason'] != 'HitHeadToHead' or pocket_of(d['head']) is not None: continue
            S = R.get(d['round'])  # end of death round
            if not S: continue
            for t in d['body'][::2]:
                dc = min((mdist(hh, t) for j, (hh, L, T) in S['heads'].items() if T == c), default=99)
                do = min((mdist(hh, t) for j, (hh, L, T) in S['heads'].items() if T != c), default=99)
                k = 'calc nearer' if dc < do else ('tie' if dc == do else 'opp nearer')
                e = eat_at.get((d['id'], t))
                w = 'none' if not e else ('calc' if e['team'] == c else 'opp')
                acc[k][w] += 1
    print(grp)
    for k, v in acc.items():
        n = sum(v.values()); print('  ', k, n, {a: '%.0f%%' % (100 * b / n) for a, b in v.items()})
