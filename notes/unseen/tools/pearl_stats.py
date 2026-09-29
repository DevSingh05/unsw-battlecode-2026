#!/usr/bin/env python3
"""Static pearl statistics over map files (read-only; no games run).

usage (from project root): python3 notes/unseen/tools/pearl_stats.py [--per-map]
Sets: gen, genhold, lesson, ranked. Prints per-set averages of:
  spawn%   fraction of tiles that spawn
  P/rnd    expected pearls per round if never blocked (sum 1/mean_gap)
  fast3/10/30  share of production from tiles with mean gap <=3/<=10/<=30
  top5%    share of production from the best 5% of tiles
  prior(r) true P(a never-seen tile has had its first spawn by round r) vs bot's 0.5*min(1,.01r)
  nbSame   P(4-neighbour has same spawner status), nbRange P(same [min,max] | both spawn)
  vis0     share of production inside the 7x7 views of one team's starting heads
  near10   share within torus-Manhattan 10 of a starting head (one team)
  half     share on the team's own half (by symmetry axis)
"""
import glob, math, sys, statistics as st

ROOT = __file__.rsplit('/notes/', 1)[0]
RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy",
          "autarky", "dilemma", "slithery_fight", "trauma"]

def load(path):
    W = H = 0; sym = None; tiles = {}; dragons = []
    for line in open(path):
        p = line.split()
        if not p: continue
        if p[0] == 'MAP': W, H = int(p[1]), int(p[2])
        elif p[0] == 'SYMMETRY': sym = p[1]
        elif p[0] == 'TILE': tiles[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
        elif p[0] == 'DRAGON': dragons.append((int(p[1]), int(p[3]), int(p[4])))
    return W, H, sym, tiles, dragons

def mean_gap(r):
    lo, hi = r
    return (lo + hi) / 2.0

def first_by(r, rnd):
    lo, hi = r
    if hi == 0: return 0.0
    return max(0.0, min(1.0, (rnd - lo + 1) / (hi - lo + 1)))

def tdist(a, b, W, H):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)

def stats(path):
    W, H, sym, tiles, dragons = load(path)
    N = W * H
    rate = {}
    for x in range(W):
        for y in range(H):
            r = tiles.get((x, y), (0, 0))
            rate[(x, y)] = 0.0 if r[1] == 0 else 1.0 / mean_gap(r)
            tiles[(x, y)] = r
    P = sum(rate.values())
    out = {'name': path.rsplit('/', 1)[-1][:-4], 'W': W, 'H': H, 'sym': sym or '-'}
    out['spawn'] = sum(1 for r in tiles.values() if r[1] > 0) / N
    out['P'] = P
    out['perTile'] = P / N
    for k in (3, 10, 30):
        out['fast%d' % k] = sum(rate[t] for t in tiles if tiles[t][1] and mean_gap(tiles[t]) <= k) / P if P else 0
    out['slow100'] = sum(rate[t] for t in tiles if tiles[t][1] and mean_gap(tiles[t]) >= 100) / P if P else 0
    rs = sorted(rate.values(), reverse=True)
    out['top5'] = sum(rs[:max(1, N // 20)]) / P if P else 0
    for rnd in (25, 50, 100, 200, 300):
        out['prior%d' % rnd] = sum(first_by(tiles[t], rnd) for t in tiles) / N
    same = tot = rsame = rtot = 0
    for (x, y), r in tiles.items():
        for dx, dy in ((1, 0), (0, 1)):
            q = tiles[((x + dx) % W, (y + dy) % H)]
            tot += 1; same += (r[1] > 0) == (q[1] > 0)
            if r[1] and q[1]:
                rtot += 1; rsame += r == q
    out['nbSame'] = same / tot
    out['nbRange'] = rsame / rtot if rtot else float('nan')
    heads = [(x, y) for team, x, y in dragons if team == 0]
    vis = set()
    for hx, hy in heads:
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                vis.add(((hx + dx) % W, (hy + dy) % H))
    out['vis0'] = sum(rate[t] for t in vis) / P if P else 0
    out['near10'] = sum(rate[t] for t in tiles if heads and min(tdist(t, h, W, H) for h in heads) <= 10) / P if P else 0
    # own half: closer (torus Manhattan) to own heads than to enemy heads
    eheads = [(x, y) for team, x, y in dragons if team == 1]
    if heads and eheads:
        own = sum(rate[t] for t in tiles if min(tdist(t, h, W, H) for h in heads) < min(tdist(t, h, W, H) for h in eheads))
        out['half'] = own / P if P else 0
    else:
        out['half'] = float('nan')
    out['N'] = N
    return out

def ours(rnd):
    return 0.5 * min(1.0, 0.01 * rnd)

def main():
    per = '--per-map' in sys.argv
    sets = {
        'gen': sorted(glob.glob(ROOT + '/maps/gen/*.map')),
        'genhold': sorted(glob.glob(ROOT + '/maps/genhold/*.map')),
        'lesson': sorted(glob.glob(ROOT + '/maps/lesson/*.map')),
        'ranked': [ROOT + '/maps/%s.map' % m for m in RANKED],
    }
    keys = ['spawn', 'perTile', 'fast3', 'fast10', 'fast30', 'slow100', 'top5', 'nbSame', 'nbRange', 'vis0', 'near10', 'half',
            'prior25', 'prior50', 'prior100', 'prior200', 'prior300']
    print('%-8s %3s ' % ('set', 'n') + ' '.join('%8s' % k for k in keys))
    for name, files in sets.items():
        rows = [stats(f) for f in files]
        if per:
            for r in rows:
                print('  %-18s %2dx%-2d %-2s ' % (r['name'], r['W'], r['H'], r['sym']) + ' '.join('%8.3f' % r[k] for k in keys))
        med = {k: st.median([r[k] for r in rows if not math.isnan(r[k])]) for k in keys}
        avg = {k: st.mean([r[k] for r in rows if not math.isnan(r[k])]) for k in keys}
        print('%-8s %3d ' % (name + ':avg', len(rows)) + ' '.join('%8.3f' % avg[k] for k in keys))
        print('%-8s %3s ' % (name + ':med', '') + ' '.join('%8.3f' % med[k] for k in keys))
    print('bot prior 0.5*min(1,.01r):', ' '.join('r%d=%.3f' % (r, ours(r)) for r in (25, 50, 100, 200, 300)))

if __name__ == '__main__':
    main()
