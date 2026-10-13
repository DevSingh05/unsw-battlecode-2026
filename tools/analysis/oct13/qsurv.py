#!/usr/bin/env python3
"""qsurv.py RUN NAME: queen survival of the build whose directory name is NAME in a local run (work/oct12/results/RUN.jsonl),
next to its opponent's, per map: games won, queens alive at the end, median death round, median final length.
Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/qsurv.py t34_hide k8a"""
import collections
import json
import pathlib
import statistics as st
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_sim as RS  # noqa: E402


def fate(path):
    o = RS.R.load(path)
    m = RS.Map(o["map"])
    team = {i: "AB"[t] for i, (t, pts) in enumerate(m.dragons)}
    ln = {i: len(pts) for i, (t, pts) in enumerate(m.dragons)}
    body = {i: [tuple(p) for p in pts] for i, (t, pts) in enumerate(m.dragons)}
    out = {team[i]: {"death": None, "len": 0, "mode": None} for i in (0, 1)}
    rnd = 0
    actor = None
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            rnd = e["round"]
        elif t == "turnStart":
            actor = e["id"]
        elif t == "dragonUpdate" and e["id"] in (0, 1):
            b = body[e["id"]]
            h = tuple(e["head"])
            if b[0] != h:
                b.insert(0, h)
            tl = tuple(e["tail"])
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif t == "dragonSplit":
            if e["parent"] in (0, 1):
                body[e["parent"]] = [tuple(x) for x in e["parentBody"]]
            team[e["child"]] = e["team"]
        elif t == "dragonDeath" and e["id"] in (0, 1):
            i = e["id"]
            mode = e["reason"]
            if mode == "HitHeadToHead":
                mode = "rammed" if actor != i else "ran into a head"
            out[team[i]].update(death=rnd, mode=mode)
            body[i] = []
    for i in (0, 1):
        out[team[i]]["len"] = len(body[i])
    return out


def main():
    run, name = sys.argv[1], sys.argv[2]
    rows = [json.loads(l) for l in (ROOT / "work/oct12/results" / f"{run}.jsonl").read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r.get("replay") and (pathlib.Path(r["A"]).name == name or pathlib.Path(r["B"]).name == name)]
    with Pool(4) as pool:
        fates = pool.map(fate, [str(ROOT / r["replay"]) for r in rows])
    G = collections.defaultdict(list)
    for r, f in zip(rows, fates):
        me = "A" if pathlib.Path(r["A"]).name == name else "B"
        op = "B" if me == "A" else "A"
        mp = pathlib.Path(r["map"]).stem
        G[mp].append((r["result"].split()[1] == me, f[me], f[op]))
        G["ALL"].append((r["result"].split()[1] == me, f[me], f[op]))
    med = lambda v: f"{st.median(v):.0f}" if v else "-"
    print(f"| map | {name} W-L | {name} queen alive | median death round | modes | opponent queen alive | median death round |")
    print("|---|---|---|---|---|---|---|")
    for mp in sorted(G, key=lambda k: (k == "ALL", k)):
        L = G[mp]
        w = sum(x[0] for x in L)
        modes = collections.Counter(x[1]["mode"] for x in L if x[1]["death"] is not None)
        print(f"| {mp} | {w}-{len(L) - w} | {sum(x[1]['death'] is None for x in L)}/{len(L)} | {med([x[1]['death'] for x in L if x[1]['death'] is not None])} | "
              f"{dict(modes)} | {sum(x[2]['death'] is None for x in L)}/{len(L)} | {med([x[2]['death'] for x in L if x[2]['death'] is not None])} |")


if __name__ == "__main__":
    main()
