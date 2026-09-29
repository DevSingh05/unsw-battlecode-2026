#!/usr/bin/env python3
"""Unknown-map endgame in local v24 self-play replays (notes/unseen/replays/king/*.replay).
usage: python3 localking.py [glob]"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feedeff as F
from multiprocessing import Pool


def main():
    pat = sys.argv[1] if len(sys.argv) > 1 else os.path.join(F.ROOT, 'notes/unseen/replays/king/*.replay')
    jobs = [(p, T, 'local', os.path.basename(p)) for p in sorted(glob.glob(pat)) for T in 'AB']
    with Pool(4) as P:
        res = [r for r in P.map(F.work, jobs) if r]
    print(len(res), 'team-games at r500')
    for r in res:
        c = r['curve']
        print(f"{r['map'][:26]:26s} {r['T']} king " + ' '.join(f"{c[x][0]:3d}" for x in (300, 350, 400, 450, 500)) +
              f" | longest r500 {c[500][1]:3d} enemy {c[500][2]:3d} units {c[500][3]:2d} total {c[500][4]:3d} | feeders {sum(1 for f in r['feeders'] if f['king'] > 0):2d} ownpearls {sum(f['king'] for f in r['feeders']):3d}")
    F.report([dict(x, grp='us') for x in res])


if __name__ == '__main__':
    main()
