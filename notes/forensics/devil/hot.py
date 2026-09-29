#!/usr/bin/env python3
"""Who eats the 18 hot tiles (gap 1) on Devil, by tile group and window, us/them, per game.
Groups are named relative to OUR home side ("own" = the tubes on our start half).
    python3 notes/forensics/devil/hot.py [W|L]
"""
import sys, collections
from common import games, sim, REFMAP

HOT = sorted(t for t, g in REFMAP.tiles.items() if g[1] == 1)


def group(t, us):
    x, y = t
    own = (x < 16) == (us == 'A')
    if x in (14, 17): return ('own' if own else 'opp') + 'Ctube'
    if x in (15, 16): return 'Ctop' if y == 0 else 'Cbot'
    return ('own' if own else 'opp') + 'Tips'


WIN = [(0, 30), (30, 60), (60, 100), (100, 200), (200, 501)]
want = sys.argv[1] if len(sys.argv) > 1 else None
agg = collections.defaultdict(lambda: collections.Counter())
for g in sorted(games(), key=lambda g: g['at']):
    if want and ('W' if g['win'] else 'L') != want: continue
    S = sim(g['game']); us = g['side']
    c = collections.Counter()
    for e in S['eats']:
        if e['corpse'] or e['tile'] not in HOT: continue
        w = next(i for i, (a, b) in enumerate(WIN) if a <= e['round'] < b)
        c[(group(e['tile'], us), w, e['team'] == us)] += 1
    grp = ['ownTips', 'ownCtube', 'Ctop', 'Cbot', 'oppCtube', 'oppTips']
    line = []
    for gname in grp:
        line.append('%s ' % gname + ' '.join('%d/%d' % (c[(gname, w, True)], c[(gname, w, False)]) for w in range(4)))
    print(g['game'], g['opp'][:14].ljust(14), 'W' if g['win'] else 'L', g['side'], ' | '.join(line))
