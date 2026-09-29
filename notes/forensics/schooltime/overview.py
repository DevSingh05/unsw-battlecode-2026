#!/usr/bin/env python3
"""Per-game overview table of Schooltime games (games.pkl).  python3 notes/forensics/schooltime/overview.py"""
import os, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
def at(D, r):
    ks = [k for k in D['tl'] if k <= r]
    return D['tl'][max(ks)]
print('game   opp                     elo  W side lay last | units r50/100/200/300/400/end us:them | total r100/200/300/400/end | longest r200/300/400/end')
for gid, D in sorted(G.items(), key=lambda kv: (-kv[1]['oppElo'])):
    us, th = D['us'], D['them']
    last = max(D['tl'])
    lay = 'A' if D['poolspawns'] > 20 else 'B'
    rs = [50, 100, 200, 300, 400, last]
    u = ' '.join('%d:%d' % (at(D, r)[us][0], at(D, r)[th][0]) for r in rs)
    t = ' '.join('%d:%d' % (at(D, r)[us][2], at(D, r)[th][2]) for r in rs[1:])
    l = ' '.join('%d:%d' % (at(D, r)[us][1], at(D, r)[th][1]) for r in rs[2:])
    print('%d %-22s %4d %s %s %s %3d | %s | %s | %s' % (gid, D['opp'][:22], D['oppElo'], 'W' if D['win'] else '-', us, lay, last, u, t, l))
