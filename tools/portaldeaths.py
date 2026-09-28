#!/usr/bin/env python3
"""Mechanism metrics for a challenge batch: per map, our vs their deaths per game, split into
fatal portal crossings and newborn portal-neck deaths, plus units alive at r200.

usage: portaldeaths.py replays/ab_v18 [replays/ab_v16_dt ...]   (dirs written by collect.py)
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "notes/tools/midgame"))
sys.path.insert(0, str(ROOT / "notes/tools"))
from sim2 import simulate  # noqa: E402
import replay_decode as R  # noqa: E402


def our_side(res, us):
    for s in "AB":
        if res[s] == us:
            return s
    return None


def main():
    for d in sys.argv[1:]:
        d = pathlib.Path(d)
        summ = {g["id"]: g for g in json.loads((d / "summary.json").read_text())}
        agg = collections.defaultdict(collections.Counter)
        for gid, g in summ.items():
            p = d / f"{gid}.replay"
            if not p.exists():
                continue
            side = our_side(R.load(str(p))["result"], g["us"])
            if side is None:
                continue
            G = simulate(str(p))
            m = G["map"]
            c = agg[g["map"]]
            c["games"] += 1
            c["wins"] += bool(g["win"])
            for dd in G["deaths"]:
                who = "us" if dd["team"] == side else "them"
                c[who + "_deaths"] += 1
                mv = dd.get("move")
                if not mv:
                    continue
                k = dd.get("step_failed", 1) - 1
                s = mv[k]
                if m.edges.get(m.side_edge(dd["head"], s), (0, -1))[0] == 2:
                    c[who + "_portal"] += 1
                    if dd["reason"] == "HitSelf" and dd["age"] == 0 and len(dd["body"]) > 1 and m.step(dd["head"], s) == dd["body"][1]:
                        c[who + "_newborn"] += 1
        print(f"== {d}")
        for mp, c in sorted(agg.items()):
            n = c["games"]
            print(f"  {mp:18s} W {c['wins']}/{n}  deaths/g us {c['us_deaths']/n:5.1f} them {c['them_deaths']/n:5.1f}"
                  f"  portal/g us {c['us_portal']/n:5.1f} them {c['them_portal']/n:5.1f}"
                  f"  newborn/g us {c['us_newborn']/n:4.1f}")


if __name__ == "__main__":
    main()
