#!/usr/bin/env python3
"""Per map, top-15 games, r0-299: fresh income (spawn + enemy corpse eats), burn (own death length - own corpse
re-eaten), retention = 1 - burn/fresh, and win rate (notes/23).  python3 notes/tools/bigboard/retention.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import GS, mean, tlv

def f(g, tag):
    E = g[tag]['eats']
    fresh = sum(v for k, v in E.items() if k[0] < 3 and k[2] in ('spawn', 'enemy'))
    own = sum(v for k, v in E.items() if k[0] < 3 and k[2] == 'own')
    dl = sum(d[1] for d in g[tag]['deaths'] if d[0] < 300)
    dself = sum(d[1] for d in g[tag]['deaths'] if d[0] < 300 and not (d[2].startswith('rammed') or d[2].startswith('ram_enemy') or d[2] == 'killed_other'))
    return fresh, dl - own, dself, sum(1 for d in g[tag]['deaths'] if d[0] < 300)

rows = []
for mp in sorted(set(g['map'] for g in GS)):
    S = [g for g in GS if g['map'] == mp and g['top']]
    if not S: continue
    u = [f(g, 'us') for g in S]; t = [f(g, 'them') for g in S]
    fu = mean(x[0] for x in u); ft = mean(x[0] for x in t)
    bu = mean(x[1] for x in u); bt = mean(x[1] for x in t)
    du = mean(x[3] for x in u); dt = mean(x[3] for x in t)
    rows.append((sum(g['win'] for g in S) / len(S), mp, len(S), fu, ft, bu, bt, 1 - bu / fu, 1 - bt / ft, du, dt,
                 mean(tlv(g, 'us', 300)[1] for g in S), mean(tlv(g, 'them', 300)[1] for g in S), S[0]['w'] * S[0]['h']))
print('%-18s %4s %3s %5s | fresh us/them (ratio) | burn us/them | retention us/them | deaths/g us/them | total@300 us/them' % ('map', 'win', 'n', 'area'))
for r in sorted(rows, reverse=True):
    print('%-18s %.2f %3d %5d | %5.0f/%-5.0f (%.2f) | %5.0f/%-5.0f | %.2f/%.2f | %5.0f/%-5.0f | %5.0f/%-5.0f' % (
        r[1], r[0], r[2], r[13], r[3], r[4], r[3] / max(1, r[4]), r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12]))
