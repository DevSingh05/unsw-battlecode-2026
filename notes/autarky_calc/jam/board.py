"""ASCII board at END of round r (state the next round starts from).  python3 board.py GAME R x0 x1 y0 y1
Our heads: letters by id list; our body 'o'; enemy head 'E', enemy body 'e'; pearl '*'; pocket 'p'. | and _ kelp."""
import sys
from common import *
g, r = int(sys.argv[1]), int(sys.argv[2]); x0, x1, y0, y1 = map(int, sys.argv[3:7])
S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
R = dict(S['rounds'])[r]
occ = {}; legend = []
for j, b in sorted(R['bodies'].items()):
    T = S['team'][j]
    for k, t in enumerate(b):
        if k == 0:
            if T == us:
                c = chr(ord('A') + len(legend) % 26); legend.append('%s=%d(L%d)' % (c, j, len(b)))
            else:
                c = 'X'
        else: c = 'o' if T == us else 'e'
        if t not in occ or k == 0: occ[t] = c
print('game', g, 'end of round', r, 'us', us)
print('     ' + ''.join('%-2d' % (x % 100) for x in range(x0, x1 + 1)))
for y in range(y0, y1 + 1):
    top = '     '; row = '%3d  ' % y
    for x in range(x0, x1 + 1):
        t = (x, y)
        top += ('_ ' if m.edges.get(('H', x, y), (0, -1))[0] == 1 else '  ')
        wall = '|' if m.edges.get(('V', x, y), (0, -1))[0] == 1 else ' '
        c = occ.get(t) or ('*' if t in R['pearls'] else ('p' if t in PK else '.'))
        row = row[:-1] + wall + c + ' ' if False else row + (wall if wall == '|' else ' ') [0:0] + ('|' + c if wall == '|' else ' ' + c)
    print(top); print(row)
print(' '.join(l for l in legend if any(True for _ in [0])))
