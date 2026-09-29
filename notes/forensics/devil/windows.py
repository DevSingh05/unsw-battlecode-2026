#!/usr/bin/env python3
"""Per-window timeline for one game, us / them.
    python3 notes/forensics/devil/windows.py GAME [W=10] [R1=120]
cols: units, total length, max len, eats (hot/other-spawn/corpse), splits, deaths (rammed-by-other H2H mover /
we-were-the-mover H2H / hitbody / self / other), mean len of dead."""
import sys, collections
from common import games, sim, REFMAP

gid = int(sys.argv[1]); W = int(sys.argv[2]) if len(sys.argv) > 2 else 10; R1 = int(sys.argv[3]) if len(sys.argv) > 3 else 120
G = {g['game']: g for g in games()}[gid]
S = sim(gid); us = G['side']; them = 'B' if us == 'A' else 'A'
snap = dict(S['rounds'])
print(gid, G['opp'], 'WIN' if G['win'] else 'LOSS', 'us=', us)
print('win   | units  | total  | max  | eat hot/sp/corpse us  them  | splits | us deaths H2Hmover/H2Hvictim/body/self/nva | them deaths')
for r0 in range(0, R1, W):
    r1 = r0 + W
    s = snap.get(r1) or snap[max(k for k in snap if k <= r1)]
    e = collections.Counter()
    for x in S['eats']:
        if r0 <= x['round'] < r1:
            k = 'c' if x['corpse'] else ('h' if REFMAP.tiles.get(x['tile'], (0, 0))[1] == 1 else 's')
            e[(x['team'], k)] += 1
    sp = collections.Counter(x['team'] for x in S['splits'] if r0 <= x['round'] < r1)
    d = collections.Counter()
    for x in S['deaths']:
        if not (r0 <= x['round'] < r1): continue
        rs = x['reason']
        k = {'HitHeadToHead': 'hm' if x['id'] == x['actor'] else 'hv', 'HitOtherBody': 'b', 'HitSelf': 's'}.get(rs, 'n')
        d[(x['team'], k)] += 1
    def dd(T): return '/'.join(str(d[(T, k)]) for k in ('hm', 'hv', 'b', 's', 'n'))
    print('%3d-%3d| %2d/%-2d | %3d/%-3d| %2d/%-2d| %2d/%2d/%2d  %2d/%2d/%2d | %2d/%-2d | %s | %s' % (
        r0, r1, s[us]['n'], s[them]['n'], s[us]['total'], s[them]['total'], s[us]['max'], s[them]['max'],
        e[(us, 'h')], e[(us, 's')], e[(us, 'c')], e[(them, 'h')], e[(them, 's')], e[(them, 'c')], sp[us], sp[them], dd(us), dd(them)))
