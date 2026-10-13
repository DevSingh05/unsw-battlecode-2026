#!/usr/bin/env python3
"""fog.py [--since UTC] [--min 8] [--maps "A,B"] [--jobs 2]: did our long dragons see the unit that lunged at them?

For every dragon of ours of --min+ segments killed by an enemy head that moved into it: where the killer's head was
when our dragon started its last move (inside its 7x7 view = Chebyshev distance <= 3 from the head, or outside), how
many steps our dragon took in that move, and whether the killer was in view of the END tile of that move (it has to
be, to aim at the head). Totals over all games, and the same for the opponents' long dragons that we killed.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/fog.py --since 2026-10-13T07:00:00"""
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

MINL = 8


def one(job):
    path, us = job
    try:
        o = RS.R.load(path)
        m = RS.Map(o["map"])
    except Exception:  # noqa: BLE001
        return None
    cheb = lambda a, b: max(min(abs(a[0] - b[0]), m.w - abs(a[0] - b[0])), min(abs(a[1] - b[1]), m.h - abs(a[1] - b[1])))
    body, team, alive = {}, {}, set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = [tuple(p) for p in pts]
        team[i] = "AB"[t]
        alive.add(i)
    last = {}  # id -> (round, head before its last move, {enemy id: head tile} within Chebyshev 8, steps so far)
    actor = None
    rnd = 0
    C = collections.Counter()
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
        elif t == "turnStart":
            actor = e["id"]
            if actor in body and actor in alive:
                h = body[actor][0]
                last[actor] = [rnd, h, {j: body[j][0] for j in alive if team[j] != team[actor] and cheb(body[j][0], h) <= 8}, 0, len(body[actor])]
        elif t == "dragonUpdate":
            i = e["id"]
            b = body[i]
            h = tuple(e["head"])
            if b[0] != h:
                b.insert(0, h)
                if i in last and last[i][0] == rnd:
                    last[i][3] += 1
            tl = tuple(e["tail"])
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif t == "dragonSplit":
            p, c = e["parent"], e["child"]
            body[p] = [tuple(x) for x in e["parentBody"]]
            body[c] = [tuple(x) for x in e["childBody"]]
            team[c] = e["team"] if e["team"] in ("A", "B") else "AB"[e["team"]]
            alive.add(c)
        elif t == "dragonDeath":
            i = e["id"]
            if e["reason"] == "HitHeadToHead" and i != actor and actor in team and team[actor] != team[i] and len(body[i]) >= MINL and i in last:
                side = "us" if team[i] == us else "th"
                r0, h0, seen, steps, _ = last[i]
                kpos = seen.get(actor)
                # the killer's head at the start of our last move (it may have been born since: then unknown)
                if rnd - r0 > 1:
                    C[(side, "stale")] += 1
                elif kpos is None:
                    C[(side, "killer further than 8 or not born")] += 1
                    C[(side, "unseen")] += 1
                else:
                    d0 = cheb(kpos, h0)
                    C[(side, "seen" if d0 <= 3 else "unseen")] += 1
                    C[(side, f"start dist {min(d0, 7)}")] += 1
                C[(side, f"our steps {min(steps, 4)}")] += 1
                C[(side, "n")] += 1
                if kpos is not None and cheb(kpos, h0) > 3:
                    C[(side, f"unseen, our steps {min(steps, 4)}")] += 1
            alive.discard(i)
    return dict(C)


def main():
    global MINL
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-13T07:00:00")
    ap.add_argument("--min", type=int, default=8)
    ap.add_argument("--maps", default="")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    MINL = a.min
    want = {x.strip() for x in a.maps.split(",") if x.strip()}
    jobs = []
    for f in glob.glob(str(ROOT / "work/oct12/watch/*.json")):
        d = json.load(open(f))
        mm = d["match"]
        if (mm["startedAt"] or mm["requestedAt"])[:19] < a.since:
            continue
        us = "A" if mm["teamAId"] == 952 else "B"
        for g in d["games"]:
            p = ROOT / "work/oct12/replays" / f"{g['id']}.replay"
            if g["status"] == "completed" and p.exists() and (not want or g["mapName"] in want):
                jobs.append((str(p), us))
    T = collections.Counter()
    with Pool(a.jobs) as pool:
        for r in pool.imap_unordered(one, jobs, chunksize=4):
            if r:
                T.update(r)
    print(f"{len(jobs)} games; dragons of {MINL}+ killed by an enemy head that moved into them")
    for side, name in (("us", "ours"), ("th", "theirs")):
        n = T[(side, "n")] or 1
        print(f"== {name}: {T[(side, 'n')]} deaths")
        print(f"   killer inside the victim's 7x7 view when the victim started its last move: {T[(side, 'seen')]} ({100 * T[(side, 'seen')] / n:.0f}%), outside: {T[(side, 'unseen')]} ({100 * T[(side, 'unseen')] / n:.0f}%), victim had not moved this round: {T[(side, 'stale')]}")
        print("   Chebyshev distance killer -> victim head at that moment: " + ", ".join(f"{k}: {T[(side, f'start dist {k}')]}" for k in range(1, 8)))
        print("   steps of the victim's last move: " + ", ".join(f"{k}: {T[(side, f'our steps {k}')]}" for k in range(0, 5)))
        print("   when the killer was outside the view, steps of the victim's last move: " + ", ".join(f"{k}: {T[(side, f'unseen, our steps {k}')]}" for k in range(0, 5)))


if __name__ == "__main__":
    main()
