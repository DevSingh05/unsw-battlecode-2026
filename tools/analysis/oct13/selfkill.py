#!/usr/bin/env python3
"""selfkill.py [--since UTC] [--jobs 4] [--maps "A,B"] [--local RUN [--bot SUFFIX]]: how many of our own units die without an enemy, per map.

For every cached server replay of ours (work/oct12/replays/<gid>.replay, sides from work/oct12/watch/) since --since:
deaths by HitSelf / HitOtherBody on an ally / NoValidAction / head-on with an ally, for us and for the opponent, in the
bins r0-99, r100-249 and r250-499, next to the unit counts at r100. Median per map over the games.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/selfkill.py --since 2026-10-13T00:00:00"""
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

BINS = ((0, 100), (100, 250), (250, 500))


def one(job):
    gid, us, mp, win, opp = job
    try:
        g = RS.simulate(gid if str(gid).endswith(".replay") else str(ROOT / "work" / "oct12" / "replays" / f"{gid}.replay"))
    except Exception as e:  # noqa: BLE001
        return None
    out = {"gid": gid, "map": mp, "win": win, "opp": opp}
    for T, tag in ((us, "us"), ("B" if us == "A" else "A", "th")):
        c = collections.Counter()
        for d in g["deaths"]:
            if d["team"] != T:
                continue
            r = d["reason"]
            if r == "HitSelf":
                k = "self"
            elif r == "NoValidAction":
                k = "noact"
            elif r == "HitOtherBody":
                k = "body_ally" if (d.get("hit") or {}).get("team") == T else "body_enemy"
            elif r == "HitHeadToHead":
                kt = d.get("killer_team") or d.get("victim_team")
                k = "h2h_ally" if kt == T else "h2h_enemy"
            else:
                k = "other"
            for bi, (lo, hi) in enumerate(BINS):
                if lo <= d["round"] < hi:
                    c[(k, bi)] += 1
                    c[(k + "_len", bi)] += d["len"]
        out[tag] = {f"{k}{b}": v for (k, b), v in c.items()}
        snap = dict(g["rounds"])
        r100 = snap.get(100) or {}
        out[tag]["n100"] = (r100.get(T) or {}).get("n", 0)
        out[tag]["tot100"] = (r100.get(T) or {}).get("total", 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T00:00:00")
    ap.add_argument("--until", default="9999")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--maps", default="")
    ap.add_argument("--opp", default="")
    ap.add_argument("--local", default="", help="a local run (work/oct12/results/RUN.jsonl) instead of the server games; --bot picks our side by path suffix")
    ap.add_argument("--bot", default="", help="with --local: the build to report as 'us' (path suffix, e.g. stage/km12); default = the side named in the tag")
    a = ap.parse_args()
    want = {x.strip() for x in a.maps.split(",") if x.strip()}
    jobs = []
    if a.local:
        for line in open(ROOT / "work/oct12/results" / f"{a.local}.jsonl"):
            r = json.loads(line)
            if not r.get("replay") or "wins" not in (r.get("result") or ""):
                continue
            us = r["tag"][-1] if r["tag"][-1] in "AB" else "A"
            if a.bot:
                us = "A" if r["A"].endswith(a.bot) else ("B" if r["B"].endswith(a.bot) else None)
                if us is None:
                    continue
            mp = pathlib.Path(r["map"]).stem
            if want and mp not in want:
                continue
            jobs.append((str(ROOT / r["replay"]), us, mp, r["result"].startswith(f"team {us} wins"), r["B" if us == "A" else "A"]))
    for f in ([] if a.local else glob.glob(str(ROOT / "work/oct12/watch/*.json"))):
        d = json.load(open(f))
        m = d["match"]
        at = (m["startedAt"] or m["requestedAt"])[:19]
        if at < a.since or at >= a.until:
            continue
        us = "A" if m["teamAId"] == 952 else "B"
        opp = d["teamBName"] if us == "A" else d["teamAName"]
        if a.opp and a.opp not in opp:
            continue
        for g in d["games"]:
            if g["status"] != "completed" or (want and g["mapName"] not in want):
                continue
            if (ROOT / "work/oct12/replays" / f"{g['id']}.replay").exists():
                jobs.append((g["id"], us, g["mapName"], g["winner"] == us.lower(), opp))
    with Pool(a.jobs) as pool:
        rows = [r for r in pool.imap_unordered(one, jobs, chunksize=4) if r]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["map"]].append(r)
    med = lambda L, tag, k: st.median([r[tag].get(k, 0) for r in L])
    print(f"{len(rows)} games since {a.since}. Deaths without an enemy = HitSelf + own body + NoValidAction + head-on with an ally; median per game.")
    print("| map | games | W-L | units r100 us/them | length r100 us/them | no-enemy deaths r0-99 us/them | r100-249 us/them | r250-499 us/them | enemy-caused r0-99 us/them |")
    print("|---|---|---|---|---|---|---|---|---|")
    def tot(r, tag, b):
        return sum(r[tag].get(f"{k}{b}", 0) for k in ("self", "noact", "body_ally", "h2h_ally"))
    def en(r, tag, b):
        return sum(r[tag].get(f"{k}{b}", 0) for k in ("body_enemy", "h2h_enemy"))
    for mp in sorted(by, key=lambda m: st.median([tot(r, "us", 0) - tot(r, "th", 0) for r in by[m]]), reverse=True):
        L = by[mp]
        w = sum(r["win"] for r in L)
        cell = lambda f, b: f"{st.median([f(r, 'us', b) for r in L]):.0f}/{st.median([f(r, 'th', b) for r in L]):.0f}"
        print(f"| {mp} | {len(L)} | {w}-{len(L) - w} | {med(L, 'us', 'n100'):.0f}/{med(L, 'th', 'n100'):.0f} | {med(L, 'us', 'tot100'):.0f}/{med(L, 'th', 'tot100'):.0f} | "
              f"{cell(tot, 0)} | {cell(tot, 1)} | {cell(tot, 2)} | {cell(en, 0)} |")


if __name__ == "__main__":
    main()
