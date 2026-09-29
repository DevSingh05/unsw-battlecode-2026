#!/usr/bin/env python3
"""Opening race on Devil. Per game, us/them:
  hub@r  = heads inside the hub box (x 12..19, all y) at r15/r20/r25
  eat30  = pearls eaten r0-30 (hot tiles / other)
  len30  = total length at r30
  idle   = head-rounds in r10-40 spent outside the hub with no eat in the previous 8 rounds (wandering the side bands)
    python3 notes/forensics/devil/opening.py
"""
import collections
from common import games, sim, REFMAP

HOT = {t for t, g in REFMAP.tiles.items() if g[1] == 1}
inhub = lambda t: 12 <= t[0] <= 19
agg = collections.defaultdict(list)
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']; them = 'B' if us == 'A' else 'A'
    snap = dict(S['rounds'])
    lastEat = collections.defaultdict(lambda: 0)
    eats_by = collections.defaultdict(list)
    for e in S['eats']: eats_by[e['round']].append(e)
    idle = collections.Counter()
    for r in range(1, 41):
        for e in eats_by[r]: lastEat[e['id']] = r
        if r < 10: continue
        for j, (h, L, T) in snap[r]['heads'].items():
            born = S['born'].get(j, 0)
            if not inhub(h) and r - max(lastEat[j], born) >= 8: idle[T] += 1
    def hub(r, T): return sum(1 for h, L, t in snap[r]['heads'].values() if t == T and inhub(h))
    e30 = collections.Counter((e['team'], e['tile'] in HOT and not e['corpse']) for e in S['eats'] if e['round'] < 30)
    row = {}
    for T in (us, them):
        row[T] = (hub(15, T), hub(20, T), hub(25, T), e30[(T, True)], e30[(T, False)], snap[30][T]['total'], idle[T])
    res = 'W' if g['win'] else 'L'
    agg[res].append((row[us], row[them]))
    print('%d %-12s %s  hub@15/20/25 %d/%d/%d v %d/%d/%d | eat30 hot %2d+%2d v %2d+%2d | len30 %2d v %2d | idle %3d v %3d' % (
        g['game'], g['opp'][:12], res, *row[us][:3], *row[them][:3], row[us][3], row[us][4], row[them][3], row[them][4],
        row[us][5], row[them][5], row[us][6], row[them][6]))
for res, L in agg.items():
    n = len(L)
    mu = [sum(a[i] for a, b in L) / n for i in range(7)]; mt = [sum(b[i] for a, b in L) / n for i in range(7)]
    print(res, n, 'means us:', ' '.join('%.1f' % x for x in mu), '| them:', ' '.join('%.1f' % x for x in mt))
