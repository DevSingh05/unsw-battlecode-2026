#!/usr/bin/env python3
"""King ledger r R0-500: the team's longest dragon each round; its pearl eats, what it gives away by
splitting (normal split: k; reverse split: parent's 2), and king deaths.  python3 .../kingledger.py [R0]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
R0 = int(sys.argv[1]) if len(sys.argv) > 1 else 300
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def yard(t): x, y = t; return 22 <= x <= 37 and y >= 24
rows = []
for gid, D in sorted(G.items()):
    res = {}
    for side in ('us', 'them'):
        T = D[side]
        kings = {r: D['tl'][r][T][3] for r in D['tl']}
        eats = sum(1 for e in D['eats'] if e['team'] == T and e['round'] >= R0 and e['id'] == kings.get(e['round'] - 1))
        rs = [s for s in D['splits'] if s['team'] == T and s['round'] >= R0 and s['parent'] == kings.get(s['round'] - 1)]
        rev = [s for s in rs if s['k'] == s['L'] - 2]
        give = sum(2 if s['k'] == s['L'] - 2 else s['k'] for s in rs)
        kd = [d for d in D['deaths'] if d['team'] == T and d['round'] >= R0 and d['id'] == kings.get(d['round'] - 1)]
        inyard = sum(1 for r in D['tl'] if r >= R0 and kings[r] is not None and kings[r] in D['tl'][r]['heads'] and yard(D['tl'][r]['heads'][kings[r]][0]))
        nr = sum(1 for r in D['tl'] if r >= R0)
        L0 = D['tl'][R0][T][1]; L1 = D['tl'][max(D['tl'])][T][1]
        res[side] = (L0, L1, eats, len(rev), give, sum(d['len'] for d in kd), inyard / max(1, nr))
    rows.append((lay(D), D['win'], gid, D['opp'], res))
print('lay W game  opp            | us: L%d->end eats revsplits give kingdeath yard%% | them: same' % R0)
for lay_, w, gid, opp, res in sorted(rows, key=lambda r: (r[0], r[1])):
    f = lambda r: '%2d->%2d eat %3d rev %2d give %3d kdie %3d yard %3.0f%%' % (r[0], r[1], r[2], r[3], r[4], r[5], 100 * r[6])
    print(lay_, 'W' if w else '-', gid, '%-14s' % opp[:14], '|', f(res['us']), '|', f(res['them']))
