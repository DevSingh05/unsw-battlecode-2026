"""Where do waiting heads sit while an own diver is inside? Relative (dx, dy_outward) to the mouth; dy>0 = away from pocket."""
from common import *
import collections
for grpname, sel in (('calc', lambda gm, T: T == gm['calc']), ('US', lambda gm, T: gm['us'] is not None and T != gm['calc'])):
    H_ = collections.Counter(); nq = collections.Counter(); N = 0
    for gm in GAMES:
        g = sim(gm['gid'])
        for r, S in g['rounds']:
            for p in range(4):
                ins = [j for j, bd in S['bodies'].items() if pocket_of(bd[0]) == p]
                if not ins: continue
                T = S['heads'][ins[0]][2]
                if not sel(gm, T): continue
                N += 1
                mx, my = MOUTH[p]; out = 1 if my < 9 else -1
                k = 0
                for j, (h, L, t) in S['heads'].items():
                    if t != T or pocket_of(h) is not None: continue
                    dx = h[0] - mx; dy = (h[1] - my) * out
                    if abs(dx) + abs(dy) <= 3 or (dy < 0 and abs(dx) <= 3):
                        H_[(dx, dy)] += 1; k += 1
                nq[min(k, 5)] += 1
    print(grpname, 'pocket-rounds with own diver inside:', N, ' #own heads within 3 of mouth:', {a: '%.0f%%' % (100 * b / N) for a, b in sorted(nq.items())})
    print('   heat (rows dy=-3..3 outward; dy<0 = alongside the pocket corridor, cols dx=-3..3), per 100 pocket-rounds')
    for dy in range(-3, 4):
        print('   ' + ' '.join('%5.1f' % (100 * H_[(dx, dy)] / N) for dx in range(-3, 4)))
