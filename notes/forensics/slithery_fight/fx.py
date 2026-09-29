#!/usr/bin/env python3
"""Forensics helpers for replays/auto/games (Slithery Fight study).
  board  GAME ROUND ID [x0 x1 y0 y1] [--focus a,b]  ascii board just before ID acts in ROUND
         (K/k = focus dragon head/body, U/u = other allies, E/e = enemies, * pearl, h hot tile (gap 1..1),
          : spawnable tile, # = kelp wall drawn on edges: '|' vertical kelp, '--' horizontal kelp)
  run    BIN GAME ID R_FROM R_TO                     re-run our binary on the reconstructed 7x7 inputs
         of dragon ID for rounds R_FROM..R_TO (child = fresh process: R_FROM = birth round) and print the
         debug block of R_TO (cand scores, '->' decision).  Pearl countdowns are approximate (mid gap).
Run from the project root."""
import os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate, Map
import botview as BV
REFMAP = Map(open(os.path.join(ROOT, 'notes/maps/Slithery_Fight__id21.map')).read())

def path_of(gid):
    return os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)

def board(gid, rnd, did, box=None, focus=()):
    S = simulate(path_of(gid), stop=(rnd, did))
    m = S['map']; us = S['team'][did]
    occ = {}
    for j, b in S['body'].items():
        for k, t in enumerate(b): occ[t] = (j, k)
    x0, x1, y0, y1 = box if box else (0, m.w - 1, 0, m.h - 1)
    out = ['     ' + ''.join(('%-2d' % (x % 100)) if x % 2 == 0 else '  ' for x in range(x0, x1 + 1))]
    fset = set(focus) | {did}
    for y in range(y0, y1 + 1):
        top = '    '; row = '%3d ' % y
        for x in range(x0, x1 + 1):
            k, _ = m.edges.get(('H', x, y), (0, -1))
            top += ' ' + ('-' if k == 1 else 'P' if k == 2 else ' ')
            kv, _ = m.edges.get(('V', x, y), (0, -1))
            wch = '|' if kv == 1 else 'P' if kv == 2 else ' '
            t = (x, y)
            if t in occ:
                j, idx = occ[t]
                if j in fset: c = 'K' if idx == 0 else 'k'
                elif S['team'][j] == us: c = 'U' if idx == 0 else 'u'
                else: c = 'E' if idx == 0 else 'e'
            elif t in S['pearls']: c = '*'
            elif REFMAP.tiles.get(t, (0, 0)) == (1, 1): c = 'h'
            elif REFMAP.tiles.get(t, (0, 0))[1] > 0: c = ':'
            else: c = '.'
            row += wch + c
        out.append(top); out.append(row)
    heads = []
    for j, b in sorted(S['body'].items()):
        hx, hy = b[0]
        if (x0 <= hx <= x1 and y0 <= hy <= y1) or j in fset:
            heads.append('%s%d L%d @%s' % ('' if S['team'][j] == us else 'EN', j, len(b), b[0]))
    out.append('heads in box: ' + '  '.join(heads))
    out.append('acting: %d %s len %d head %s tail %s' % (did, S['act'], len(S['body'][did]), S['body'][did][0], S['body'][did][-1]))
    return '\n'.join(out), S

def run(binary, gid, did, r0, r1):
    m, turns = BV.capture(path_of(gid), did, r0, r1)
    outs, dbg = BV.run_bot(binary, did, turns)
    blocks = re.split(r'\n(?=R\d+ id=)', dbg)
    blk = [b for b in blocks if b.startswith('R%d ' % r1)]
    b = blk[-1] if blk else ''
    b = '\n'.join(l for l in b.splitlines() if not l.startswith('  seg '))
    return 'real action r%d: %s | bot outputs (last 2): %s\n%s' % (r1, turns[-1].get('act') if turns else None, outs[-2:], b)

if __name__ == '__main__':
    a = sys.argv[1:]
    focus = ()
    if '--focus' in a:
        i = a.index('--focus'); focus = tuple(int(v) for v in a[i + 1].split(',')); a = a[:i] + a[i + 2:]
    if a[0] == 'board':
        box = tuple(map(int, a[4:8])) if len(a) >= 8 else None
        print(board(int(a[1]), int(a[2]), int(a[3]), box, focus)[0])
    elif a[0] == 'run':
        print(run(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5])))
