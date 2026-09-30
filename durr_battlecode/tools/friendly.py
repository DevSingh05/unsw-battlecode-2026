#!/usr/bin/env python3
"""Count head-on collision types per team in replays: friendly (same team) vs cross-team."""
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "notes" / "tools"))
from replay_decode import load  # noqa: E402


def count(path):
    o = load(path)
    team, i = {}, 0
    for line in o["map"].splitlines():
        f = line.split()
        if f and f[0] == "DRAGON":
            team[i] = "AB"[int(f[1])]
            i += 1
    ev = [e for e in o["events"] if e["t"] != "tileChange"]
    c = collections.Counter()
    for k, e in enumerate(ev):
        if e["t"] == "dragonSplit":
            team[e["child"]] = e["team"]
        if (e["t"] == "dragonDeath" and e["reason"] == "HitHeadToHead" and k + 1 < len(ev)
                and ev[k + 1]["t"] == "dragonDeath"):
            a, b = team[e["id"]], team[ev[k + 1]["id"]]
            c[f"{a}{b}"] += 1
    return c


if __name__ == "__main__":
    tot = collections.Counter()
    for p in sys.argv[1:]:
        tot += count(p)
    print(dict(tot), "(AA = team A friendly, BB = team B friendly)")
