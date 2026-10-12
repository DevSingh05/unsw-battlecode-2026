#!/usr/bin/env python3
"""mech.py RUN [map-substring]: mechanism table for local games of work/oct12/results/RUN.jsonl (candidate = bot A in
*_A tags, bot B in *_B tags): pearls eaten, units and total length at r100/r300, deaths by cause, queen fate.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/mech.py t1_kn3_qf1 metro"""
import collections
import json
import pathlib
import re
import statistics as st
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
W = ROOT / "work" / "oct12"


def snap(g, r):
    best = g["rounds"][0][1]
    for rr, x in g["rounds"]:
        if rr <= r:
            best = x
        else:
            break
    return best


def one(a):
    tag, rp, seat = a
    import replay_sim as RS
    g = RS.simulate(str(ROOT / rp))
    out = {"tag": tag}
    for T, k in ((seat, "c"), ("B" if seat == "A" else "A", "b")):
        q = 0 if g["team"][0] == T else 1
        dq = next((d for d in g["deaths"] if d["id"] == q), None)
        D = [d for d in g["deaths"] if d["team"] == T]
        c = collections.Counter(d["reason"] for d in D)
        out[k] = {"eats": sum(1 for e in g["eats"] if e["team"] == T), "splits": sum(1 for x in g["splits"] if x["team"] == T),
                  "n100": snap(g, 100)[T]["n"], "tot100": snap(g, 100)[T]["total"], "n300": snap(g, 300)[T]["n"],
                  "tot300": snap(g, 300)[T]["total"], "max_end": g["rounds"][-1][1][T]["max"],
                  "q_dead": dq["round"] if dq else None, "q_mode": dq["reason"] if dq else None,
                  "q_end": g["rounds"][-1][1][T]["ids"].get(q, 0), "self": c["HitSelf"], "ally": c["HitOtherBody"],
                  "h2h": c["HitHeadToHead"], "wall": c["HitWall"], "nva": c["NoValidAction"], "lost": sum(d["len"] for d in D)}
    out["win"] = int(g["result"].get("winner") == seat)
    return out


def main():
    run = sys.argv[1]
    sub = sys.argv[2] if len(sys.argv) > 2 else ""
    todo = []
    for l in open(W / "results" / f"{run}.jsonl"):
        r = json.loads(l)
        if sub in r["tag"] and r.get("replay"):
            todo.append((r["tag"], r["replay"], r["tag"][-1]))
    with Pool(3) as P:
        rows = P.map(one, todo)
    by = collections.defaultdict(list)
    for r in rows:
        by[re.sub(r"_\d+_[AB]$", "", r["tag"])].append(r)
    f = lambda L, k, s: f"{st.mean([x[s][k] for x in L]):.0f}"
    print("| map | W-L | eats c/b | units r100 c/b | total r100 c/b | total r300 c/b | longest end c/b | queen alive end c/b | "
          "queen death round c/b (median) | deaths self/ally/h2h/wall c | deaths self/ally/h2h/wall b | length lost c/b |")
    print("|" + "---|" * 12)
    for mp, L in sorted(by.items()):
        qd = lambda s: (lambda v: f"{st.median(v):.0f}" if v else "-")([x[s]["q_dead"] for x in L if x[s]["q_dead"] is not None])
        print(f"| {mp} | {sum(x['win'] for x in L)}-{len(L) - sum(x['win'] for x in L)} | {f(L, 'eats', 'c')}/{f(L, 'eats', 'b')} | "
              f"{f(L, 'n100', 'c')}/{f(L, 'n100', 'b')} | {f(L, 'tot100', 'c')}/{f(L, 'tot100', 'b')} | {f(L, 'tot300', 'c')}/{f(L, 'tot300', 'b')} | "
              f"{f(L, 'max_end', 'c')}/{f(L, 'max_end', 'b')} | {sum(1 for x in L if x['c']['q_dead'] is None)}/{sum(1 for x in L if x['b']['q_dead'] is None)} of {len(L)} | "
              f"{qd('c')}/{qd('b')} | {f(L, 'self', 'c')}/{f(L, 'ally', 'c')}/{f(L, 'h2h', 'c')}/{f(L, 'wall', 'c')} | "
              f"{f(L, 'self', 'b')}/{f(L, 'ally', 'b')}/{f(L, 'h2h', 'b')}/{f(L, 'wall', 'b')} | {f(L, 'lost', 'c')}/{f(L, 'lost', 'b')} |")


if __name__ == "__main__":
    main()
