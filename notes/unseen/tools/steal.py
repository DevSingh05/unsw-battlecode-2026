#!/usr/bin/env python3
"""Who eats the king's food? For own-corpse pearls from deaths within 3 of the final king (r300+),
eaten by a non-king ally: eater length, eater distance to king head at eat time, and whether the
eater later died within 3 of the king (recycled). usage: python3 steal.py [us|top]"""
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
    lineage = {k}; cur = k
    while cur in g['parent_of']:
        p = g['parent_of'][cur]
        sp = [s for s in g['splits'] if s['child'] == cur]
        if sp and sp[0]['k'] > sp[0]['L'] - sp[0]['k']:
            lineage.add(p); cur = p
        else:
            break
    near = set()
    for d in g['deaths']:
        if d['team'] == T and d['round'] >= 300 and d['id'] not in lineage and d.get('king') and d['king'][0] in lineage and d['king'][2] <= 3:
            near.add(d['id'])
    death_of = {d['id']: d for d in g['deaths']}
    out = []
    for e in g['eats']:
        if not e['corpse'] or e['corpse'][0] not in near or e['team'] != T or e['id'] in lineage:
            continue
        s = rounds.get(e['round'])
        kh = None
        if s:
            for j in lineage:
                if j in s['heads']:
                    kh = s['heads'][j][0]
        kd = m.dist(e['tile'], kh) if kh else None
        dd = death_of.get(e['id'])
        rec = dd and dd.get('king') and dd['king'][0] in lineage and dd['king'][2] <= 3
        out.append((e['len'], kd, bool(rec), e['round'] - e['corpse'][2]))
    return out


def main():
    grp = sys.argv[1] if len(sys.argv) > 1 else 'us'
    G = [x for x in F.games() if x[2] == grp]
    with Pool(4) as P:
        R = [r for x in P.map(work, G, chunksize=2) if x for r in x]
    print(grp, 'stolen pearls', len(R))
    print(' eater len:', collections.Counter(min(r[0] or 0, 7) for r in R).most_common())
    print(' pearl dist to king head at eat:', sorted(collections.Counter(min(r[1], 9) for r in R if r[1] is not None).items()))
    print(' eater later died within 3 of king (recycled):', sum(r[2] for r in R) / max(1, len(R)))
    print(' rounds after drop:', st.median([r[3] for r in R]))


if __name__ == '__main__':
    main()
