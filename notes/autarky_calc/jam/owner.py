"""Per 20-round window: which team owns each pocket (rounds owned us/calc) and pocket eats us/calc."""
import sys, collections
from common import *
from jtl import mouths, bfsd
for g in (list(map(int, sys.argv[1:])) or GAMES):
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]; th = 'B' if us == 'A' else 'A'
    MO = mouths(m, PK); MD = [bfsd(m, x, 3) for x in MO]
    pocket_of = {u: min(range(4), key=lambda i: m.dist(u, MO[i])) for u in PK}
    R = dict(S['rounds'])
    pe = collections.Counter((e['round'] // 20, pocket_of[e['tile']], e['team']) for e in S['eats'] if e['tile'] in PK)
    own = collections.Counter()
    for r in sorted(R):
        for i in range(4):
            ins = collections.Counter(T for j, (t, L, T) in R[r]['heads'].items() if pocket_of.get(t) == i)
            nearc = collections.Counter(T for j, (t, L, T) in R[r]['heads'].items() if t in MD[i] and t not in PK)
            if ins: o = max(ins, key=lambda T: ins[T])
            elif nearc and nearc[us] != nearc[th]: o = us if nearc[us] > nearc[th] else th
            else: continue
            own[(r // 20, i, o)] += 1
    home = [i for i in range(4) if MO[i][0] == (35 if us == 'B' else 18)]
    print('game', g, 'us', us, 'home pockets', [MO[i] for i in home], 'cells: owned rounds us/calc  eats us/calc')
    print('win   ' + '  '.join('%-22s' % ('%s%s' % (MO[i], '*' if i in home else '')) for i in range(4)))
    for w in range(0, 13):
        print('r%3d  ' % (w * 20) + '  '.join('%2d/%2d  %2d/%2d          ' % (own[(w, i, us)], own[(w, i, th)], pe[(w, i, us)], pe[(w, i, th)]) for i in range(4)))
