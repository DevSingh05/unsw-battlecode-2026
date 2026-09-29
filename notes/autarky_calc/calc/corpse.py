"""Corpse race: for each corpse pearl (dropped by any death), who eats it and how fast; conditioned on local head counts at the death."""
from common import *
import collections, statistics as st
for grp in ('US', 'oth'):
    acc = collections.defaultdict(collections.Counter); lat = collections.defaultdict(list)
    for gm in GAMES:
        if (gm['us'] is not None) != (grp == 'US'): continue
        g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
        # map corpse (dead id) -> eats
        eats_by = collections.defaultdict(list)
        for e in g['eats']:
            if e['corpse']: eats_by[e['corpse'][0]].append(e)
        for d in g['deaths']:
            if d['round'] > 350 or d['reason'] != 'HitHeadToHead' or pocket_of(d['head']) is not None: continue
            S = R.get(d['round'] - 1)
            if not S: continue
            h = d['head']
            nc = sum(1 for j, (hh, L, T) in S['heads'].items() if T == c and j != d['id'] and mdist(hh, h) <= 4)
            no = sum(1 for j, (hh, L, T) in S['heads'].items() if T != c and j != d['id'] and mdist(hh, h) <= 4)
            loc = 'calc>opp' if nc > no else ('even' if nc == no else 'calc<opp')
            dropped = (d['len'] + 1) // 2
            ev = eats_by.get(d['id'], [])
            k = ('calc corpse' if d['team'] == c else 'opp corpse', loc)
            acc[k]['dropped'] += dropped
            for e in ev:
                acc[k]['eaten by calc' if e['team'] == c else 'eaten by opp'] += 1
                lat[k[0] + (' by calc' if e['team'] == c else ' by opp')].append(e['round'] - d['round'])
    print('==', grp, '(deaths r<=350; local = heads within 4 of the dying head)')
    for k in sorted(acc):
        v = acc[k]; n = v['dropped']
        print('  %-12s local %-9s dropped %4d  eaten by calc %3.0f%%  by opp %3.0f%%' % (k[0], k[1], n, 100 * v['eaten by calc'] / n, 100 * v['eaten by opp'] / n))
    for k, v in sorted(lat.items()): print('  latency', k, 'median', st.median(v))
