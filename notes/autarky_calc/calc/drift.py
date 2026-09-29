"""Do small heads move toward pocket mouths? For L<=3 heads, fraction of moves that reduce Manhattan distance to the nearest mouth, by distance band; and where heads are (distance distribution)."""
from common import *
import collections
for grp in ('calc_vsUS', 'US', 'calc_vsOth', 'oth'):
    A = collections.defaultdict(lambda: [0, 0, 0]); D = collections.Counter(); N = 0
    for gm in GAMES:
        if grp in ('US', 'calc_vsUS') and gm['us'] is None: continue
        if grp in ('oth', 'calc_vsOth') and gm['us'] is not None: continue
        g = sim(gm['gid']); c = gm['calc']
        for mv in g['moves']:
            if mv['round'] < 30 or mv['round'] > 300: continue
            if (mv['team'] == c) != grp.startswith('calc'): continue
            if mv['len_before'] > 3 or not mv.get('head_after'): continue
            h0, h1 = mv['head'], mv['head_after']
            if pocket_of(h0) is not None: continue
            d0 = min(mdist(h0, M) for M in MOUTH); d1 = min(mdist(h1, M) for M in MOUTH)
            b = '0-2' if d0 <= 2 else ('3-5' if d0 <= 5 else ('6-9' if d0 <= 9 else '10+'))
            A[b][0] += 1; A[b][1] += d1 < d0; A[b][2] += d1 > d0
            D[b] += 1; N += 1
    print(grp, 'head-turns', N, ' share by distance-to-nearest-mouth:', {k: '%.0f%%' % (100 * D[k] / N) for k in ('0-2', '3-5', '6-9', '10+')})
    print('     toward/away: ', {k: '%.0f/%.0f' % (100 * A[k][1] / A[k][0], 100 * A[k][2] / A[k][0]) for k in ('0-2', '3-5', '6-9', '10+') if A[k][0]})
