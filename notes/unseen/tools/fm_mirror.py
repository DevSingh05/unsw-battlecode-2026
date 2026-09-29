#!/usr/bin/env python3
"""Find the first round where a mirror match stops being mirror-symmetric.

    python3 notes/unseen/tools/fm_mirror.py REPLAY [sym]    (sym: x = left/right mirror, y = up/down, xy = 180 deg)

Prints the first few rounds where team A's occupied tiles (mirrored) differ from team B's, and the
dragons involved. Identical bots on a mirror map should stay symmetric except for turn order
(A's lower ids move first) and direction tie-breaks that are not mirror-equivariant.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map

path = sys.argv[1]
o = R.load(path); m = Map(o['map'])
sym = sys.argv[2] if len(sys.argv) > 2 else None
def mir(p):
    x, y = p
    if sym == 'x': return (m.w - 1 - x, y)
    if sym == 'y': return (x, m.h - 1 - y)
    return (m.w - 1 - x, m.h - 1 - y)
if sym is None:
    # guess from starting dragons
    a = [pts for t, pts in m.dragons if t == 0]; b = [pts for t, pts in m.dragons if t == 1]
    for s in ('x', 'y', 'xy'):
        sym = s
        if sorted(tuple(map(mir, p)) for p in a) == sorted(tuple(p) for p in b): break
print('sym', sym)
body = {}; team = {}
for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]
rnd = 0; shown = 0
def state():
    A = {}; B = {}
    for i, b in body.items():
        for k, s in enumerate(b):
            (A if team[i] == 'A' else B)[s if team[i] == 'B' else mir(s)] = (i, k, len(b))
    return A, B
for e in o['events']:
    t = e['t']
    if t == 'roundStart':
        if rnd > 0:
            A, B = state()
            if set(A) != set(B):
                diffA = set(A) - set(B); diffB = set(B) - set(A)
                print('round', rnd, 'A-only (mirrored)', sorted(diffA)[:8], 'ids', sorted({A[s][0] for s in diffA})[:6])
                print('         B-only          ', sorted(diffB)[:8], 'ids', sorted({B[s][0] for s in diffB})[:6])
                shown += 1
                if shown >= 3: break
        rnd = e['round']
    elif t == 'dragonUpdate':
        b = body[e['id']]; b.insert(0, e['head'])
        while b and b[-1] != e['tail']: b.pop()
    elif t == 'dragonSplit':
        body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']
    elif t == 'dragonDeath':
        body.pop(e['id'], None)
