#!/usr/bin/env python3
"""feedleak.py [--since UTC] [--maps "A,B"] [--from 250] [--jobs 2]: where the pearls of our own late suicides go.

For every dragon that dies by its own doing (HitSelf / NoValidAction) from round --from on: its length, and who eats
each pearl its body leaves: the side's longest dragon at that moment (or one at least 70% as long: a "king"), another
unit of the same side, or the ENEMY. Per map and side, mean per game: self-deaths, length given up, pearls eaten by a
king / by other own units / by the enemy, and the side's total length at r300 and at the end.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/feedleak.py --since 2026-10-13T21:25:37"""
import argparse
import collections
import glob
import json
import pathlib
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402

FROM = 250


def one(job):
    path, us, mp, win = job
    try:
        g = RS.simulate(path)
    except Exception:  # noqa: BLE001
        return None
    snaps = dict(g["rounds"])
    selfdead = {}
    C = collections.Counter()
    for d in g["deaths"]:
        if d["reason"] in ("HitSelf", "NoValidAction") and d["round"] >= FROM:
            selfdead[d["id"]] = d["team"]
            T = "us" if d["team"] == us else "th"
            C[(T, "n")] += 1
            C[(T, "len")] += d["len"]
    for e in g["eats"]:
        c = e["corpse"]
        if not c or c[0] not in selfdead:
            continue
        owner = selfdead[c[0]]
        T = "us" if owner == us else "th"
        if e["team"] != owner:
            C[(T, "enemy")] += 1
            continue
        snap = snaps.get(e["round"]) or snaps.get(e["round"] - 1) or {}
        mx = (snap.get(owner) or {}).get("max", 0)
        C[(T, "king" if (e["len"] or 0) >= max(8, 0.7 * mx) else "own")] += 1
    for T, L in (("us", us), ("th", "B" if us == "A" else "A")):
        C[(T, "tot300")] = (snaps.get(300) or {}).get(L, {}).get("total", 0)
        C[(T, "totend")] = g["rounds"][-1][1][L]["total"]
        C[(T, "maxend")] = g["rounds"][-1][1][L]["max"]
    return mp, win, dict(C)


def main():
    global FROM
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T21:25:37")
    ap.add_argument("--maps", default="")
    ap.add_argument("--from", dest="frm", type=int, default=250)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--local", default="", help="a local run (work/oct12/results/RUN.jsonl) instead of the server games")
    ap.add_argument("--bot", default="", help="with --local: path suffix of the build reported as 'us'")
    a = ap.parse_args()
    FROM = a.frm
    want = {x.strip() for x in a.maps.split(",") if x.strip()}
    jobs = []
    if a.local:
        for line in open(ROOT / "work/oct12/results" / f"{a.local}.jsonl"):
            r = json.loads(line)
            if not r.get("replay") or "wins" not in (r.get("result") or ""):
                continue
            us = "A" if r["A"].endswith(a.bot) else ("B" if r["B"].endswith(a.bot) else None)
            mp = pathlib.Path(r["map"]).stem
            if us and (not want or mp in want):
                jobs.append((str(ROOT / r["replay"]), us, mp, r["result"].startswith(f"team {us} wins")))
    for f in ([] if a.local else glob.glob(str(ROOT / "work/oct12/watch/*.json"))):
        d = json.load(open(f))
        mm = d["match"]
        if (mm["startedAt"] or mm["requestedAt"])[:19] < a.since:
            continue
        us = "A" if mm["teamAId"] == 952 else "B"
        for g in d["games"]:
            p = ROOT / "work/oct12/replays" / f"{g['id']}.replay"
            if g["status"] == "completed" and p.exists() and (not want or g["mapName"] in want):
                jobs.append((str(p), us, g["mapName"], g["winner"] == us.lower()))
    with Pool(a.jobs) as pool:
        res = [r for r in pool.imap_unordered(one, jobs, chunksize=4) if r]
    by = collections.defaultdict(list)
    for mp, win, c in res:
        by[mp].append((win, c))
        by["ALL"].append((win, c))
    mean = lambda L, k: sum(c.get(k, 0) for _, c in L) / len(L)
    print(f"{len(res)} games; own deaths (HitSelf / no action) from r{FROM}; means per game, ours / theirs")
    print("| map | games | W-L | self-deaths | length given up | pearls eaten by a king | by other own units | by the ENEMY | total r300 | total at the end | longest at the end |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for mp in sorted(by, key=lambda m: -mean(by[m], ("us", "enemy"))):
        L = by[mp]
        w = sum(1 for x, _ in L if x)
        cell = lambda k: f"{mean(L, ('us', k)):.0f}/{mean(L, ('th', k)):.0f}"
        print(f"| {mp} | {len(L)} | {w}-{len(L) - w} | {cell('n')} | {cell('len')} | {cell('king')} | {cell('own')} | {cell('enemy')} | {cell('tot300')} | {cell('totend')} | {cell('maxend')} |")


if __name__ == "__main__":
    main()
