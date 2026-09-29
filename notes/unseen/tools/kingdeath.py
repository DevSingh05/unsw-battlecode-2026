#!/usr/bin/env python3
"""Deaths of the team's longest dragon (L>=10) from r400, all games (ours vs top-10), by reason and killer.
usage: python3 kingdeath.py"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feedeff as F
from multiprocessing import Pool


def work(job):
    path, T, grp, mp = job
    g = F.simulate(path)
    out = []
    for d in g['deaths']:
        if d['team'] != T or d['round'] < 400 or d['len'] < 10: continue
        other = d.get('king')
        if other and other[1] >= d['len']: continue
        vol = d['actor'] == d['id'] and d['reason'] in ('HitSelf', 'NoValidAction') and any(v in ('free', 'pearl') for v in d.get('nbrs', {}).values())
        kind = 'voluntary' if vol else d['reason'] + ('/enemy' if d.get('killer_team', d.get('victim_team', T)) != T else '')
        out.append((grp, d['round'] // 25 * 25, kind, d['len'], d.get('killer_len') or d.get('victim_len'), d.get('enemy_near', (0, 0, 99))[2]))
    return [(grp, g['result'].get('endReason'))] + out


def main():
    G = F.games()
    with Pool(4) as P:
        R = P.map(work, G, chunksize=2)
    for grp in ('top', 'us'):
        n = sum(1 for r in R if r and r[0][0] == grp)
        rows = [x for r in R if r and r[0][0] == grp for x in r[1:]]
        print(grp, 'team-games', n, 'longest-dragon deaths r400+ per game %.2f' % (len(rows) / n))
        print('  by kind:', collections.Counter(x[2] for x in rows).most_common())
        print('  by round:', sorted(collections.Counter(x[1] for x in rows).items()))
        print('  enemy dist at death (non-voluntary):', collections.Counter(min(x[5], 9) for x in rows if x[2] != 'voluntary').most_common(6))


if __name__ == '__main__':
    main()
