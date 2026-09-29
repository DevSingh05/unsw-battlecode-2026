#!/usr/bin/env python3
"""Endgame fragmentation counterfactual: at round R (default 470), our top dragons and where they are
(Y = yard, reachable only through portals 0/1; o = outside). A fed dragon of length L leaves ceil(L/2)
pearls (even segments), so 'fed2' = top1 + ceil(top2/2) and 'fed3' = fed2 + ceil(top3/2); compared with
the opponent's FINAL longest.  python3 notes/forensics/schooltime/fragment.py [R]"""
import os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
R = int(sys.argv[1]) if len(sys.argv) > 1 else 470
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
yard = lambda t: 22 <= t[0] <= 37 and t[1] >= 24
cnt = {}
for gid, D in sorted(G.items(), key=lambda kv: (lay(kv[1]), kv[1]['win'])):
    us, th = D['us'], D['them']
    if R not in D['tl']: continue
    hs = D['tl'][R]['heads']
    top = sorted(((L, j, h) for j, (h, L, T) in hs.items() if T == us), reverse=True)[:3] + [(0, -1, (0, 0))] * 3
    fin = D['tl'][max(D['tl'])]
    theirs = fin[th][1]; ours = fin[us][1]
    f2 = top[0][0] + (top[1][0] + 1) // 2; f3 = f2 + (top[2][0] + 1) // 2
    split = 'split' if top[1][0] and yard(top[0][2]) != yard(top[1][2]) else 'same'
    key = (lay(D), D['win'])
    c = cnt.setdefault(key, [0, 0, 0, 0])
    c[0] += 1; c[1] += (not D['win']) and f2 > theirs; c[2] += (not D['win']) and f3 > theirs; c[3] += split == 'split'
    print('%s %s %d %-14s r%d top %s | final us %d them %d | fed2 %d fed3 %d | top1/top2 %s' % (
        lay(D), 'W' if D['win'] else '-', gid, D['opp'][:14], R,
        ' '.join('%d%s' % (L, 'Y' if yard(h) else 'o') for L, j, h in top[:3] if L), ours, theirs, f2, f3, split))
for k, c in sorted(cnt.items()):
    print(k, 'games %d  losses flipped by fed2 %d  by fed3 %d  top1/top2 in different regions %d' % tuple(c))
