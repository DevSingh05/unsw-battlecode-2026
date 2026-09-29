"""Shared helpers for jam forensics (read-only over replays)."""
import os, sys, pickle
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/autarky')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import sim2, simj
from collect import pockets
GAMES = {625768: 'B', 617872: 'A', 612737: 'A', 608221: 'A'}
def path(g): return os.path.join(ROOT, 'replays/auto/games/%d.replay' % g)
_C = {}
def sim(g):
    if g not in _C:
        cp = os.path.join(H, 'cache_%d.pkl' % g)
        if os.path.exists(cp): _C[g] = pickle.load(open(cp, 'rb'))
        else:
            S = simj.simulate(path(g)); m = S['map']
            S['PK'] = pockets(m)
            _C[g] = S; pickle.dump(S, open(cp, 'wb'))
    return _C[g]
