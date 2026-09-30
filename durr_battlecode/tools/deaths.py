#!/usr/bin/env python3
"""Summarise a replay: death causes per team, dragon counts and longest over time."""
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "notes" / "tools"))
from replay_decode import load  # noqa: E402


def summarise(path, verbose=False):
    o = load(path)
    team = {}
    i = 0
    for line in o["map"].splitlines():
        f = line.split()
        if f and f[0] == "DRAGON":
            team[i] = "AB"[int(f[1])]
            i += 1
    alive = {k: True for k in team}
    length = {}
    rnd = 0
    deaths = collections.Counter()
    timeline = []
    death_log = []
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
            if rnd % 50 == 0:
                a = sum(1 for k, v in alive.items() if v and team[k] == "A")
                b = sum(1 for k, v in alive.items() if v and team[k] == "B")
                timeline.append((rnd, a, b))
        elif t == "dragonSplit":
            team[e["child"]] = e["team"]
            alive[e["child"]] = True
        elif t == "dragonDeath":
            alive[e["id"]] = False
            deaths[(team[e["id"]], e["reason"])] += 1
            death_log.append((rnd, team[e["id"]], e["id"], e["reason"]))
    print(path, o["result"])
    for k in sorted(deaths):
        print("  ", k, deaths[k])
    print("   alive (round, A, B):", timeline)
    if verbose:
        for d in death_log:
            print("   ", d)


if __name__ == "__main__":
    v = "-v" in sys.argv
    for p in sys.argv[1:]:
        if p != "-v":
            summarise(p, v)
