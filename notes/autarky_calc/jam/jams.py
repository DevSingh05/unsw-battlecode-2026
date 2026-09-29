"""Detect jam/idle episodes of OUR team.
 A  mouth clump: >=3 our heads within BFS 3 of the same pocket mouth (or inside that pocket) and none of them eats that round;
    episode = maximal run of such rounds (>=3). Weight = dragon-rounds.
 B  open clump: >=3 our heads in one Chebyshev-3 cluster (single linkage), no member eats, >=3 rounds, not near a mouth.
 C  oscillation: a dragon whose last 6 head tiles have <=3 distinct tiles and no eat in those rounds.
 D  pearl-ignored: our dragon has a pearl within BFS 2 (open tiles, current bodies blocked) and does not eat within the next 3 rounds.
Writes jams_<game>.pkl and prints the ranked list."""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
def run(g, verbose=True):
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
    MO = mouths(m, PK)
    pocket_of = {}
    for u in PK:  # pocket id by mouth
        best = min(range(len(MO)), key=lambda i: m.dist(u, MO[i])); pocket_of[u] = best
    MD = [bfsd(m, x, 3) for x in MO]
    R = dict(S['rounds'])
    eatR = collections.defaultdict(set)
    for e in S['eats']: eatR[e['round']].add(e['id'])
    # rounds dict key r = state at END of round r
    rs = sorted(R)
    A = collections.defaultdict(list)  # mouth -> list of (r, ids)
    for r in rs:
        H = {j: t for j, (t, L, T) in R[r]['heads'].items() if T == us}
        for i, D in enumerate(MD):
            ids = [j for j, t in H.items() if t in D or pocket_of.get(t) == i]
            if len(ids) >= 3 and not any(j in eatR[r] for j in ids):
                A[i].append((r, ids))
    eps = []
    for i, lst in A.items():
        run_ = []
        for r, ids in lst + [(10**9, [])]:
            if run_ and r != run_[-1][0] + 1:
                if len(run_) >= 3:
                    allids = sorted({j for _, x in run_ for j in x})
                    eps.append(dict(kind='A-mouth', game=g, mouth=MO[i], r0=run_[0][0], r1=run_[-1][0], n=len(run_), ids=allids,
                                    dr=sum(len(x) for _, x in run_), maxh=max(len(x) for _, x in run_),
                                    pocket_pearls=[len([p for p in R[rr]['pearls'] if pocket_of.get(p) == i]) for rr, _ in run_]))
                run_ = []
            run_.append((r, ids))
    # B: open clumps
    Bl = []
    for r in rs:
        H = {j: t for j, (t, L, T) in R[r]['heads'].items() if T == us}
        ids = list(H); par = {j: j for j in ids}
        def f(x):
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        for a in ids:
            for b in ids:
                if a < b and m.cheb(H[a], H[b]) <= 3: par[f(a)] = f(b)
        cl = collections.defaultdict(list)
        for j in ids: cl[f(j)].append(j)
        for c in cl.values():
            if len(c) >= 3 and not any(j in eatR[r] for j in c) and not any(H[j] in D or H[j] in PK for j in c for D in MD):
                Bl.append((r, frozenset(c)))
    # chain clusters across rounds when they share >=2 members
    byr = collections.defaultdict(list)
    for r, c in Bl: byr[r].append(c)
    used = set()
    for r, c in Bl:
        if (r, c) in used: continue
        chain = [(r, c)]; used.add((r, c)); cur = c; rr = r
        while True:
            nx = [c2 for c2 in byr[rr + 1] if len(c2 & cur) >= 2 and (rr + 1, c2) not in used]
            if not nx: break
            cur = nx[0]; rr += 1; chain.append((rr, cur)); used.add((rr, cur))
        if len(chain) >= 3:
            allids = sorted(set().union(*[x for _, x in chain]))
            eps.append(dict(kind='B-open', game=g, r0=chain[0][0], r1=chain[-1][0], n=len(chain), ids=allids, dr=sum(len(x) for _, x in chain),
                            maxh=max(len(x) for _, x in chain), where=R[chain[0][0]]['heads'][sorted(chain[0][1])[0]][0]))
    # C: oscillation
    hist = collections.defaultdict(list)
    for r in rs:
        for j, (t, L, T) in R[r]['heads'].items():
            if T == us: hist[j].append((r, t, j in eatR[r]))
    osc = []
    for j, hs in hist.items():
        k = 0; cur = None
        for idx in range(5, len(hs)):
            w = hs[idx - 5: idx + 1]
            if w[-1][0] - w[0][0] == 5 and len({t for _, t, _ in w}) <= 3 and not any(e for _, _, e in w):
                if cur and cur['r1'] == w[-1][0] - 1: cur['r1'] = w[-1][0]
                else:
                    cur = dict(kind='C-osc', game=g, ids=[j], r0=w[0][0], r1=w[-1][0], where=w[-1][1]); osc.append(cur)
    for c in osc:
        c['n'] = c['r1'] - c['r0'] + 1; c['dr'] = c['n']; c['maxh'] = 1
    eps += osc
    return eps, S
if __name__ == '__main__':
    allep = []
    for g in (list(map(int, sys.argv[1:])) or list(GAMES)):
        eps, S = run(g); allep += eps
        pickle.dump(eps, open(os.path.join(H, 'jams_%d.pkl' % g), 'wb'))
        cnt = collections.Counter(); drs = collections.Counter()
        for e in eps: cnt[e['kind']] += 1; drs[e['kind']] += e['dr']
        print(g, dict(cnt), 'dragon-rounds', dict(drs))
    allep.sort(key=lambda e: -e['dr'])
    for e in allep[:40]:
        print(e['game'], e['kind'], 'r%d-%d' % (e['r0'], e['r1']), 'n=%d dr=%d maxh=%d' % (e['n'], e['dr'], e['maxh']), e.get('mouth', e.get('where')), e['ids'][:10], e.get('pocket_pearls', '')[:12] if e.get('pocket_pearls') else '')
