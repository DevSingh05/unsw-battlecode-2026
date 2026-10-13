#!/usr/bin/env python3
"""badsplit.py [--since UTC] [--maps "A,B"] [--local RUN --bot SUFFIX] [--until 250]: splits that lose one half at once.

A split is "bad" when the parent or the child dies within 2 rounds of it by HitSelf / own-team body / NoValidAction.
Splits are sorted by where the parent's head stood: in the core, or inside a dead-end pocket (leaf-pruned tiles of
the map graph; there the lost front half is the planned price of a dive). Per map: games, splits per game before
--until, bad splits with the head in the core (ours / theirs), bad splits inside a pocket (ours / theirs), and for
ours in the core which half died and how many free neighbours the parent's head had before the split.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/badsplit.py --since 2026-10-13T07:00:00 --maps "Around UNSW,Australia" """
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
sys.path.insert(0, str(ROOT / "tools" / "analysis" / "oct13"))
import replay_sim as RS  # noqa: E402
import traffic as TR  # noqa: E402

UNTIL = 250


def pockets(m):
    nb = [list(dict.fromkeys(x)) for x in TR.graph(m)]
    deg = [len([v for v in nb[t] if v != t]) for t in range(len(nb))]
    pk = [False] * len(nb)
    q = [t for t in range(len(nb)) if deg[t] <= 1]
    i = 0
    while i < len(q):
        t = q[i]
        i += 1
        if pk[t]:
            continue
        pk[t] = True
        for v in nb[t]:
            if v != t and not pk[v]:
                deg[v] -= 1
                if deg[v] == 1:
                    q.append(v)
    return pk


def one(job):
    path, us, mp = job
    try:
        g = RS.simulate(path)
    except Exception:  # noqa: BLE001
        return None
    m = g["map"]
    pk = pockets(m)
    idx = lambda p: p[1] * m.w + p[0]
    dead = {}
    for d in g["deaths"]:
        own = d["reason"] in ("HitSelf", "NoValidAction") or (d["reason"] == "HitOtherBody" and (d.get("hit") or {}).get("team") == d["team"])
        if own:
            dead[d["id"]] = (d["round"], d["head"])
    C = collections.Counter()
    for s in g["splits"]:
        if s["round"] >= UNTIL:
            continue
        T = "us" if s["team"] == us else "th"
        C[(T, "splits")] += 1
        hit = [k for k in ("parent", "child") if s[k] in dead and 0 <= dead[s[k]][0] - s["round"] <= 2]
        if not hit:
            continue
        # where did the dying half die: the parent's head at the split is not stored, so use the death tile of the parent
        # (it moves at most 2 tiles) or, for a dead child, the child's death tile
        where = "pocket" if pk[idx(tuple(dead[s[hit[0]]][1]))] else "core"
        C[(T, "bad_" + where)] += 1
        C[(T, "bad_" + where + "_" + hit[0])] += 1
        if where == "core" or True:
            C[(T, f"exits{min(s['exits'], 3)}_{where}")] += 1
    return mp, dict(C)


def main():
    global UNTIL
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T07:00:00")
    ap.add_argument("--maps", default="")
    ap.add_argument("--local", default="")
    ap.add_argument("--bot", default="")
    ap.add_argument("--until", type=int, default=250)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    UNTIL = a.until
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
    print(f"{len(res)} games; medians per game, rounds 0-{UNTIL - 1}")
    print("| map | games | splits us/them | bad, died in the core us/them | bad, died in a pocket us/them | ours in the core: parent/child died | ours: head exits before the split 0/1/2/3+ (all bad) |")
    print("|---|---|---|---|---|---|---|")
    med = lambda L, k: st.median([c.get(k, 0) for c in L])
    tot = lambda L, k: sum(c.get(k, 0) for c in L)
    for mp in sorted(by, key=lambda m: -med(by[m], ("us", "bad_core"))):
        L = by[mp]
        ex = "/".join(str(tot(L, ("us", f"exits{e}_core")) + tot(L, ("us", f"exits{e}_pocket"))) for e in range(4))
        print(f"| {mp} | {len(L)} | {med(L, ('us', 'splits')):.0f}/{med(L, ('th', 'splits')):.0f} | {med(L, ('us', 'bad_core')):.0f}/{med(L, ('th', 'bad_core')):.0f} | "
              f"{med(L, ('us', 'bad_pocket')):.0f}/{med(L, ('th', 'bad_pocket')):.0f} | {tot(L, ('us', 'bad_core_parent'))}/{tot(L, ('us', 'bad_core_child'))} | {ex} |")


if __name__ == "__main__":
    main()
