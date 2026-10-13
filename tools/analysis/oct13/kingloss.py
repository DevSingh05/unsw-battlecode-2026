#!/usr/bin/env python3
"""kingloss.py GID SIDE [--min 20]: how the long dragons of one side lose their length in one server replay.

For every dragon of SIDE (A or B) that reaches --min segments: birth round, peak length and round, and every event that
took 3+ segments from it at once (a split with the child's length, a move with paid steps, its death with the cause).
Then, per 100-round bin, the length the side's dragons of --min+ lost to splits, to paid steps and to deaths.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/kingloss.py 1863290 A"""
import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gid")
    ap.add_argument("side")
    ap.add_argument("--min", type=int, default=20)
    ap.add_argument("-q", action="store_true", help="only the per-bin summary")
    a = ap.parse_args()
    p = pathlib.Path(a.gid) if a.gid.endswith(".replay") else ROOT / "work" / "oct12" / "replays" / f"{a.gid}.replay"
    g = RS.simulate(str(p))
    T = a.side
    peak = collections.defaultdict(lambda: (0, 0))
    for rnd, snap in g["rounds"]:
        for i, L in snap[T]["ids"].items():
            if L > peak[i][0]:
                peak[i] = (L, rnd)
    big = {i for i, (L, _) in peak.items() if L >= a.min}
    ev = collections.defaultdict(list)
    bins = collections.defaultdict(lambda: collections.Counter())
    for s in g["splits"]:
        if s["parent"] in big and s["L"] >= a.min:
            ev[s["parent"]].append((s["round"], f"split L{s['L']} -> child {s['k']} (exits {s['exits']}, enemy head {s['enemy_dist']} away, units {s['units_before']})"))
            bins[s["round"] // 100]["split"] += s["k"]
    for mv in g["moves"]:
        if mv["id"] in big and mv["len_before"] >= a.min and not mv.get("suicide"):
            lost = mv["len_before"] + mv["ate"] - mv["len_after"]
            if mv["len_after"] and lost > 0:
                bins[mv["round"] // 100]["paid"] += lost
                if lost >= 3:
                    ev[mv["id"]].append((mv["round"], f"paid {lost} (L{mv['len_before']} -> {mv['len_after']}, {mv['steps']} steps, ate {mv['ate']}, enemy head {mv['near_enemy_head'][0] if mv['near_enemy_head'] else '-'} away)"))
    for d in g["deaths"]:
        if d["id"] in big and d["team"] == T:
            why = d["reason"]
            if why == "HitHeadToHead":
                why += f" killer L{d.get('killer_len')}" if d.get("killer") is not None else f" (moved into L{d.get('victim_len')})"
            ev[d["id"]].append((d["round"], f"DIED L{d['len']} {why} nbrs {d['nbrs']}"))
            if d["len"] >= a.min:
                bins[d["round"] // 100]["death:" + d["reason"]] += d["len"]
    if not a.q:
        for i in sorted(big, key=lambda i: peak[i][1]):
            print(f"id {i} born r{g['born'][i]} peak L{peak[i][0]} at r{peak[i][1]}")
            for r, s in sorted(ev[i]):
                print(f"    r{r} {s}")
    print("length lost by dragons of", a.min, "+ per 100 rounds:")
    for b in sorted(bins):
        print(f"  r{b * 100}-{b * 100 + 99}: " + ", ".join(f"{k} {v}" for k, v in sorted(bins[b].items())))


if __name__ == "__main__":
    main()
