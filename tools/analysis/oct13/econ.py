#!/usr/bin/env python3
"""econ.py RUN SUFFIX [SUFFIX ...] [--jobs 4]: early economy of each candidate build in a local run, per map.

For every game of work/oct12/results/RUN.jsonl in which a build whose path ends with SUFFIX played: W-L, and the
candidate's / the opponent's length at r100 and r200, units at r100 and distinct tiles visited by r100 (spread.py).
One row per map and candidate, medians over the games, then a total row per candidate (sum of W-L, mean of the
per-map length ratios).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/econ.py t74_gamma stage/g88 stage/g92 stage/g95"""
import collections
import json
import pathlib
import statistics as st
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "analysis" / "oct13"))
import spread as SP  # noqa: E402

SP.CK = (100, 200)


def job(a):
    replay, us = a
    try:
        _, out = SP.one(replay, us)
    except Exception:  # noqa: BLE001
        return None
    th = "B" if us == "A" else "A"
    return {k: (out.get((k, us)), out.get((k, th))) for k in SP.CK}


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    jobs_n = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 4
    if "--jobs" in sys.argv:
        args.remove(sys.argv[sys.argv.index("--jobs") + 1])
    run, bots = args[0], args[1:]
    todo = []
    for line in open(ROOT / "work/oct12/results" / f"{run}.jsonl"):
        r = json.loads(line)
        if not r.get("replay") or "wins" not in (r.get("result") or ""):
            continue
        for b in bots:
            us = "A" if r["A"].endswith(b) else ("B" if r["B"].endswith(b) else None)
            if us:
                todo.append((b, pathlib.Path(r["map"]).stem, r["result"].startswith(f"team {us} wins"), str(ROOT / r["replay"]), us))
    with Pool(jobs_n) as pool:
        res = pool.map(job, [(t[3], t[4]) for t in todo], chunksize=2)
    G = collections.defaultdict(list)
    for (b, mp, win, _, _), r in zip(todo, res):
        if r:
            G[(mp, b)].append((win, r))
    print("| map | build | W-L | length r100 us/them | length r200 us/them | units r100 us/them | tiles visited r100 us/them |")
    print("|---|---|---|---|---|---|---|")
    tot = collections.defaultdict(lambda: [0, 0, [], []])
    for mp in sorted({k[0] for k in G}):
        for b in bots:
            L = G.get((mp, b))
            if not L:
                continue
            w = sum(x[0] for x in L)
            med = lambda ck, side, k: st.median([x[1][ck][side][k] for x in L if x[1][ck][0] and x[1][ck][1]] or [0])
            l1u, l1t, l2u, l2t = med(100, 0, 1), med(100, 1, 1), med(200, 0, 1), med(200, 1, 1)
            print(f"| {mp} | {b.split('/')[-1]} | {w}-{len(L) - w} | {l1u:.0f}/{l1t:.0f} | {l2u:.0f}/{l2t:.0f} | {med(100, 0, 0):.0f}/{med(100, 1, 0):.0f} | {med(100, 0, 2):.0f}/{med(100, 1, 2):.0f} |")
            T = tot[b]
            T[0] += w
            T[1] += len(L) - w
            if l1t:
                T[2].append(l1u / l1t)
            if l2t:
                T[3].append(l2u / l2t)
    for b in bots:
        T = tot[b]
        if T[2]:
            print(f"| ALL | {b.split('/')[-1]} | {T[0]}-{T[1]} | mean ratio {st.mean(T[2]):.2f} | mean ratio {st.mean(T[3]):.2f} | | |")


if __name__ == "__main__":
    main()
