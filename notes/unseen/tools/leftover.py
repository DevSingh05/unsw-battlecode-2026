#!/usr/bin/env python3
"""Length left unconverted at r500 in round-limit games: non-king dragons by length bucket and their
distance to the final king at r450 and r500. usage: python3 leftover.py"""
import collections, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feedeff as F
from multiprocessing import Pool


def work(job):
    path, T, grp, mp = job
    g = F.simulate(path)
    if g['result'].get('endReason') != 'roundLimit':
        return None
    m = g['map']; rounds = dict(g['rounds']); last = g['last_round']
    fin = rounds[last][T]
    if not fin['ids']:
        return None
    k = max(fin['ids'], key=lambda j: (fin['ids'][j], -j))
    out = {'grp': grp, 'second': sorted(fin['ids'].values(), reverse=True)[1:2], 'rows': []}
    kh = fin_heads = rounds[last]['heads']
    kt = fin_heads[k][0]
    for j, L in fin['ids'].items():
        if j == k: continue
        out['rows'].append((L, m.dist(fin_heads[j][0], kt)))
    return out


def main():
    G = F.games()
    with Pool(4) as P:
        R = [r for r in P.map(work, G, chunksize=2) if r]
    for grp in ('top', 'us'):
        X = [r for r in R if r['grp'] == grp]
        rows = [x for r in X for x in r['rows']]
        b = collections.Counter(); d = collections.defaultdict(list)
        for L, dist in rows:
            k = 'L2-3' if L <= 3 else 'L4-7' if L <= 7 else 'L8-15' if L <= 15 else 'L16+'
            b[k] += L; d[k].append(dist)
        print(grp, len(X), 'non-king length at r500 per game:', {k: round(v / len(X), 1) for k, v in b.items()},
              'median dist to king:', {k: st.median(v) for k, v in d.items()},
              'second longest mean %.1f' % st.mean([r['second'][0] for r in X if r['second']]))


if __name__ == '__main__':
    main()
