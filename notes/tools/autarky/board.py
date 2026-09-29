"""ASCII board of an Autarky game at the start of ROUND (before the lowest-id live dragon acts).
    python3 notes/tools/autarky/board.py GAME ROUND [x0 x1 y0 y1] [FOCUS_TEAM]
F/f = focus team head/body (us or the top team), E/e = other team, * pearl, # kelp-locked tile (never reachable),
P/p = pocket tile (empty), | and _ = kelp edges west/north of a tile."""
import os, sys, pickle
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
a = sys.argv[1:]; gid = int(a[0]); rnd = int(a[1])
path = [g['path'] for g in collect.games() if g['gid'] == gid][0]
R = [r for r in pickle.load(open(os.path.join(H, 'games.pkl'), 'rb')) if r['gid'] == gid]
foc = next((r for r in R if r['grp'] in ('us', 'top')), R[0])
F = a[6] if len(a) > 6 else foc['T']
full = sim2.simulate(path)
prev = dict(full['rounds']).get(rnd - 1)
first = min(prev['heads']) if prev else 0
S = sim2.simulate(path, stop=(rnd, first))
m = S['map']; PK = collect.pockets(m)
x0, x1, y0, y1 = (int(v) for v in a[2:6]) if len(a) >= 6 else (0, m.w - 1, 0, m.h - 1)
occ = {}
for i, b in S['body'].items():
    for k, t in enumerate(b):
        T = S['team'][i]; c = ('F' if T == F else 'E') if k == 0 else ('f' if T == F else 'e')
        occ[t] = c if k else c
print(gid, 'round', rnd, 'focus', F, foc['name'] if foc['T'] == F else foc['oppname'])
print('    ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1)))
for y in range(y0, y1 + 1):
    top = '    '
    row = '%3d ' % y
    for x in range(x0, x1 + 1):
        t = (x, y)
        top += ('_ ' if m.edges.get(('H', x, y), (0, -1))[0] == 1 else '  ')
        wall = '|' if m.edges.get(('V', x, y), (0, -1))[0] == 1 else ' '
        c = occ.get(t) or ('*' if t in S['pearls'] else ('p' if t in PK else '.'))
        row += wall + c
    print(top); print(row)
