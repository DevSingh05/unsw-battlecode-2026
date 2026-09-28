import json, os, sys, collections, pickle
import analyze as A, sim2
items = [x for x in A.games() if x[2] in ('Default', 'Autarky')]
res = {(r['gid'], r['grp']): r for r in pickle.load(open('metrics.pkl', 'rb'))}
C = collections.defaultdict(collections.Counter); N = collections.Counter()
cache = {}
for it in items:
    p, gid, mp, T, grp = it[:5]
    r = res.get((gid, grp))
    if not r: continue
    T = r['T']
    if p not in cache: cache.clear(); cache[p] = sim2.simulate(p)
    g = cache[p]; N[(mp, grp)] += 1
    for d in g['deaths']:
        if d['team'] != T or not (60 <= d['round'] <= 320): continue
        free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        key = d['reason']
        if key == 'HitOtherBody' and d.get('hit'): key += '-' + ('ally' if d['hit']['team'] == T else 'enemy')
        if key != 'HitHeadToHead': key += '/free' + ('0' if free == 0 else '1+')
        else: key += '-' + ('killer' if d['actor'] == d['id'] else 'victim')
        en = d.get('enemy_near', (0, 0, 99))[2]
        C[(mp, grp)][key] += 1
        C[(mp, grp)]['enemy<=2|' + key.split('/')[0]] += en <= 2
for k in sorted(C):
    n = N[k]; print(k, n, {a: round(b / n, 1) for a, b in sorted(C[k].items(), key=lambda x: -x[1])})
