"""Pocket idle capacity: rounds r60-349 where no head (either team) is inside a pocket, and who was near its mouth.
    python3 idle.py   (groups as report.py)"""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
sys.argv = ['x', 'none']; import report as RP
paths = {g['gid']: g['path'] for g in collect.games()}
for grp in ['us-L-strong', 'us-W-weak', 'us-W-strong', 'top-W']:
    c = collections.Counter(); n = 0
    for r in RP.G[grp]:
        S = sim2.simulate(paths[r['gid']]); m = S['map']; PK = collect.pockets(m); PID = collect.pocket_ids(PK, m)
        mouths = collections.defaultdict(list)
        for u in PK:
            for d in 'NESW':
                t = m.step(u, d)
                if t is not None and t not in PK: mouths[PID[u]].append(t)
        T = r['T']; n += 1
        for rnd, s in S['rounds']:
            if not (60 <= rnd <= 349): continue
            inside = collections.Counter(PID[v[0]] for v in s['heads'].values() if v[0] in PK)
            for p, ms in mouths.items():
                c['pocket_rounds'] += 1
                if inside[p]: continue
                c['idle'] += 1
                own = min((m.dist(v[0], mt) for v in s['heads'].values() if v[2] == T and v[1] <= 3 for mt in ms), default=99)
                en = min((m.dist(v[0], mt) for v in s['heads'].values() if v[2] != T for mt in ms), default=99)
                c['own<=3'] += own <= 3; c['own<=6'] += own <= 6; c['own<=10'] += own <= 10
                c['en<=3'] += en <= 3
                c['own_closer'] += own < en
    print(f"{grp:14s} idle {100 * c['idle'] / c['pocket_rounds']:.0f}% of pocket-rounds r60-349 ({c['idle'] / n:.0f} per game);"
          f" during idle: own L<=3 head within 3/6/10 of mouth {100 * c['own<=3'] / c['idle']:.0f}/{100 * c['own<=6'] / c['idle']:.0f}/{100 * c['own<=10'] / c['idle']:.0f}%,"
          f" enemy head within 3 {100 * c['en<=3'] / c['idle']:.0f}%, own closer than enemy {100 * c['own_closer'] / c['idle']:.0f}%")
