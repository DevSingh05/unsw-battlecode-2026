import pickle, collections, analyze as A, sim2
res = {(r['gid'], r['grp']): r for r in pickle.load(open('metrics.pkl', 'rb'))}
C = collections.defaultdict(collections.Counter); N = collections.Counter()
cache = {}
for it in A.games():
    p, gid, mp, T, grp = it[:5]
    r = res.get((gid, grp))
    if not r: continue
    T = r['T']
    if p not in cache: cache.clear(); cache[p] = sim2.simulate(p)
    g = cache[p]; m = g['map']
    if not any(k == 2 for k, _ in m.edges.values()): continue
    N[(mp, grp)] += 1; c = C[(mp, grp)]
    for a in g['moves']:
        if a['team'] != T or not (60 <= a['round'] <= 320) or a.get('suicide'): continue
        mvs = a['act'].get('move', [])
        pos = a['head']; crossed = False
        for i, d in enumerate(mvs):
            e = m.side_edge(pos, d)
            if m.edges.get(e, (0, -1))[0] == 2: crossed = True; break
            nxt = m.step(pos, d)
            if nxt is None: break
            pos = nxt
        c['moves'] += 1
        if crossed:
            c['cross'] += 1
            if a['died']: c['cross_died'] += 1; c['cross_died_' + a['died']] += 1
        elif a['died']: c['nocross_died'] += 1
for k in sorted(C):
    c = C[k]; n = N[k]
    print(k, n, 'moves/g', round(c['moves'] / n), 'cross/g', round(c['cross'] / n, 1), 'cross%', round(100 * c['cross'] / c['moves'], 2),
          'death|cross %', round(100 * c['cross_died'] / max(1, c['cross']), 1), 'death|nocross %', round(100 * c['nocross_died'] / max(1, c['moves'] - c['cross']), 2),
          {x.replace('cross_died_', ''): round(v / n, 1) for x, v in c.items() if x.startswith('cross_died_')})
