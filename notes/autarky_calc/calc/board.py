"""python3 board.py GID ROUND [x0 x1 y0 y1]   end-of-round state. C/c calc head/body (with id), O/o opponent, * pearl"""
from common import *
import sys
def show(gid, rnd, x0=0, x1=53, y0=0, y1=17, out=print):
    gm = [x for x in GAMES if x['gid'] == gid][0]; g = sim(gid); S = dict(g['rounds'])[rnd]; m = realmap(); c = gm['calc']
    occ = {}
    for j, bd in S['bodies'].items():
        T = S['heads'][j][2]
        for k, t in enumerate(bd):
            occ[t] = ('C' if T == c else 'O') if k == 0 else ('c' if T == c else 'o')
    out('%d r%d (end of round)  calc=%s' % (gid, rnd, c))
    out('    ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        top = '    '; row = '%3d ' % y
        for x in range(x0, x1 + 1):
            t = (x, y)
            top += ('_ ' if m.edges.get(('H', x, y), (0, -1))[0] == 1 else '  ')
            wall = '|' if m.edges.get(('V', x, y), (0, -1))[0] == 1 else ' '
            ch = occ.get(t) or ('*' if t in S['pearls'] else ('p' if t in pockets() else '.'))
            row += wall + ch
        out(top); out(row)
    hs = sorted((j, h, L) for j, (h, L, T) in S['heads'].items() if x0 <= h[0] <= x1 and y0 <= h[1] <= y1)
    out('  heads: ' + ' '.join('%s%d@%s L%d' % ('C' if S['heads'][j][2] == c else 'O', j, h, L) for j, h, L in hs))
if __name__ == '__main__':
    a = [int(v) for v in sys.argv[1:]]
    show(*a)
