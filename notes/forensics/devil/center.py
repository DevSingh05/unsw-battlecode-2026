#!/usr/bin/env python3
"""Centre presence per round: heads of us/them in the hub (x 12..19) and in the 4 hot pockets
(Ctop 15-16 y0-2, Cbot 15-16 y13-15, tube14 x14 y5-10, tube17 x17 y5-10), sampled every 5 rounds.
    python3 notes/forensics/devil/center.py [GAME...]
"""
import sys
from common import games, sim


def where(t):
    x, y = t
    if x in (15, 16) and y <= 2: return 'T'
    if x in (15, 16) and y >= 13: return 'B'
    if x in (14, 17) and 5 <= y <= 10: return 'C'
    if 12 <= x <= 19: return 'h'
    return None


G = {g['game']: g for g in games()}
ids = [int(a) for a in sys.argv[1:]] or sorted(G)
for gid in ids:
    g = G[gid]; S = sim(gid); us = g['side']
    out = []
    for r, s in S['rounds']:
        if r % 5 or r > 80: continue
        cu = ct = ''
        for j, (h, L, T) in s['heads'].items():
            w = where(h)
            if not w: continue
            if T == us: cu += w
            else: ct += w
        out.append('%d:%s/%s' % (r, ''.join(sorted(cu)) or '-', ''.join(sorted(ct)) or '-'))
    print(gid, g['opp'][:12], 'W' if g['win'] else 'L', ' '.join(out))
