#!/usr/bin/env python3
"""ASCII board of a replay before dragon ID acts in ROUND (or at round start with id -1).
    python3 notes/tools/devdil/board.py GAME ROUND [ID] [x0 x1 y0 y1]
Shows kelp walls, hot tiles (h), pearls (*), our dragons (A-head 'U'/body 'u'), enemy (E/e), id labels listed below."""
import os, sys, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
GS = {g['game']: g for g in pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))}
REF = {'Devil': 'notes/maps/Devil__id13.map', 'Prisoners Dilemma': 'notes/maps/Prisoners_Dilemma__id17.map'}


def board(gid, rnd, did=None, box=None):
    g = GS[gid]
    ref = Map(open(os.path.join(ROOT, REF[g['map']])).read())
    if did is None:
        # first acting dragon of that round: use a large search
        S = None
        for i in range(0, 400):
            try:
                S = simulate(g['path'], stop=(rnd, i))
            except Exception:
                S = None
            if S and 'act' in S: break
    else:
        S = simulate(g['path'], stop=(rnd, did))
    if not S or 'act' not in S:
        print('no state'); return
    m = S['map']; us = g['us']
    occ = {}
    for j, b in S['body'].items():
        for k, t in enumerate(b): occ[t] = (j, k)
    x0, x1, y0, y1 = box if box else (0, m.w - 1, 0, m.h - 1)
    lines = []
    hdr = '    ' + ''.join('%-2d' % (x % 100) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1))
    lines.append(hdr)
    for y in range(y0, y1 + 1):
        top = '    '; row = '%3d ' % y
        for x in range(x0, x1 + 1):
            k, _ = m.edges.get(('H', x, y), (0, -1))
            top += ('--' if k == 1 else 'PP' if k == 2 else '  ')
            kv, _ = m.edges.get(('V', x, y), (0, -1))
            wch = '|' if kv == 1 else 'P' if kv == 2 else ' '
            t = (x, y)
            if t in occ:
                j, idx = occ[t]; mine = S['team'][j] == us
                c = ('U' if mine else 'E') if idx == 0 else ('u' if mine else 'e')
            elif t in S['pearls']: c = '*'
            elif ref.tiles.get(t, (0, 0)) == (1, 1): c = 'h'
            else: c = '.'
            row += wch + c
        lines.append(top); lines.append(row)
    print('\n'.join(lines))
    heads = []
    for j, b in sorted(S['body'].items()):
        hx, hy = b[0]
        if x0 <= hx <= x1 and y0 <= hy <= y1:
            heads.append('%s%d L%d @%s' % ('us' if S['team'][j] == us else 'EN', j, len(b), b[0]))
    print('  '.join(heads))
    print('acting:', S['e']['id'], S['act'])
    return S


if __name__ == '__main__':
    a = sys.argv[1:]
    box = tuple(map(int, a[3:7])) if len(a) >= 7 else None
    board(int(a[0]), int(a[1]), int(a[2]) if len(a) > 2 and a[2] != '-' else None, box)
