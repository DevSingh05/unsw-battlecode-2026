"""Dead-end pocket harvesting: pocket tiles = removed by iterative leaf pruning of the static tile graph."""
import pickle, collections, analyze as A, sim2
res = {(r['gid'], r['grp']): r for r in pickle.load(open('metrics.pkl', 'rb'))}
def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = set(); depth = {}
    q = [t for t, d in deg.items() if d <= 1]; k = 1
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem.add(t); depth[t] = k
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq; k += 1
    return rem, depth
C = collections.defaultdict(collections.Counter); N = collections.Counter(); PM = {}
cache = {}
for it in A.games():
    p, gid, mp, T, grp = it[:5]
    r = res.get((gid, grp))
    if not r: continue
    T = r['T']
    if p not in cache: cache.clear(); cache[p] = sim2.simulate(p)
    g = cache[p]; m = g['map']
    if mp not in PM: PM[mp] = pockets(m)
    pk, depth = PM[mp]
    key = (mp, grp); N[key] += 1; c = C[key]
    c['pocket_tiles'] = len(pk)
    for e in g['eats']:
        if e['team'] == T and 60 <= e['round'] <= 320:
            c['eats'] += 1
            if e['tile'] in pk: c['pk_eats'] += 1; c['pk_spawn'] += not e['corpse']
    for a in g['moves']:
        if a['team'] == T and 60 <= a['round'] <= 320:
            c['turns'] += 1; c['pk_turns'] += a['head'] in pk
    dr = {d['id']: d for d in g['deaths']}
    for s in g['splits']:
        if s['team'] != T or not (60 <= s['round'] <= 320): continue
        if s['exits'] <= 1:
            c['sp_exit01'] += 1
            d = dr.get(s['parent'])
            if d and d['round'] - s['round'] <= 3: c['pump'] += 1; c['pump_k'] += s['k']; c['pump_L'] += s['L']
    for d in g['deaths']:
        if d['team'] == T and 60 <= d['round'] <= 320 and d['head'] in pk: c['pk_deaths'] += 1
for k in sorted(C):
    c = C[k]; n = N[k]
    print(f"{k[0][:10]:10s} {k[1]:7s} n={n:2d} pocketTiles={c['pocket_tiles']:3d} eats/g={c['eats']/n:5.0f} pocketEats/g={c['pk_eats']/n:5.1f} ({100*c['pk_eats']/max(1,c['eats']):4.1f}%) pocketTurn%={100*c['pk_turns']/max(1,c['turns']):4.1f} pocketDeaths/g={c['pk_deaths']/n:4.1f} lowExitSplits/g={c['sp_exit01']/n:4.1f} pump/g={c['pump']/n:4.1f} pumpL={c['pump_L']/max(1,c['pump']):.1f} pumpK={c['pump_k']/max(1,c['pump']):.1f}")
