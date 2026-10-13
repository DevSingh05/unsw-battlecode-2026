#!/usr/bin/env python3
"""hotspots.py [--era qf1|km|all]: death hot-spots per map from our server replays in work/oct12/replays.

For every map: tiles (5x5 blocks and single tiles) where OUR dragons die far more often than the opponents' do, with
the death causes, plus pearls eaten per game for both sides. It found the Troll Australia trap rooms after the fact;
the point is to screen the other maps for the same kind of categorical leak.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/hotspots.py --era qf1"""
import argparse
import collections
import glob
import json
import pathlib
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
W = ROOT / "work" / "oct12"
T_KM = "2026-10-12T19:19:00"


def load_games():
    G = {}
    for r in json.loads((W / "games_recent.json").read_text()):
        G[r["gid"]] = (r["side"].upper(), r["map"], r["at"][:19], r["win"])
    for f in glob.glob(str(W / "watch" / "*.json")):
        d = json.loads(pathlib.Path(f).read_text())
        m = d["match"]
        us = "A" if m["teamAId"] == 952 else "B"
        for g in d["games"]:
            if g["status"] == "completed" and g["winner"] in ("a", "b"):
                G[g["id"]] = (us, g["mapName"], (m["startedAt"] or m["requestedAt"])[:19], int(g["winner"] == us.lower()))
    return G


def one(a):
    gid, us = a
    import replay_sim as RS
    try:
        g = RS.simulate(str(W / "replays" / f"{gid}.replay"))
    except Exception:  # noqa: BLE001
        return None
    out = {"gid": gid, "us": [], "th": [], "eu": 0, "et": 0}
    for d in g["deaths"]:
        (out["us"] if d["team"] == us else out["th"]).append((d["head"][0], d["head"][1], d["len"], d["reason"], d["round"]))
    for e in g["eats"]:
        if e["team"] == us:
            out["eu"] += 1
        else:
            out["et"] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era", default="all")
    a = ap.parse_args()
    G = load_games()
    todo = []
    for gid, (us, mp, at, win) in G.items():
        if not (W / "replays" / f"{gid}.replay").exists():
            continue
        era = "km" if at >= T_KM else "qf1"
        if a.era != "all" and era != a.era:
            continue
        todo.append((gid, us))
    with Pool(3) as P:
        res = [r for r in P.map(one, todo, chunksize=4) if r]
    by = collections.defaultdict(list)
    for r in res:
        by[G[r["gid"]][1]].append(r)
    for mp, L in sorted(by.items()):
        n = len(L)
        if n < 5:
            continue
        wins = sum(G[r["gid"]][3] for r in L)
        ut = collections.Counter()
        tt = collections.Counter()
        ul = collections.Counter()
        cause = collections.defaultdict(collections.Counter)
        for r in L:
            for x, y, ln, why, rd in r["us"]:
                ut[(x, y)] += 1
                ul[(x, y)] += ln
                cause[(x, y)][why] += 1
            for x, y, ln, why, rd in r["th"]:
                tt[(x, y)] += 1
        totu = sum(ut.values()) / n
        tott = sum(tt.values()) / n
        hot = [(c / n, t) for t, c in ut.items() if c / n >= 1.0 and c >= 3 * max(tt[t], 1)]
        hot.sort(reverse=True)
        print(f"== {mp}: {n} games, {wins}-{n - wins}; deaths/game us {totu:.0f} them {tott:.0f}; eats/game us "
              f"{sum(r['eu'] for r in L) / n:.0f} them {sum(r['et'] for r in L) / n:.0f}")
        for c, t in hot[:8]:
            print(f"     tile {t}: our deaths {c:.1f}/game ({ul[t] / n:.1f} length), theirs {tt[t] / n:.1f}/game; causes {dict(cause[t].most_common(3))}")


if __name__ == "__main__":
    main()
