import pickle, collections, sys, analyze as A, sim2
MAPS = set(sys.argv[1].split(','))
res = {(r['gid'], r['grp']): r for r in pickle.load(open('metrics.pkl', 'rb'))}
C = collections.defaultdict(collections.Counter); N = collections.Counter(); ex = collections.defaultdict(list)
cache = {}
for it in A.games():
    p, gid, mp, T, grp = it[:5]
    if mp not in MAPS: continue
    r = res.get((gid, grp))
    if not r: continue
    T = r['T']
    if p not in cache: cache.clear(); cache[p] = sim2.simulate(p)
    g = cache[p]; m = g['map']; N[grp] += 1
    deg = lambda t: sum(1 for d in 'NESW' if m.step(t, d) is not None)
    eats_by = collections.defaultdict(list)
    for e in g['eats']: eats_by[e['id']].append(e['round'])
    for d in g['deaths']:
        if d['team'] != T or not (60 <= d['round'] <= 320): continue
        free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        if d['reason'] == 'HitHeadToHead' or free: continue
        c = C[grp]; c['trapped'] += 1
        dg = deg(d['head']); c[f'deg{dg}'] += 1
        kelp = sum(1 for v in d['nbrs'].values() if v == 'kelp'); c[f'kelpnb{kelp}'] += 1
        own = sum(1 for v in d['nbrs'].values() if isinstance(v, tuple) and v[0] in ('self',)); c[f'selfnb{own}'] += 1
        ally = sum(1 for v in d['nbrs'].values() if isinstance(v, tuple) and v[0] == 'ally'); c['allynb' + str(ally)] += 1
        en = sum(1 for v in d['nbrs'].values() if isinstance(v, tuple) and v[0] == 'enemy'); c['enemynb' + str(en)] += 1
        ate = sum(1 for rr in eats_by[d['id']] if d['round'] - 5 <= rr <= d['round']); c['ate5_' + str(min(ate, 2))] += 1
        c[f"len{min(d['len'],5)}"] += 1
        # corpse re-harvest
        drop = set(d['body'][::2])
        got = [e for e in g['eats'] if e['corpse'] and e['corpse'][0] == d['id']]
        c['drop'] += len(drop); c['own_eat'] += sum(1 for e in got if e['team'] == T); c['en_eat'] += sum(1 for e in got if e['team'] != T)
        c['own_eat10'] += sum(1 for e in got if e['team'] == T and e['round'] - d['round'] <= 10)
        if len(ex[grp]) < 4: ex[grp].append((gid, d['round'], d['id'], d['len'], d['reason'], d['nbrs']))
for g_, c in C.items():
    n = N[g_]; t = c['trapped']
    print(g_, 'games', n, 'trapped/game', round(t / n, 1), {k: round(v / t, 2) for k, v in sorted(c.items()) if k not in ('trapped',)})
    for e in ex[g_]: print('   ', e)
