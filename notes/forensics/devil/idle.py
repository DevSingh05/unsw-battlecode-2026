#!/usr/bin/env python3
"""Idle heads vs uneaten hub food, rounds R0..R1 (default 20..100).
  idle%   = share of our (their) head-rounds spent OUTSIDE the hub (x 12..19) with no eat in the last 8 rounds
  hubfood = mean number of pearls lying in the hub at round start
  idle&food = our idle head-rounds while >= 8 pearls lay uneaten in the hub
    python3 notes/forensics/devil/idle.py [R0 R1]
"""
import sys, collections
from common import games, sim, GDIR
sys.path.insert(0, __import__('os').path.join(__import__('common').ROOT, 'notes/tools'))
import replay_decode as RD
import os

R0 = int(sys.argv[1]) if len(sys.argv) > 1 else 20
R1 = int(sys.argv[2]) if len(sys.argv) > 2 else 100
inhub = lambda t: 12 <= t[0] <= 19


def pearls_per_round(gid):
    o = RD.load(os.path.join(GDIR, '%d.replay' % gid))
    P = set(); rnd = 0; out = {}
    for e in o['events']:
        if e['t'] == 'roundStart':
            out[rnd] = sum(1 for t in P if inhub(t)); rnd = e['round']
        elif e['t'] == 'tileChange':
            (P.add if e['hasPearl'] else P.discard)(e['tile'])
    return out


agg = collections.defaultdict(list)
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']; them = 'B' if us == 'A' else 'A'
    snap = dict(S['rounds']); hp = pearls_per_round(g['game'])
    last = collections.defaultdict(int)
    eats = collections.defaultdict(list)
    for e in S['eats']: eats[e['round']].append(e)
    tot = collections.Counter(); idle = collections.Counter(); idlefood = 0; food = []
    for r in range(1, R1 + 1):
        for e in eats[r]: last[e['id']] = r
        if r < R0 or r not in snap: continue
        food.append(hp.get(r, 0))
        for j, (h, L, T) in snap[r]['heads'].items():
            tot[T] += 1
            if not inhub(h) and r - max(last[j], S['born'].get(j, 0)) >= 8:
                idle[T] += 1
                if T == us and hp.get(r, 0) >= 8: idlefood += 1
    res = 'W' if g['win'] else 'L'
    f = sum(food) / max(1, len(food))
    agg[res].append((idle[us] / max(1, tot[us]), idle[them] / max(1, tot[them]), f, idlefood, tot[us]))
    print('%d %-12s %s idle%% us %4.0f%% (%4d of %4d)  them %4.0f%% | hubfood %4.1f | our idle while >=8 hub pearls: %d' % (
        g['game'], g['opp'][:12], res, 100 * idle[us] / max(1, tot[us]), idle[us], tot[us], 100 * idle[them] / max(1, tot[them]), f, idlefood))
for res, L in agg.items():
    n = len(L)
    print(res, n, 'mean idle us %.0f%% them %.0f%% hubfood %.1f idle&food %.0f' % (100 * sum(a[0] for a in L) / n, 100 * sum(a[1] for a in L) / n, sum(a[2] for a in L) / n, sum(a[3] for a in L) / n))
