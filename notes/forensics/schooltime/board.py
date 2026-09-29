#!/usr/bin/env python3
"""ASCII board just before dragon ID acts in ROUND (Schooltime games in replays/auto/games).
    python3 notes/forensics/schooltime/board.py GAME ROUND ID [x0 x1 y0 y1] [--focus ID2,...]
Focus dragons (ID and --focus): head 'K', body 'k'. Other allies of ID 'U'/'u', enemies 'E'/'e'.
Kelp '|' / '--', portal edges 'P' / 'PP', pearls '*', spawn tiles of the layout ':' ([1,20] pool 'o')."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate, Map
import replay_decode as R
import botview as BV

def path_of(gid):
    for d in ('auto/games', 'v28', 'v19plus'):
        p = os.path.join(ROOT, 'replays', d, '%d.replay' % gid)
        if os.path.exists(p): return p

def render(S, did, box=None, focus=(), tiles=None, mark=None):
    m = S['map']; us = S['team'][did]; tiles = tiles or m.tiles; mark = mark or {}
    occ = {}
    for j, b in S['body'].items():
        for k, t in enumerate(b): occ[t] = (j, k)
    x0, x1, y0, y1 = box if box else (0, m.w - 1, 0, m.h - 1)
    lines = ['    ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1))]
    fset = set(focus) | {did}
    for y in range(y0, y1 + 1):
        top = '    '; row = '%3d ' % y
        for x in range(x0, x1 + 1):
            k, _ = m.edges.get(('H', x, y), (0, -1))
            top += ('--' if k == 1 else 'PP' if k == 2 else '  ')
            kv, _ = m.edges.get(('V', x, y), (0, -1))
            wch = '|' if kv == 1 else 'P' if kv == 2 else ' '
            t = (x, y)
            if t in mark: c = mark[t]
            elif t in occ:
                j, idx = occ[t]
                if j in fset: c = 'K' if idx == 0 else 'k'
                elif S['team'][j] == us: c = 'U' if idx == 0 else 'u'
                else: c = 'E' if idx == 0 else 'e'
            elif t in S['pearls']: c = '*'
            elif tiles.get(t, (0, 0)) == (1, 20): c = 'o'
            elif tiles.get(t, (0, 0))[1] > 0: c = ':'
            else: c = '.'
            row += wch + c
        lines.append(top); lines.append(row)
    out = ['\n'.join(lines)]
    heads = []
    for j, b in sorted(S['body'].items()):
        hx, hy = b[0]
        if (x0 <= hx <= x1 and y0 <= hy <= y1) or j in fset:
            heads.append('%s%d L%d @%s' % ('' if S['team'][j] == us else 'EN', j, len(b), b[0]))
    out.append('  '.join(heads))
    out.append('acting: %d %s' % (did, S['act']))
    return '\n'.join(out)

def board(gid, rnd, did, box=None, focus=()):
    p = path_of(gid)
    S = simulate(p, stop=(rnd, did))
    if not S or 'act' not in S: return 'no state'
    o = R.load(p); tiles = BV.gap_source(o, S['map'])
    return render(S, did, box, focus, tiles)

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    focus = ()
    if '--focus' in sys.argv:
        fv = sys.argv[sys.argv.index('--focus') + 1]
        focus = tuple(int(v) for v in fv.split(',')); a = [x for x in a if x != fv]
    box = tuple(map(int, a[3:7])) if len(a) >= 7 else None
    print(board(int(a[0]), int(a[1]), int(a[2]), box, focus))
