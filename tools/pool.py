#!/usr/bin/env python3
"""Test a candidate against a pool of past versions, with a confidence interval.

usage: pool.py CANDIDATE [--pool variants/v61,variants/v44,variants/v35] [--seeds 3] [--jobs 16]
       CANDIDATE is 'dir' or 'dir:-DFLAG=1 ...' (see arena.py)

Plays every pool member on all 10 ranked maps, both sides, seeds 1000+. Reports the
score (win=1, draw=0.5) with a 95% interval, per opponent and per map. Only trust a
change whose interval stays above 0.5.
"""
import argparse
import concurrent.futures as cf
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from arena import RANKED, build, play  # noqa: E402


def interval(score, n):
    if n == 0:
        return 0.0, 1.0
    p = score / n
    z = 1.96
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--pool", default="variants/v61,variants/v44,variants/v35")
    ap.add_argument("--maps", default=",".join(RANKED))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed-base", type=int, default=1000)
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    cand = build(a.cand)
    pool = [(p, build(p)) for p in a.pool.split(",")]
    maps = a.maps.split(",")
    jobs = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, opp in pool:
            for mp in maps:
                for s in range(a.seeds):
                    seed = a.seed_base + s
                    jobs.append((name, mp, False, ex.submit(play, cand, opp, mp, seed, None)))
                    jobs.append((name, mp, True, ex.submit(play, opp, cand, mp, seed, None)))
        by_opp, by_map = {}, {}
        total = n = 0
        for name, mp, swapped, fut in jobs:
            winner = fut.result()[0]
            if winner == "?":
                continue
            s = 0.5 if winner == "D" else float(winner == ("B" if swapped else "A"))
            total += s
            n += 1
            for d, k in ((by_opp, name), (by_map, mp)):
                d.setdefault(k, [0.0, 0])
                d[k][0] += s
                d[k][1] += 1
    for title, d in (("vs opponent", by_opp), ("per map", by_map)):
        print(title)
        for k, (s, m) in d.items():
            lo, hi = interval(s, m)
            print(f"  {k:22s} {s:5.1f}/{m:<4d} {s / m:.2f}  [{lo:.2f}, {hi:.2f}]")
    lo, hi = interval(total, n)
    print(f"OVERALL {a.cand}: {total:.1f}/{n} = {total / max(1, n):.3f}  95% [{lo:.3f}, {hi:.3f}]")


if __name__ == "__main__":
    main()
