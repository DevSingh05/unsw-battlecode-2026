#!/usr/bin/env python3
"""feedwho.py GID US [FROM TO]: who eats the pearls dropped next to each queen.

For each side: own-team dragons that die by their own doing (HitSelf / NoValidAction) within 8 map steps of their
queen's head in rounds FROM..TO, the pearls their bodies leave, and who eats each of those pearls: the queen, another
unit of the same team (with its length), or the enemy; plus pearls never eaten. US = our team letter.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/feedwho.py 1861674 A 250 450"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402


def run(path, us, lo, hi):
    g = RS.simulate(path)
    m = g["map"]
    qid = {g["team"][0]: 0, g["team"][1]: 1}
    qpos = {0: {}, 1: {}}
    for mv in g["moves"]:
        if mv["id"] in (0, 1):
            qpos[mv["id"]][mv["round"]] = tuple(mv["head"])
    fed = {}  # tile -> (team, round)
    C = {T: collections.Counter() for T in "AB"}
    for d in g["deaths"]:
        if d["reason"] not in ("HitSelf", "NoValidAction") or not lo <= d["round"] < hi or d["id"] in (0, 1):
            continue
        T = d["team"]
        q = qpos[qid[T]].get(d["round"]) or qpos[qid[T]].get(d["round"] - 1)
        if q is None or m.dist(tuple(d["head"]), q) > 8:
            continue
        C[T]["feeders"] += 1
        C[T]["feeder_len"] += d["len"]
    # pearls: use the eat records' corpse field (dead id, team, round, L)
    dead_near = {}
    for d in g["deaths"]:
        if d["reason"] in ("HitSelf", "NoValidAction") and lo <= d["round"] < hi and d["id"] not in (0, 1):
            T = d["team"]
            q = qpos[qid[T]].get(d["round"]) or qpos[qid[T]].get(d["round"] - 1)
            if q is not None and m.dist(tuple(d["head"]), q) <= 8:
                dead_near[d["id"]] = T
    lens = collections.defaultdict(list)
    for e in g["eats"]:
        c = e["corpse"]
        if not c or c[0] not in dead_near:
            continue
        T = dead_near[c[0]]
        if e["id"] == qid[T]:
            C[T]["eaten_by_queen"] += 1
        elif e["team"] == T:
            C[T]["eaten_by_own_unit"] += 1
            lens[T].append(e["len"] or 0)
        else:
            C[T]["eaten_by_enemy"] += 1
    for T in ((us, "B" if us == "A" else "A")):
        c = C[T]
        L = sorted(lens[T])
        print(f"{'us  ' if T == us else 'them'}: {c['feeders']} own deaths within 8 steps of the queen (length {c['feeder_len']}); their pearls eaten by the queen {c['eaten_by_queen']}, "
              f"by other own units {c['eaten_by_own_unit']} (median eater length {L[len(L) // 2] if L else '-'}), by the enemy {c['eaten_by_enemy']}")


if __name__ == "__main__":
    gid, us = sys.argv[1], sys.argv[2]
    lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (250, 450)
    run(gid if gid.endswith(".replay") else str(ROOT / "work/oct12/replays" / f"{gid}.replay"), us, lo, hi)
