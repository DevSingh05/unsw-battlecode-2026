#!/usr/bin/env python3
"""Offline check (no games): does a neighbour-smoothed pearl prior rank moves better than the flat UNK_PRIOR?

usage (from project root): python3 notes/unseen/tools/pearl_smooth_sim.py [set=gen] [samples_per_map=60]
For random head tiles and rounds, the dragon sees its 7x7 window (true spawner status + range class via
observed countdowns, idealised). For each of the 4 first steps it BFS-sums (kelp respected, portals as plain
edges like the bot) gamma^d * p(tile) over UNSEEN tiles within 25 steps, under:
  truth : p = P(first spawn by round r | tile range)   (ignores eating)
  flat  : p = 0.5*min(1,.01 r)                           (current bot)
  smooth: p = blend of 'nearest seen tile's class' and the flat prior, weight decaying with distance
Reports agreement of each model's best direction with truth's best, and truth-regret.
Also prints P(same spawner status) vs offset distance k (the decay the smooth model relies on).
"""
import glob, random, sys
from collections import deque
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from pearl_stats import ROOT, first_by

G = 0.82

def load(path):
    W = H = 0; tiles = {}; kelp = set()
    for line in open(path):
        p = line.split()
        if not p: continue
        if p[0] == 'MAP': W, H = int(p[1]), int(p[2])
        elif p[0] == 'TILE': tiles[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
        elif p[0] == 'EDGE' and p[2] == '1': kelp.add(int(p[1]))
    for x in range(W):
        for y in range(H):
            tiles.setdefault((x, y), (0, 0))
    return W, H, tiles, kelp

def nbrs(W, H, kelp, x, y):
    # edge index: north edge of (x,y) = 2y*(W+1)+x ; west edge = (2y+1)*(W+1)+x ; wrap uses y=0 / x=0 rows
    out = []
    if (2 * y) * (W + 1) + x not in kelp and (2 * ((y + 1) % H)) * (W + 1) + x not in kelp or True:
        pass
    n = (2 * y) * (W + 1) + x
    s = (2 * ((y + 1) % H)) * (W + 1) + x
    wv = (2 * y + 1) * (W + 1) + x
    e = (2 * y + 1) * (W + 1) + (x + 1) % W
    # border edges may also be stored at index x=W / y=H
    s2 = (2 * (y + 1)) * (W + 1) + x
    e2 = (2 * y + 1) * (W + 1) + x + 1
    if n not in kelp: out.append((x, (y - 1) % H))
    if s not in kelp and s2 not in kelp: out.append((x, (y + 1) % H))
    if wv not in kelp: out.append(((x - 1) % W, y))
    if e not in kelp and e2 not in kelp: out.append(((x + 1) % W, y))
    return out

def main():
    sset = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    files = sorted(glob.glob(ROOT + '/maps/%s/*.map' % sset)) if sset != 'ranked' else \
        [ROOT + '/maps/%s.map' % m for m in ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy",
                                             "autarky", "dilemma", "slithery_fight", "trauma"]]
    rng = random.Random(7)
    # decay of spawner-status agreement with offset k
    agree = {k: [0, 0] for k in range(1, 9)}
    for f in files:
        W, H, tiles, _ = load(f)
        for (x, y), r in tiles.items():
            for k in agree:
                for q in (tiles[((x + k) % W, y)], tiles[(x, (y + k) % H)]):
                    agree[k][0] += (r[1] > 0) == (q[1] > 0); agree[k][1] += 1
    print('P(same spawner status) at offset k:', ' '.join('k%d=%.2f' % (k, a / b) for k, (a, b) in agree.items()))
    res = {m: [0, 0.0] for m in ('flat', 'smooth')}
    n = 0
    for f in files:
        W, H, tiles, kelp = load(f)
        adj = {t: nbrs(W, H, kelp, *t) for t in tiles}
        glob_p = {}
        for _ in range(S):
            hx, hy = rng.randrange(W), rng.randrange(H)
            rnd = rng.choice((40, 80, 150, 250))
            flatp = 0.5 * min(1, 0.01 * rnd)
            seen = {((hx + dx) % W, (hy + dy) % H) for dx in range(-3, 4) for dy in range(-3, 4)}
            if len(adj[(hx, hy)]) < 2: continue
            # smoothed estimate for every tile from nearest seen tile (Chebyshev from window edge)
            def smooth_p(t):
                dx = (t[0] - hx + W // 2) % W - W // 2; dy = (t[1] - hy + H // 2) % H - H // 2
                cx = max(-3, min(3, dx)); cy = max(-3, min(3, dy))
                k = max(abs(dx - cx), abs(dy - cy))
                src = tiles[((hx + cx) % W, (hy + cy) % H)]
                w = 0.85 ** k  # trust in the neighbour class decays with distance
                return w * first_by(src, rnd) + (1 - w) * flatp * 0.6
            vals = {}
            for d, s0 in enumerate(adj[(hx, hy)]):
                dist = {s0: 1}; q = deque([s0]); tot = {'truth': 0, 'flat': 0, 'smooth': 0}
                blocked = {(hx, hy)}
                while q:
                    u = q.popleft(); du = dist[u]
                    if u not in seen:
                        g = G ** du
                        tot['truth'] += g * first_by(tiles[u], rnd)
                        tot['flat'] += g * flatp
                        tot['smooth'] += g * smooth_p(u)
                    if du >= 25: continue
                    for v in adj[u]:
                        if v not in dist and v not in blocked:
                            dist[v] = du + 1; q.append(v)
                vals[d] = tot
            if len(vals) < 2: continue
            best_t = max(vals, key=lambda d: vals[d]['truth'])
            tmax = vals[best_t]['truth']
            if tmax <= 1e-9: continue
            n += 1
            for m in res:
                pick = max(vals, key=lambda d: vals[d][m])
                res[m][0] += pick == best_t
                res[m][1] += vals[pick]['truth'] / tmax
    print('%s: %d samples' % (sset, n))
    for m, (a, reg) in res.items():
        print('  %-6s picks truth-best %.1f%%, mean truth value of pick %.3f of best' % (m, 100 * a / n, reg / n))

if __name__ == '__main__':
    main()
