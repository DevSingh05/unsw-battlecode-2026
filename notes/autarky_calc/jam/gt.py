"""Ground truth per dragon-turn, both teams, from the replay state at the END of the previous round:
nearest pearl (BFS over free tiles, bodies block, cap 8), whether another head (ally / enemy) is strictly closer to it,
nearest enemy head, own heads within Chebyshev 3.  -> gt_<g>.pkl  {(id, r): dict}"""
import sys, collections, pickle
from common import *
def bfs(m, src, occ, cap):
    D = {src: 0}; q = [src]
    for u in q:
        if D[u] >= cap: continue
        for d in 'NESW':
            v = m.step(u, d)
            if v is None or v in D or v in occ: continue
            D[v] = D[u] + 1; q.append(v)
    return D
for g in GAMES:
    S = sim(g); m = S['map']; R = dict(S['rounds']); out = {}
    for r in sorted(R):
        if r + 1 not in R: continue
        st = R[r]; occ = set(t for b in st['bodies'].values() for t in b)
        heads = st['heads']
        Ds = {j: bfs(m, t, occ - {t}, 8) for j, (t, L, T) in heads.items()}
        for j, (t, L, T) in heads.items():
            D = Ds[j]
            pe = sorted((D[p], p) for p in st['pearls'] if p in D)
            near = pe[0] if pe else (99, None)
            closer_ally = closer_en = False
            if near[1] is not None:
                for k, (t2, L2, T2) in heads.items():
                    if k == j: continue
                    d2 = Ds[k].get(near[1], 99)
                    if d2 < near[0]:
                        if T2 == T: closer_ally = True
                        else: closer_en = True
            en = min((m.dist(t, t2) for k, (t2, L2, T2) in heads.items() if T2 != T), default=99)
            al = sum(1 for k, (t2, L2, T2) in heads.items() if T2 == T and k != j and m.cheb(t, t2) <= 3)
            # "free" pearls: nearest pearl that no other head reaches first
            free = [d for d, p in pe if all(Ds[k].get(p, 99) >= d for k in heads if k != j)]
            out[(j, r + 1)] = dict(T=T, L=L, head=t, pd=near[0], p_ally_closer=closer_ally, p_en_closer=closer_en,
                                   free_pd=free[0] if free else 99, en=en, allies3=al, npear=len(pe))
    pickle.dump(out, open('gt_%d.pkl' % g, 'wb'))
    print(g, len(out))
