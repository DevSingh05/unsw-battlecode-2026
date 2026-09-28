"""Median longest-dragon / unit-count / total-length curves (every 25 rounds) per map, winner vs loser.
Reads the sim caches built by permap_analyze.py (dedupes deterministic re-runs the same way).
Usage: python3 permap_curves.py"""
import os, sys, glob, json, pickle, statistics as st
from collections import defaultdict
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/permap')
idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
bym = defaultdict(list); seen = set()
for f in sorted(glob.glob(os.path.join(RD, '*.replay.sim.pkl'))):
    mid = int(os.path.basename(f).split('.')[0]); g = pickle.load(open(f, 'rb'))
    W = g['result']['winner']
    if W not in ('A', 'B'): continue
    sig = (idx[mid]['mapName'], idx[mid]['a']['id'], idx[mid]['b']['id'], g['last_round'], len(g['eats']), len(g['splits']))
    if sig in seen: continue
    seen.add(sig); bym[idx[mid]['mapName']].append((g, W, 'B' if W == 'A' else 'A'))
R = list(range(25, 500, 25)) + [499]
def at(g, r):
    b = None
    for rr, s in g['rounds']:
        if rr <= r: b = s
        else: break
    return b if r <= g['last_round'] else None
for mp, G in bym.items():
    print(f'\n== {mp} ({len(G)} games)  rounds {R}')
    for lab, k in (('max', 'max'), ('units', 'n'), ('total', 'total')):
        for side in (1, 2):
            v = []
            for r in R:
                xs = [at(g, r)[t[side]][k] for t in G for g in [t[0]] if at(g, r)]
                v.append(st.median(xs) if xs else '-')
            print(f"  {'W' if side == 1 else 'L'} {lab:5s} {v}  (n alive games@499: {sum(1 for t in G if t[0]['last_round'] >= 499)})" if lab == 'max' and side == 1 else f"  {'W' if side == 1 else 'L'} {lab:5s} {v}")
