from common import *
g = sim(625768); m = g['map']; PK = collect.pockets(m)
print(m.w, m.h, m.sym, [(t, len(p), p[:3]) for t, p in m.dragons])
# gap char: gmax
def gc(t):
    mn, mx = m.tiles.get(t, (0, 0))
    if mx == 0: return ' '
    if mx <= 1: return '1'
    if mx <= 5: return '5'
    if mx <= 10: return 'a'
    if mx <= 50: return 'b'
    return 'c'
print('    ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(m.w)))
for y in range(m.h):
    top = '    '; row = '%3d ' % y
    for x in range(m.w):
        t = (x, y)
        e = m.edges.get(('H', x, y), (0, -1))[0]
        top += ('_ ' if e == 1 else ('= ' if e == 2 else '  '))
        e2 = m.edges.get(('V', x, y), (0, -1))[0]
        wall = '|' if e2 == 1 else (':' if e2 == 2 else ' ')
        c = gc(t)
        if t in PK: c = 'P' if c == ' ' else {'1': 'Q', '5': 'R', 'a': 'S'}.get(c, 'T')
        row += wall + c
    print(top); print(row)
from collections import Counter
print(Counter(m.tiles.values()).most_common(20))
print('pockets', sorted(PK.items()))
