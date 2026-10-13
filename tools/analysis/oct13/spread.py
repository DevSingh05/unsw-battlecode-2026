#!/usr/bin/env python3
"""spread.py REPLAY US [REPLAY US ...]: how each side spreads and harvests early in one or more replays.

Per checkpoint (r25, r50, r75, r100, r150) and side: units, total length, distinct tiles any head has stood on so far,
mean and 90th-percentile plain+portal steps of the heads from the side's queen start, pearls eaten so far that were not
corpse pearls, portal crossings so far, and moves so far that used more than one step.
US = the team letter (A or B) to print first. Replay = a path or a server game id (work/oct12/replays/<id>.replay).

With --local RUN SUFFIX [SUFFIX ...]: medians over a local run (work/oct12/results/RUN.jsonl) for each build whose path
ends with SUFFIX, next to its opponents.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/spread.py 1861675 A
    python3 tools/analysis/oct13/spread.py --local t72_nodive stage/nd1"""
import collections
import pathlib
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "analysis" / "oct13"))
import replay_sim as RS  # noqa: E402
import traffic as TR  # noqa: E402

CK = (25, 50, 75, 100, 150)


def one(path, us):
    o = RS.R.load(path)
    m = RS.Map(o["map"])
    nb = TR.graph(m)
    idx = lambda p: p[1] * m.w + p[0]
    body, team, alive = {}, {}, set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = [tuple(p) for p in pts]
        team[i] = "AB"[t]
        alive.add(i)
    qsp = {team[i]: idx(body[i][0]) for i in (0, 1)}
    dist = {T: TR.bfs_from(nb, qsp[T]) for T in "AB"}
    seen = {T: set() for T in "AB"}
    S = {T: collections.Counter() for T in "AB"}
    corpse = set()
    rnd = 0
    actor = None
    steps = 0
    out = {}

    def snap():
        for T in "AB":
            hs = [idx(body[i][0]) for i in alive if team[i] == T]
            d = sorted(dist[T].get(h, 99) for h in hs) or [0]
            out[(rnd, T)] = (len(hs), sum(len(body[i]) for i in alive if team[i] == T), len(seen[T]), st.mean(d), d[int(0.9 * (len(d) - 1))],
                             S[T]["new"], S[T]["portal"], S[T]["multi"], S[T]["corpse"])

    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            if rnd in CK:
                snap()
            rnd = e["round"]
            if rnd > CK[-1] + 1:
                break
        elif t == "turnStart":
            actor = e["id"]
            steps = 0
        elif t == "dragonUpdate":
            i = e["id"]
            b = body[i]
            h = tuple(e["head"])
            if b[0] != h:
                old = b[0]
                b.insert(0, h)
                seen[team[i]].add(idx(h))
                steps += 1
                if steps == 2:
                    S[team[i]]["multi"] += 1
                if h != m.wrap(old[0] + 1, old[1]) and h != m.wrap(old[0] - 1, old[1]) and h != m.wrap(old[0], old[1] + 1) and h != m.wrap(old[0], old[1] - 1):
                    S[team[i]]["portal"] += 1
            tl = tuple(e["tail"])
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif t == "tileChange":
            tile = tuple(e["tile"])
            if not e["hasPearl"]:
                if actor in team:
                    S[team[actor]]["corpse" if tile in corpse else "new"] += 1
                corpse.discard(tile)
        elif t == "dragonSplit":
            p, c = e["parent"], e["child"]
            body[p] = [tuple(x) for x in e["parentBody"]]
            body[c] = [tuple(x) for x in e["childBody"]]
            team[c] = e["team"] if e["team"] in ("A", "B") else "AB"[e["team"]]
            alive.add(c)
        elif t == "dragonDeath":
            i = e["id"]
            for s in body[i]:
                corpse.add(s)
            alive.discard(i)
    return m.name, out


def local(run, bot):
    """Median over a local run's games of the checkpoint rows, for the build whose path ends with bot and for its opponent."""
    import json
    rows = collections.defaultdict(list)
    for line in open(ROOT / "work/oct12/results" / f"{run}.jsonl"):
        r = json.loads(line)
        if not r.get("replay") or "wins" not in (r.get("result") or ""):
            continue
        us = "A" if r["A"].endswith(bot) else ("B" if r["B"].endswith(bot) else None)
        if us is None:
            continue
        _, out = one(str(ROOT / r["replay"]), us)
        for (rd, T), v in out.items():
            rows[(rd, "us" if T == us else "them")].append(v)
        rows[("win", "us")].append(r["result"].startswith(f"team {us} wins"))
    n = len(rows[("win", "us")])
    print(f"== {run} {bot}: {n} games, {sum(rows[('win', 'us')])}-{n - sum(rows[('win', 'us')])}; medians")
    print("| round | side | units | length | tiles visited | mean steps from start | 90th pct | new pearls | corpse pearls | portal crossings | multi-step moves |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for rd in CK:
        for side in ("us", "them"):
            L = rows.get((rd, side))
            if L:
                med = [st.median(x[k] for x in L) for k in range(9)]
                print(f"| {rd} | {side} | {med[0]:.0f} | {med[1]:.0f} | {med[2]:.0f} | {med[3]:.1f} | {med[4]:.0f} | {med[5]:.0f} | {med[8]:.0f} | {med[6]:.0f} | {med[7]:.0f} |")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--local":
        for bot in args[2:]:
            local(args[1], bot)
        return
    for k in range(0, len(args), 2):
        gid, us = args[k], args[k + 1]
        p = gid if gid.endswith(".replay") else str(ROOT / "work/oct12/replays" / f"{gid}.replay")
        name, out = one(p, us)
        print(f"== {gid} {name}: us = team {us}")
        print("| round | side | units | length | tiles visited | mean steps from start | 90th pct | new pearls | corpse pearls | portal crossings | multi-step moves |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in CK:
            for T in (us, "B" if us == "A" else "A"):
                if (r, T) in out:
                    n, tot, seen, md, p90, new, por, mul, cor = out[(r, T)]
                    print(f"| {r} | {'us' if T == us else 'them'} | {n} | {tot} | {seen} | {md:.1f} | {p90} | {new} | {cor} | {por} | {mul} |")


if __name__ == "__main__":
    main()
