"""Non-ram deaths r100-320 per game: trapped (0 free nbrs) vs voluntary (>=1 free), in pocket vs open, len; and whether the
corpse was eaten by own team (share, rounds). Usage: churn.py [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
maps = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
gm = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us', 'us31': 'u31'}
C = collections.defaultdict(collections.Counter); ng = collections.Counter()
bp = collections.defaultdict(list)
for x in collect.games():
    if x['grp'] in gm and (not maps or x['map'] in maps): bp[x['path']].append(x)
for p, its in bp.items():
    g = sim2.simulate(p); PK = collect.pockets(g['map'])
    ate = collections.defaultdict(collections.Counter)
    for e in g['eats']:
        if e['corpse'] is not None: ate[e['corpse'][0]][e['team']] += 1
    for it in its:
        k = gm[it['grp']]; T = collect.side(it, g); ng[k] += 1
        for d in g['deaths']:
            if d['team'] != T or not (100 <= d['round'] <= 320) or d['reason'] == 'HitHeadToHead': continue
            fr = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
            key = ('trapped' if fr == 0 else 'free%d' % min(fr, 2)) + ('-pk' if d['head'] in PK else '-open')
            C[k][key] += 1; C[k]['ALL'] += 1; C[k]['len_' + key] += d['len']
            C[k]['drop'] += (d['len'] + 1) // 2; C[k]['own_eat'] += ate[d['id']][T]; C[k]['en_eat'] += ate[d['id']]['AB'.replace(T, '')]
for k in C:
    n = ng[k]
    print(k, 'games', n, {kk: round(v / n, 1) for kk, v in sorted(C[k].items()) if not kk.startswith('len_')})
    print('   mean len', {kk[4:]: round(C[k][kk] / max(1, C[k][kk[4:]]), 2) for kk in sorted(C[k]) if kk.startswith('len_')})
