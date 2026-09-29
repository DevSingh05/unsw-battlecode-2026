#!/usr/bin/env python3
"""Collect compact per-game data for every Schooltime game in replays/auto/games/ledger.json.
    python3 notes/forensics/schooltime/collect.py [--jobs 6]   -> notes/forensics/schooltime/games.pkl
Read-only over replays. Uses notes/tools/midgame/sim2.simulate."""
import json, os, sys, pickle
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')

def yard(t): x, y = t; return 22 <= x <= 37 and y >= 24
def pool(t): x, y = t; return 27 <= x <= 32 and 34 <= y <= 38

def one(g):
    p = os.path.join(GD, '%d.replay' % g['game'])
    if not os.path.exists(p): return g['game'], None
    S = simulate(p)
    us = g['side']; them = 'B' if us == 'A' else 'A'
    tl = {}
    for rnd, snap in S['rounds']:
        tl[rnd] = {T: (snap[T]['n'], snap[T]['max'], snap[T]['total'], snap[T]['king'], snap[T]['lens'][:5]) for T in 'AB'}
        tl[rnd]['heads'] = {j: v for j, v in snap['heads'].items()}  # j -> (head, len, team)
    # layout: pool spawn appearances
    poolsp = sum(1 for r, t, c in S['appears'] if pool(t) and not c)
    D = dict(g); D.update(us=us, them=them, tl=tl, deaths=S['deaths'], eats=S['eats'], splits=S['splits'],
                          born=S['born'], parent_of=S['parent_of'], poolspawns=poolsp, result=S['result'],
                          moves=[{k: v for k, v in mv.items() if k in ('round', 'id', 'team', 'act', 'len_before', 'len_after', 'head', 'head_after', 'ate', 'died', 'steps', 'suicide')} for mv in S['moves']])
    return g['game'], D

if __name__ == '__main__':
    L = json.load(open(os.path.join(GD, 'ledger.json')))
    S = [g for g in L if g['map'] == 'Schooltime']
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 6
    with Pool(jobs) as P:
        res = dict(P.map(one, S))
    miss = [k for k, v in res.items() if v is None]
    print('games', len(res), 'missing', miss)
    pickle.dump({k: v for k, v in res.items() if v}, open(os.path.join(HERE, 'games.pkl'), 'wb'))
