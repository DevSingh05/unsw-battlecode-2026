import pickle, collections, statistics as st, analyze as A, sim2
res = {(r['gid'], r['grp']): r for r in pickle.load(open('metrics.pkl', 'rb'))}
def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = {}; q = [t for t, d in deg.items() if d <= 1]; k = 1
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem[t] = k
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq; k += 1
    return rem
C = collections.defaultdict(lambda: collections.defaultdict(list)); cache = {}
for it in A.games():
    p, gid, mp, T, grp = it[:5]
    if mp not in ('Autarky', 'Trauma', 'Prisoners Dilemma') or grp not in ('top', 'topopp', 'usopp'): continue
    r = res.get((gid, grp)); T = r['T']
    if p not in cache: cache.clear(); cache[p] = sim2.simulate(p)
    g = cache[p]; m = g['map']; pk = pockets(m)
    rounds = dict(g['rounds'])
    # episodes: a dragon whose head enters a pocket tile
    inside = {}
    for a in g['moves']:
        if a['team'] != T or not (60 <= a['round'] <= 320) or a.get('suicide'): continue
        h1 = a.get('head_after')
        if a['head'] not in pk and h1 in pk:
            # entry
            hs = rounds.get(a['round'] - 1, {}).get('heads', {})
            en = min((m.dist(h1, v[0]) for v in hs.values() if v[2] != T), default=99)
            own_in = sum(1 for k, v in hs.items() if v[2] == T and v[0] in pk and m.dist(v[0], h1) <= 6)
            C[grp]['entry_len'].append(a['len_before']); C[grp]['entry_enemy'].append(en); C[grp]['entry_own_inside'].append(own_in)
    dr = {d['id']: d for d in g['deaths']}
    for s in g['splits']:
        if s['team'] != T or not (60 <= s['round'] <= 320) or s['exits'] > 1: continue
        d = dr.get(s['parent'])
        if not d or d['round'] - s['round'] > 3: continue
        C[grp]['pump_L'].append(s['L']); C[grp]['pump_k_is_L-2'].append(int(s['k'] == s['L'] - 2)); C[grp]['pump_exits'].append(s['exits'])
        C[grp]['parent_death'].append(d['reason']); C[grp]['in_pocket'].append(int(d['head'] in pk))
        C[grp]['depth'].append(pk.get(d['head'], 0))
for g, c in C.items():
    print(g)
    for k, v in c.items():
        if isinstance(v[0], str): print('  ', k, collections.Counter(v).most_common())
        else: print('  ', k, 'n', len(v), 'mean', round(sum(v) / len(v), 2), 'hist', dict(sorted(collections.Counter(min(x, 8) for x in v).items())))
