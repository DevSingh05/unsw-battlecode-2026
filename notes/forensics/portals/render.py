#!/usr/bin/env python3
"""ASCII board just before dragon ID acts in ROUND (auto/games replays).
   python3 notes/forensics/portals/render.py GAME ROUND ID [x0 x1 y0 y1] [--focus ID2,...]
Acting dragon + focus: head 'K', body 'k'. Other allies 'U'/'u', enemies 'E'/'e'.
Edges: kelp '|' / '--', portal 'P' / 'PP' (with portal ids listed below). Pearls '*', hot [1,1] tiles 'h' (empty),
other spawn tiles ':' (empty), never-spawn '.'."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())


def board(gid, rnd, did, box=None, focus=(), out=None):
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid), stop=(rnd, did))
    if not S or 'act' not in S:
        return 'no state'
    m = S['map']
    # sim2 double-counts starter heads: dedupe consecutive duplicates
    for j, b in S['body'].items():
        S['body'][j] = [t for k, t in enumerate(b) if k == 0 or t != b[k - 1]]
    us = S['team'][did]
    occ = {}
    for j, b in S['body'].items():
        for k, t in enumerate(b): occ[t] = (j, k)
    x0, x1, y0, y1 = box if box else (0, m.w - 1, 0, m.h - 1)
    lines = ['    ' + ''.join('%-2d' % (x % 100) for x in range(x0, x1 + 1))]
    fset = set(focus) | {did}
    for y in range(y0, y1 + 1):
        top = '    '; row = '%3d ' % y
        for x in range(x0, x1 + 1):
            k, _ = m.edges.get(('H', x, y), (0, -1))
            top += ('--' if k == 1 else 'PP' if k == 2 else '  ')
            kv, _ = m.edges.get(('V', x, y), (0, -1))
            wch = '|' if kv == 1 else 'P' if kv == 2 else ' '
            t = (x, y)
            if t in occ:
                j, idx = occ[t]
                if j in fset: c = 'K' if idx == 0 else 'k'
                elif S['team'][j] == us: c = 'U' if idx == 0 else 'u'
                else: c = 'E' if idx == 0 else 'e'
            elif t in S['pearls']: c = '*'
            elif REF.tiles.get(t, (0, 0)) == (1, 1): c = 'h'
            elif REF.tiles.get(t, (0, 0))[1] > 0: c = ':'
            else: c = '.'
            row += wch + c
        lines.append(top); lines.append(row)
    heads = []
    for j, b in sorted(S['body'].items()):
        hx, hy = b[0]
        if (x0 <= hx <= x1 and y0 <= hy <= y1) or j in fset:
            heads.append('%s%d L%d @%s' % ('' if S['team'][j] == us else 'EN', j, len(b), b[0]))
    lines.append('heads: ' + '  '.join(heads))
    lines.append('acting: %d %s body: %s' % (did, S['act'], S['body'][did][:8] + (['...'] + S['body'][did][-2:] if len(S['body'][did]) > 8 else [])))
    s = '\n'.join(lines)
    return s


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    focus = ()
    if '--focus' in sys.argv:
        fv = sys.argv[sys.argv.index('--focus') + 1]
        focus = tuple(int(v) for v in fv.split(',')); a = [x for x in a if x != fv]
    box = tuple(map(int, a[3:7])) if len(a) >= 7 else None
    print(board(int(a[0]), int(a[1]), int(a[2]), box, focus))
