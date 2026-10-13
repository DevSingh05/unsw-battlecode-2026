#!/usr/bin/env python3
"""bigdeaths.py [--since UTC] [--maps "A,B"] [--min 8] [--local RUN --bot SUFFIX]: how our long dragons die to enemy heads.

For every death of a dragon of --min+ segments by a head-on in which the enemy moved (it rammed us): the number of
steps of the killing move (1 = it stood next to our head, 2+ = a lunge), the killer's length, and whether the victim
was the team's longest. Also the reverse (we ram theirs), and per game the length each side loses this way and to
head-ons the long dragon itself walked into. Median per game and totals.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/bigdeaths.py --since 2026-10-13T07:00:00"""
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

MINL = 8


def one(job):
    path, us, mp = job
    try:
        g = RS.simulate(path)
    except Exception:  # noqa: BLE001
        return None
    steps = {}
    for mv in g["moves"]:
        steps[(mv["round"], mv["id"])] = (mv["steps"], mv["len_before"])
    C = collections.Counter()
    for d in g["deaths"]:
        if d["len"] < MINL or d["reason"] != "HitHeadToHead":
            continue
        T = "us" if d["team"] == us else "th"
        if d.get("killer") is not None and d.get("killer_team") != d["team"]:
            n, kl = steps.get((d["round"], d["killer"]), (0, d.get("killer_len") or 0))
            C[(T, "rammed", "n")] += 1
            C[(T, "rammed", "len")] += d["len"]
            C[(T, "rammed", f"steps{min(n, 4)}")] += 1
            C[(T, "rammed", f"klen{min(kl, 6)}")] += 1
            C[(T, "rammed", "phase" + str(min(d["round"] // 100, 4)))] += d["len"]
        elif d.get("victim") is not None and d.get("victim_team") != d["team"]:
            C[(T, "walked", "n")] += 1
            C[(T, "walked", "len")] += d["len"]
    snap = dict(g["rounds"])
    for T, L in (("us", us), ("th", "B" if us == "A" else "A")):
        C[(T, "tot300", "")] = (snap.get(300) or {}).get(L, {}).get("total", 0)
    return mp, dict(C)


def main():
    global MINL
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T07:00:00")
    ap.add_argument("--maps", default="")
    ap.add_argument("--min", type=int, default=8)
    ap.add_argument("--local", default="")
    ap.add_argument("--bot", default="")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    MINL = a.min
    want = {x.strip() for x in a.maps.split(",") if x.strip()}
    jobs = []
    if a.local:
        for line in open(ROOT / "work/oct12/results" / f"{a.local}.jsonl"):
            r = json.loads(line)
            if not r.get("replay") or "wins" not in (r.get("result") or ""):
                continue
            us = "A" if r["A"].endswith(a.bot) else ("B" if r["B"].endswith(a.bot) else None)
            if us:
                jobs.append((str(ROOT / r["replay"]), us, pathlib.Path(r["map"]).stem))
    else:
        for f in glob.glob(str(ROOT / "work/oct12/watch/*.json")):
            d = json.load(open(f))
            mm = d["match"]
            if (mm["startedAt"] or mm["requestedAt"])[:19] < a.since:
                continue
            us = "A" if mm["teamAId"] == 952 else "B"
            for g in d["games"]:
                p = ROOT / "work/oct12/replays" / f"{g['id']}.replay"
                if g["status"] == "completed" and p.exists() and (not want or g["mapName"] in want):
                    jobs.append((str(p), us, g["mapName"]))
    with Pool(a.jobs) as pool:
        res = [r for r in pool.imap_unordered(one, jobs, chunksize=4) if r]
    by = collections.defaultdict(list)
    for mp, c in res:
        by[mp].append(c)
        by["ALL"].append(c)
    med = lambda L, k: st.median([c.get(k, 0) for c in L])
    tot = lambda L, k: sum(c.get(k, 0) for c in L)
    print(f"{len(res)} games; dragons of {MINL}+ segments killed by an enemy head that moved into them (median per game)")
    print("| map | games | deaths us/them | length lost us/them | total length r300 us/them | ours: killer steps 1/2/3/4+ | ours: killer length 2/3/4/5/6+ | ours also walked into a head: n, length |")
    print("|---|---|---|---|---|---|---|---|")
    for mp in sorted(by, key=lambda m: -med(by[m], ("us", "rammed", "len"))):
        L = by[mp]
        stp = "/".join(str(tot(L, ("us", "rammed", f"steps{k}"))) for k in (1, 2, 3, 4))
        kl = "/".join(str(tot(L, ("us", "rammed", f"klen{k}"))) for k in (2, 3, 4, 5, 6))
        print(f"| {mp} | {len(L)} | {med(L, ('us', 'rammed', 'n')):.0f}/{med(L, ('th', 'rammed', 'n')):.0f} | {med(L, ('us', 'rammed', 'len')):.0f}/{med(L, ('th', 'rammed', 'len')):.0f} | "
              f"{med(L, ('us', 'tot300', '')):.0f}/{med(L, ('th', 'tot300', '')):.0f} | {stp} | {kl} | {med(L, ('us', 'walked', 'n')):.0f}, {med(L, ('us', 'walked', 'len')):.0f} |")


if __name__ == "__main__":
    main()
