#!/usr/bin/env python3
"""Does the king's beacon reach the team late in the game? For own non-king dragons alive at
r430/r470 in round-limit games: share hit by any own-team sonar ray in the previous 8 rounds
(upper bound on 'heard the king'), by length. usage: python3 reach.py"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feedeff as F
from multiprocessing import Pool


def work(job):
    path, T, grp, mp = job
    g = F.simulate(path)
    if g['result'].get('endReason') != 'roundLimit':
        return None
    rounds = dict(g['rounds'])
    out = []
    for R0 in (430, 470):
        s = rounds.get(R0)
        if not s: continue
        k = s[T]['king']
        hit = set(x['hitId'] for x in g['sonars'] if x['team'] == T and R0 - 8 <= x['round'] <= R0 and x['hitId'] is not None)
        pings = collections.Counter(x['id'] for x in g['sonars'] if x['team'] == T and R0 - 8 <= x['round'] <= R0)
        for j, L in s[T]['ids'].items():
            if j == k: continue
            out.append((grp, R0, 'L2-3' if L <= 3 else 'L4-7' if L <= 7 else 'L8+', j in hit, pings[j] > 0))
    return out


def main():
    G = F.games()
    with Pool(4) as P:
        R = [x for r in P.map(work, G, chunksize=2) if r for x in r]
    c = collections.defaultdict(lambda: [0, 0, 0])
    for grp, R0, b, h, p in R:
        c[(grp, R0, b)][0] += 1; c[(grp, R0, b)][1] += h; c[(grp, R0, b)][2] += p
    for k in sorted(c):
        n, h, p = c[k]
        print(k, n, 'hit by own ray %.2f' % (h / n), 'itself pinged %.2f' % (p / n))


if __name__ == '__main__':
    main()
