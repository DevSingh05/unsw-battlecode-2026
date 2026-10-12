#!/usr/bin/env python3
"""score.py RUN [RUN...]: per-map score of the candidate (the bot that is A in *_A tags and B in *_B tags) from
work/oct12/results/RUN.jsonl. Pairs = same map and seed, both seats: 2-0 / 1-1 / 0-2. A 1-1 pair where the same seat
won both games is seat-decided (no information).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/score.py t1_kn3_qf1"""
import collections
import json
import math
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[3] / "work" / "oct12"
rows = {}
for run in sys.argv[1:]:
    for l in open(W / "results" / f"{run}.jsonl"):
        r = json.loads(l)
        if r.get("result"):
            rows[r["tag"]] = r
by = collections.defaultdict(dict)
for tag, r in rows.items():
    m = re.match(r"^(.*)_(\d+)_([AB])$", tag)
    mp, seed, seat = m.group(1), m.group(2), m.group(3)
    w = re.match(r"team ([AB]) wins", r["result"])
    by[(mp, seed)][seat] = (1 if w and w.group(1) == seat else 0, r["result"])
tot = collections.Counter()
pm = collections.defaultdict(lambda: [0, 0, 0, 0, 0])  # wins, games, 2-0, 1-1, 0-2
mx = 0.0
for (mp, seed), d in sorted(by.items()):
    for seat, (w, _) in d.items():
        pm[mp][0] += w
        pm[mp][1] += 1
    if len(d) == 2:
        s = d["A"][0] + d["B"][0]
        pm[mp][2 + (2 - s)] += 1
print(f"{'map':26s} W-L    pairs 2-0/1-1/0-2")
W_ = G = P2 = P1 = P0 = 0
for mp, (w, g, a, b, c) in sorted(pm.items()):
    print(f"{mp:26s} {w}-{g - w:<4d} {a}/{b}/{c}")
    W_ += w; G += g; P2 += a; P1 += b; P0 += c
p = W_ / max(G, 1)
se = math.sqrt(p * (1 - p) / max(G, 1))
# sign test on discordant pairs (2-0 vs 0-2)
n = P2 + P0
pv = sum(math.comb(n, k) for k in range(max(P2, P0), n + 1)) / 2 ** n * 2 if n else 1.0
print(f"TOTAL {W_}-{G - W_} = {p:.3f} (+-{1.96 * se:.3f}); pairs 2-0 {P2}, 1-1 {P1}, 0-2 {P0}; sign test on discordant pairs p={min(pv, 1):.3f}")
for run in sys.argv[1:]:
    for l in open(W / "results" / f"{run}.jsonl"):
        r = json.loads(l)
        for T in "AB":
            mx = max(mx, (r.get("summary") or {}).get(T, {}).get("max", 0))
print(f"max CPU points per turn over all bots: {mx:.1f}M")
