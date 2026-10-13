#!/usr/bin/env python3
"""traffic.py [--jobs 4] [--step 3]: where is a queen out of lunge range? Enemy-traffic maps from every cached server replay.

For each replay (work/oct12/replays/*.replay, work/top3_oct12/*/replays/*.replay) and each side, every STEP-th round
from r30: a tile is "lunge-exposed" when some enemy head can reach it this round (path distance through open edges
and portals <= reach, reach = ceil(L/4) free steps + L-2 paid steps, capped at 8; bodies ignored). The view of the team that holds
queen 1 is mirrored onto queen 0's side with the map symmetry (the server swaps the teams' sides between games), so both
sides of a game count as one "home side" sample.

Writes work/oct13/traffic/<map>.json: {w, h, n (samples), lunge[tile], near[tile] (enemy head within 3 steps),
qocc[tile] (queen rounds there), qocc_alive[tile] (same, queens alive at the end), spawn (queen 0's start), lost[tile] / nl (lunge counts and samples
for the side that lost the game), early[tile] / ne (rounds before 200)}
and work/oct13/traffic/queens.json: one row per game and side (map, death round or null, share of her rounds that her
head tile was lunge-exposed / near, mean steps from her spawn, final length, gid).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/traffic.py --jobs 4"""
import argparse
import collections
import json
import pathlib
import re
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402

OUT = ROOT / "work" / "oct13" / "traffic"
STEP = 3
FIRST = 30
CAP = 8


def reach(L):
    return min(CAP, (L + 3) // 4 + max(0, L - 2))


def graph(m):
    idx = lambda p: p[1] * m.w + p[0]
    nb = [[] for _ in range(m.w * m.h)]
    for y in range(m.h):
        for x in range(m.w):
            for d in "NESW":
                q = m.step((x, y), d)
                if q is not None:
                    nb[idx((x, y))].append(idx(q))
    return nb


def symmetry(m):
    """Tile permutation that maps team B's start onto team A's (the map symmetry), as a list tile -> tile."""
    A = [pts for t, pts in m.dragons if t == 0]
    B = [pts for t, pts in m.dragons if t == 1]
    sa = {tuple(p) for pts in A for p in pts}
    for f in (lambda x, y: (m.w - 1 - x, m.h - 1 - y), lambda x, y: (m.w - 1 - x, y), lambda x, y: (x, m.h - 1 - y)):
        if {f(*p) for pts in B for p in pts} == sa:
            return [f(t % m.w, t // m.w)[1] * m.w + f(t % m.w, t // m.w)[0] for t in range(m.w * m.h)]
    return None


def bfs_from(nb, src, limit=10 ** 9):
    dist = {src: 0}
    q = collections.deque([src])
    while q:
        t = q.popleft()
        if dist[t] >= limit:
            continue
        for u in nb[t]:
            if u not in dist:
                dist[u] = dist[t] + 1
                q.append(u)
    return dist


def exposure(nb, heads):
    """heads: [(tile, length)] -> (set of lunge-exposed tiles, set of tiles within 3 steps of a head)."""
    best = {}
    buckets = [[] for _ in range(CAP + 1)]
    for t, L in heads:
        r = reach(L)
        if best.get(t, -1) < r:
            best[t] = r
            buckets[r].append(t)
    for r in range(CAP, 0, -1):
        for t in buckets[r]:
            if best[t] != r:
                continue
            for u in nb[t]:
                if best.get(u, -1) < r - 1:
                    best[u] = r - 1
                    buckets[r - 1].append(u)
    near = {}
    q = collections.deque()
    for t, _ in heads:
        if t not in near:
            near[t] = 0
            q.append(t)
    while q:
        t = q.popleft()
        if near[t] >= 3:
            continue
        for u in nb[t]:
            if u not in near:
                near[u] = near[t] + 1
                q.append(u)
    return set(best), set(near)


def one(path):
    try:
        o = RS.R.load(path)
        m = RS.Map(o["map"])
    except Exception as e:  # noqa: BLE001
        return {"error": repr(e), "path": path}
    sig = symmetry(m)
    if sig is None:
        return {"error": "no symmetry", "path": path}
    N = m.w * m.h
    idx = lambda p: p[1] * m.w + p[0]
    nb = graph(m)
    body, team, alive = {}, {}, set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = [tuple(p) for p in pts]
        team[i] = "AB"[t]
        alive.add(i)
    qid = {team[i]: i for i in (0, 1)}  # the queens are ids 0 and 1; which team holds which depends on the map file
    # The server swaps the teams' sides between games, so "home side" is normalised on the dragon ids, not the team
    # letters: the team that holds queen 0 is counted as is, the team that holds queen 1 is mirrored onto queen 0's side.
    spawn0 = idx(body[0][0])
    dsp = bfs_from(nb, spawn0)
    lunge = [0] * N
    near = [0] * N
    qocc = [0] * N
    n = 0
    mw = re.search(r"'winner': '([AB])'", str(o.get("result")))
    winner = mw.group(1) if mw else None
    lost = [0] * N   # same as lunge, only for the side that lost the game
    early = [0] * N  # same as lunge, only rounds before 200
    nl = ne_ = 0
    qrow = {T: {"rounds": 0, "lunge": 0, "near": 0, "dist": 0, "death": None, "len": 0, "tiles": collections.Counter()} for T in "AB"}
    rnd = 0

    def sample():
        nonlocal n, nl, ne_
        for T in "AB":
            E = "B" if T == "A" else "A"
            heads = [(idx(body[i][0]), len(body[i])) for i in alive if team[i] == E]
            lu, ne = exposure(nb, heads) if heads else (set(), set())
            n += 1
            isl = winner is not None and winner != T
            ise = rnd < 200
            nl += isl
            ne_ += ise
            ident = qid[T] == 0
            for t in lu:
                tn = t if ident else sig[t]
                lunge[tn] += 1
                if isl:
                    lost[tn] += 1
                if ise:
                    early[tn] += 1
            for t in ne:
                near[t if ident else sig[t]] += 1
            q = qid[T]
            if q in alive:
                h = idx(body[q][0])
                hn = h if ident else sig[h]
                r = qrow[T]
                r["rounds"] += 1
                r["lunge"] += h in lu
                r["near"] += h in ne
                r["dist"] += dsp.get(hn, 99)
                r["tiles"][hn] += 1
                qocc[hn] += 1

    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            if rnd >= FIRST and rnd % STEP == 0:
                sample()
            rnd = e["round"]
        elif t == "dragonUpdate":
            b = body[e["id"]]
            h = tuple(e["head"])
            if b[0] != h:
                b.insert(0, h)
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
            alive.discard(i)
            for T in "AB":
                if qid[T] == i:
                    qrow[T]["death"] = rnd
    gid = pathlib.Path(path).stem
    rows = []
    for T in "AB":
        r = qrow[T]
        q = qid[T]
        rows.append({"map": m.name, "gid": gid, "side": T, "death": r["death"], "rounds": r["rounds"],
                     "lunge": r["lunge"] / r["rounds"] if r["rounds"] else None, "near": r["near"] / r["rounds"] if r["rounds"] else None,
                     "dist": r["dist"] / r["rounds"] if r["rounds"] else None, "len": len(body[q]) if q in alive else 0,
                     "last": rnd, "won": winner == T, "tiles": dict(r["tiles"])})
    return {"map": m.name, "w": m.w, "h": m.h, "n": n, "lunge": lunge, "near": near, "qocc": qocc, "spawn": spawn0, "rows": rows,
            "lost": lost, "early": early, "nl": nl, "ne": ne_}


def main():
    global STEP
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--old", type=int, default=0, help="also read up to this many replays from each older server folder under replays/")
    a = ap.parse_args()
    STEP = a.step
    src = list((ROOT / "work/oct12/replays").glob("*.replay")) + list((ROOT / "work/top3_oct12").glob("*/replays/*.replay"))
    if a.old:
        # older server games (5 Oct on, current rules, the 17 older maps): our A/B test games and the top-team studies
        cut = 1791158400  # 2026-10-05 00:00 UTC
        for d in ("ab_mech", "opp_oct6", "top4_ftm", "ftm_oct5", "top_oct6", "top4_horse", "top4_aaah", "vib_oct5", "top4_cutlery", "devtest"):
            L = sorted(p for p in (ROOT / "replays" / d).rglob("*.replay") if p.stat().st_mtime >= cut)
            src += L[:: max(1, len(L) // a.old)] if len(L) > a.old else L
    paths = sorted({p.stem: str(p) for p in src}.values())
    if a.limit:
        paths = paths[:: max(1, len(paths) // a.limit)]
    OUT.mkdir(parents=True, exist_ok=True)
    agg = {}
    queens = []
    bad = 0
    with Pool(a.jobs) as pool:
        for k, r in enumerate(pool.imap_unordered(one, paths, chunksize=4)):
            if "error" in r:
                bad += 1
                continue
            g = agg.setdefault(r["map"], {"w": r["w"], "h": r["h"], "n": 0, "games": 0, "spawn": r["spawn"], "lunge": [0] * len(r["lunge"]),
                                          "near": [0] * len(r["lunge"]), "qocc": [0] * len(r["lunge"]), "qocc_alive": [0] * len(r["lunge"]),
                                          "lost": [0] * len(r["lunge"]), "early": [0] * len(r["lunge"]), "nl": 0, "ne": 0})
            g["n"] += r["n"]
            g["games"] += 1
            g["nl"] += r["nl"]
            g["ne"] += r["ne"]
            for key in ("lunge", "near", "qocc", "lost", "early"):
                src, dst = r[key], g[key]
                for i, v in enumerate(src):
                    if v:
                        dst[i] += v
            for row in r["rows"]:
                if row["death"] is None:
                    for t, v in row["tiles"].items():
                        g["qocc_alive"][int(t)] += v
                row.pop("tiles")
                queens.append(row)
            if k % 100 == 99:
                print(f"{k + 1}/{len(paths)}", flush=True)
    for mp, g in agg.items():
        (OUT / f"{mp.replace(' ', '_')}.json").write_text(json.dumps(g))
    (OUT / "queens.json").write_text(json.dumps(queens))
    print(f"{len(paths)} replays, {bad} unreadable, {len(agg)} maps -> {OUT}")


if __name__ == "__main__":
    main()
