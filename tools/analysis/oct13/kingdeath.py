#!/usr/bin/env python3
"""kingdeath.py [--since UTC] [--min 30] [--from 300] [--jobs 2]: how each side's long dragons die late.

For every death of a dragon of --min+ segments from round --from on, in our cached server games: the cause (boxed =
HitSelf / own-team body / no action; enemy head moved into it; walked into an enemy head or body), its length and how
many free neighbours its head had. Per map: deaths and length lost per game for us and for the opponents, and the
number of games in which our LONGEST dragon of the moment died boxed in the last 60 rounds.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/kingdeath.py --since 2026-10-13T17:34:00"""
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

MINL, FROM = 30, 300


def one(job):
    path, us, mp, win = job
    try:
        g = RS.simulate(path)
    except Exception:  # noqa: BLE001
        return None
    C = collections.Counter()
    snaps = dict(g["rounds"])
    for d in g["deaths"]:
        if d["len"] < MINL or d["round"] < FROM:
            continue
        T = "us" if d["team"] == us else "th"
        r = d["reason"]
        if r in ("HitSelf", "NoValidAction") or (r == "HitOtherBody" and (d.get("hit") or {}).get("team") == d["team"]):
            k = "boxed"
        elif r == "HitHeadToHead" and d.get("killer") is not None and d.get("killer_team") != d["team"]:
            k = "rammed"
        else:
            k = "walked"
        C[(T, k, "n")] += 1
        C[(T, k, "len")] += d["len"]
        snap = snaps.get(d["round"] - 1) or snaps.get(d["round"]) or {}
        mx = (snap.get(d["team"]) or {}).get("max", 0)
        if d["len"] >= mx - 2 and d["round"] >= 440:
            C[(T, k, "king_last60")] += 1
    return mp, win, dict(C)


def main():
    global MINL, FROM
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T17:34:00")
    ap.add_argument("--min", type=int, default=30)
    ap.add_argument("--from", dest="frm", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    MINL, FROM = a.min, a.frm
    jobs = []
    for f in glob.glob(str(ROOT / "work/oct12/watch/*.json")):
        d = json.load(open(f))
        mm = d["match"]
        if (mm["startedAt"] or mm["requestedAt"])[:19] < a.since:
            continue
        us = "A" if mm["teamAId"] == 952 else "B"
        for g in d["games"]:
            p = ROOT / "work/oct12/replays" / f"{g['id']}.replay"
            if g["status"] == "completed" and p.exists():
                jobs.append((str(p), us, g["mapName"], g["winner"] == us.lower()))
    with Pool(a.jobs) as pool:
        res = [r for r in pool.imap_unordered(one, jobs, chunksize=4) if r]
    by = collections.defaultdict(list)
    for mp, win, c in res:
        by[mp].append((win, c))
        by["ALL"].append((win, c))
    print(f"{len(res)} games; dragons of {MINL}+ dying from r{FROM}; per game means; 'king' = the side's longest at that moment, dying from r440")
    print("| map | games | boxed us/them: deaths, length | rammed us/them: deaths, length | walked into something us/them | games with our king boxed late (lost) | their king boxed late | our king rammed late (lost) |")
    print("|---|---|---|---|---|---|---|---|")
    mean = lambda L, k: sum(c.get(k, 0) for _, c in L) / len(L)
    for mp in sorted(by, key=lambda m: -mean(by[m], ("us", "boxed", "len"))):
        L = by[mp]
        kb = [(w, c) for w, c in L if c.get(("us", "boxed", "king_last60"))]
        kr = [(w, c) for w, c in L if c.get(("us", "rammed", "king_last60"))]
        tb = [(w, c) for w, c in L if c.get(("th", "boxed", "king_last60"))]
        print(f"| {mp} | {len(L)} | {mean(L, ('us', 'boxed', 'n')):.1f}/{mean(L, ('th', 'boxed', 'n')):.1f}, {mean(L, ('us', 'boxed', 'len')):.0f}/{mean(L, ('th', 'boxed', 'len')):.0f} | "
              f"{mean(L, ('us', 'rammed', 'n')):.1f}/{mean(L, ('th', 'rammed', 'n')):.1f}, {mean(L, ('us', 'rammed', 'len')):.0f}/{mean(L, ('th', 'rammed', 'len')):.0f} | "
              f"{mean(L, ('us', 'walked', 'n')):.1f}/{mean(L, ('th', 'walked', 'n')):.1f} | {len(kb)} ({sum(1 for w, _ in kb if not w)}) | {len(tb)} | {len(kr)} ({sum(1 for w, _ in kr if not w)}) |")


if __name__ == "__main__":
    main()
