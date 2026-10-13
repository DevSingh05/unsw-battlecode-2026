#!/usr/bin/env python3
"""qfate.py [--since UTC] [--ranked] [--jobs 4]: both queens' fate per map in our cached server games.

Per map: games, W-L, the four end states (our queen alive or dead x theirs alive or dead) with our wins in each, the
median round their queen died in, and how far (map steps) their queen's head was from her start tile on average while
she lived (a queen that sits at home can be found there).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/qfate.py --since 2026-10-13T03:12:00"""
import argparse
import collections
import glob
import json
import pathlib
import statistics as st
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402


def one(job):
    path, us, mp, win = job
    try:
        g = RS.simulate(path)
    except Exception:  # noqa: BLE001
        return None
    m = g["map"]
    qid = {g["team"][0]: 0, g["team"][1]: 1}
    th = "B" if us == "A" else "A"
    death = {d["id"]: d["round"] for d in g["deaths"] if d["id"] in (0, 1)}
    sp = tuple(m.dragons[qid[th]][1][0])
    ds = [m.dist(tuple(mv["head"]), sp) for mv in g["moves"] if mv["id"] == qid[th] and mv["round"] >= 50]
    return {"map": mp, "win": win, "us_dead": death.get(qid[us]), "th_dead": death.get(qid[th]), "th_home": st.mean(ds) if ds else None,
            "last": g["last_round"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T03:12:00")
    ap.add_argument("--ranked", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    jobs = []
    for f in glob.glob(str(ROOT / "work/oct12/watch/*.json")):
        d = json.load(open(f))
        mm = d["match"]
        if (mm["startedAt"] or mm["requestedAt"])[:19] < a.since or (a.ranked and not mm["ranked"]):
            continue
        us = "A" if mm["teamAId"] == 952 else "B"
        for g in d["games"]:
            p = ROOT / "work/oct12/replays" / f"{g['id']}.replay"
            if g["status"] == "completed" and p.exists():
                jobs.append((str(p), us, g["mapName"], g["winner"] == us.lower()))
    with Pool(a.jobs) as pool:
        res = [r for r in pool.imap_unordered(one, jobs, chunksize=4) if r]
    by = collections.defaultdict(list)
    for r in res:
        by[r["map"]].append(r)
        by["ALL"].append(r)
    print(f"{len(res)} games since {a.since}{' (ranked only)' if a.ranked else ''}; each cell = games (our wins)")
    print("| map | games | W-L | ours alive, theirs dead | both alive | both dead | ours dead, theirs alive | their queen dies (median round) | their queen's mean steps from her start |")
    print("|---|---|---|---|---|---|---|---|---|")
    for mp in sorted(by, key=lambda m: -sum(1 for r in by[m] if r["us_dead"] is not None and r["th_dead"] is None) / len(by[m])):
        L = by[mp]
        cell = lambda ud, td: (lambda S: f"{len(S)} ({sum(r['win'] for r in S)})")([r for r in L if (r["us_dead"] is not None) == ud and (r["th_dead"] is not None) == td])
        td = [r["th_dead"] for r in L if r["th_dead"] is not None]
        hm = [r["th_home"] for r in L if r["th_home"] is not None]
        w = sum(r["win"] for r in L)
        print(f"| {mp} | {len(L)} | {w}-{len(L) - w} | {cell(False, True)} | {cell(False, False)} | {cell(True, True)} | {cell(True, False)} | {st.median(td) if td else '-'} | {st.mean(hm) if hm else 0:.0f} |")


if __name__ == "__main__":
    main()
