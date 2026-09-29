#!/usr/bin/env python3
"""Per-window mass ledger, W vs L (notes/23).  python3 notes/tools/bigboard/window.py [maps...]
Uses deathctx.pkl (per-death, all rounds) and games.pkl eats (per 100 rounds only) -> windows of 100 from collect,
and deathctx for finer death windows."""
import collections, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import GS, BIG, STRONG, tlv, mean
H = os.path.dirname(os.path.abspath(__file__))
DC = {g['game']: g for g in pickle.load(open(os.path.join(H, 'deathctx.pkl'), 'rb'))}
def selfinf(c): return not (c.startswith('rammed') or c.startswith('ram_enemy') or c == 'killed_other')
maps = sys.argv[1:] or BIG
sub = [g for g in GS if g['map'] in maps and g['top'] and g['game'] in DC]
for wl in (True, False):
    S = [g for g in sub if g['win'] == wl]
    print('== win=%s n=%d' % (wl, len(S)))
    print('  window   | units us/them (start->end) | splits us/them | selfinf deaths | headon deaths | selfinf len | mean L at split us/them | child k>=3 share')
    for a, b in ((0, 25), (25, 50), (50, 75), (75, 100), (100, 150), (150, 200), (200, 300)):
        row = []
        for tag in ('us', 'them'):
            sp = [s for g in S for s in DC[g['game']]['splits'] if s['tag'] == tag and a <= s['round'] < b]
            ds = [d for g in S for d in DC[g['game']]['deaths'] if d['tag'] == tag and a <= d['round'] < b]
            si = [d for d in ds if selfinf(d['cls'])]; ho = [d for d in ds if not selfinf(d['cls'])]
            row.append((mean(tlv(g, tag, max(1, a))[0] for g in S), mean(tlv(g, tag, b)[0] for g in S), len(sp) / len(S), len(si) / len(S), len(ho) / len(S),
                        sum(d['len'] for d in si) / len(S), mean(s['L'] for s in sp), mean(s['k'] >= 3 for s in sp)))
        u, t = row
        print('  r%3d-%3d | %4.1f->%4.1f / %4.1f->%4.1f | %5.1f/%5.1f | %5.1f/%5.1f | %4.1f/%4.1f | %5.1f/%5.1f | %.2f/%.2f | %.2f/%.2f' % (
            a, b, u[0], u[1], t[0], t[1], u[2], t[2], u[3], t[3], u[4], t[4], u[5], t[5], u[6], t[6], u[7], t[7]))
