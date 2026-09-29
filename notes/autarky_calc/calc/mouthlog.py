"""python3 mouthlog.py GID POCKET R0 R1 [RADIUS]  per-round log of heads near a pocket mouth + deaths there"""
from common import *
import sys
gid, p, r0, r1 = (int(v) for v in sys.argv[1:5]); RAD = int(sys.argv[5]) if len(sys.argv) > 5 else 5
gm = [x for x in GAMES if x['gid'] == gid][0]; g = sim(gid); R = dict(g['rounds']); c = gm['calc']
M = MOUTH[p]
for r in range(r0, r1 + 1):
    S = R.get(r)
    if not S: continue
    pe = ''.join('*' if t in S['pearls'] else '.' for t in sorted([t for t in pockets() if pocket_of(t) == p], key=lambda t: -pockets()[t]))
    ins = ['%s%d' % ('C' if S['heads'][j][2] == c else 'u', j) for j, bd in S['bodies'].items() if any(pocket_of(s) == p for s in bd)]
    near = sorted((mdist(h, M), j, h, L, T) for j, (h, L, T) in S['heads'].items() if mdist(h, M) <= RAD and pocket_of(h) is None)
    ds = ['%s%d(L%d %s%s)' % ('C' if d['team'] == c else 'u', d['id'], d['len'], d['reason'][:9], (' by %s%d' % ('C' if d.get('killer_team') == c else 'u', d['killer'])) if d.get('killer') is not None else '') for d in g['deaths'] if d['round'] == r and mdist(d['head'], M) <= RAD + 1]
    print('r%3d pocket[%s] in=%-12s near: %s %s' % (r, pe, ','.join(ins), ' '.join('%s%d:L%d@%s d%d' % ('C' if T == c else 'u', j, L, h, dd) for dd, j, h, L, T in near), ('DEATHS ' + ' '.join(ds)) if ds else ''))
