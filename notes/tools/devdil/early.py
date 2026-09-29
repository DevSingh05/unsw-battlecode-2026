#!/usr/bin/env python3
"""Opening (r0-R) per-game summary.  python3 notes/tools/devdil/early.py MAP [R=50]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1]; RR = int(sys.argv[2]) if len(sys.argv) > 2 else 50
print('game   ver res side | splits u/t | ramsInit u/t | nonram deaths u/t | hot eats u/t | corpse u/t | units@R | first5 our splits (r:L->k)')
for g in sorted([g for g in GS if g['map'].startswith(M)], key=lambda g: (g['win'], g['ver'], g['game'])):
    sp = collections.Counter(s['who'] for s in g['splitlist'] if s['round'] < RR)
    ri = collections.Counter(d['who'] for d in g['dl'] if d['round'] < RR and d['cat'] == 'ram_enemy')
    nr = collections.Counter(d['who'] for d in g['dl'] if d['round'] < RR and d['cat'] not in ('ram_enemy', 'rammed_by_enemy'))
    # eats in phases 0 and 1 approximated by phase index (0-50, 50-100)
    ph = 0 if RR <= 50 else 1
    he = {w: sum(v for (i, k), v in g['eats'].get(w, {}).items() if k == 'hot' and i <= ph) for w in ('us', 'them')}
    ce = {w: sum(v for (i, k), v in g['eats'].get(w, {}).items() if k == 'corpse' and i <= ph) for w in ('us', 'them')}
    ser = {x[0]: x for x in g['series']}; s = ser.get(min(RR, g['last']))
    first = ' '.join('%d:%d->%d' % (x['round'], x['L'], x['k']) for x in g['splitlist'] if x['who'] == 'us')[:0]
    fu = [x for x in g['splitlist'] if x['who'] == 'us'][:5]; ft = [x for x in g['splitlist'] if x['who'] == 'them'][:5]
    print('%d %-5s %s %s | %3d/%3d | %2d/%2d | %2d/%2d | %2d/%2d | %2d/%2d | %2d/%2d | us %s | them %s' % (g['game'], g['ver'], 'W' if g['win'] else 'L', 'left ' if g['we_left'] else 'right',
          sp['us'], sp['them'], ri['us'], ri['them'], nr['us'], nr['them'], he['us'], he['them'], ce['us'], ce['them'], s[1] if s else 0, s[4] if s else 0,
          ' '.join('%d:%d>%d' % (x['round'], x['L'], x['k']) for x in fu), ' '.join('%d:%d>%d' % (x['round'], x['L'], x['k']) for x in ft)))
