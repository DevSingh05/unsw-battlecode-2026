#!/usr/bin/env python3
"""adopt_audit.py CAND BASE OUT.jsonl [--jobs 3] [--seed 1000] [--maps a.map,b.map]: which known maps does CAND adopt?

CAND must be built with SPRINT_DEBUG=1 (stderr "ADOPT <name> id=.. team=.." / "DROP <name> ..."). Plays CAND as A and
as B against BASE on every map (--sandbox -v) and tallies CAND's adoptions and drops by map name, split into starting
dragons (round 0) and split children. A correct build adopts only the true map and never drops it.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/adopt_audit.py work/oct12/stage/kn2dbg variants/qf1 work/oct12/results/adopt.jsonl"""
import argparse
import collections
import concurrent.futures as cf
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
HDR = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) stderr:")
PTS = re.compile(r"^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)")
EV = re.compile(r"^(ADOPT|DROP) (.*) id=(\d+) team=([AB])$")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def play(mp, cand, base, side, seed):
    a, b = (cand, base) if side == "A" else (base, cand)
    p = subprocess.run(["unswbc", "run", str(ROOT / mp), str(ROOT / a), str(ROOT / b), "--seed", str(seed), "--sandbox",
                        "-v", "--no-replay"], capture_output=True, text=True, cwd=ROOT, errors="replace")
    rnd = 0
    ev = []
    mx = 0
    res = None
    for raw in (p.stdout + p.stderr).splitlines():
        l = ANSI.sub("", raw)
        m = PTS.match(l)
        if m:
            rnd = int(m.group(1))
            if m.group(3) == side:
                mx = max(mx, int(m.group(4)))
            continue
        m = EV.match(l)
        if m and m.group(4) == side:
            ev.append((rnd, m.group(1), m.group(2), int(m.group(3))))
            continue
        if l.startswith("team ") and " wins after " in l or l.startswith("draw after"):
            res = l
    return {"map": mp, "side": side, "seed": seed, "result": res, "max_pts": mx, "events": ev}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--maps", default=None)
    a = ap.parse_args()
    assert a.jobs <= 5
    maps = a.maps.split(",") if a.maps else (
        sorted(str(p.relative_to(ROOT)) for p in (ROOT / "maps/server_live31").glob("*.map"))
        + ["maps/schooltime_b.map", "maps/schooltime_b2.map", "maps/schooltime_b3.map"])
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex, open(out, "a") as f:
        futs = [ex.submit(play, mp, a.cand, a.base, s, a.seed) for mp in maps for s in "AB"]
        for fut in cf.as_completed(futs):
            r = fut.result()
            f.write(json.dumps(r) + "\n")
            f.flush()
            c = collections.Counter((e[1], e[2], "start" if e[0] == 0 else "child") for e in r["events"])
            print(f"{pathlib.Path(r['map']).stem:24s} {r['side']} max {r['max_pts'] / 1e6:5.1f}M  "
                  + ", ".join(f"{k[0]} {k[1]} ({k[2]}) x{v}" for k, v in sorted(c.items())) + f"  | {(r['result'] or '?')[:60]}",
                  flush=True)


if __name__ == "__main__":
    main()
