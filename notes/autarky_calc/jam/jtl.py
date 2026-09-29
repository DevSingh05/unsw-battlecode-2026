"""Per-20-round timeline per game: units, total, eats (pocket/other), our/their heads within 3 of a mouth."""
import sys, collections
from common import *
def mouths(m, PK):
    return sorted({t for u in PK for d in 'NESW' for t in [m.step(u, d)] if t is not None and t not in PK})
def bfsd(m, src, cap=6):
    D = {src: 0}; q = [src]
    for u in q:
        if D[u] >= cap: continue
        for d in 'NESW':
            v = m.step(u, d)
            if v is not None and v not in D: D[v] = D[u] + 1; q.append(v)
    return D
if __name__ == '__main__':
    for g in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else GAMES):
        S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]; th = 'B' if us == 'A' else 'A'
        MO = mouths(m, PK); MD = [bfsd(m, x, 3) for x in MO]
        near = lambda t: any(t in D for D in MD) or t in PK
        rounds = dict(S['rounds'])
        E = collections.Counter()
        for e in S['eats']:
            E[(e['round'] // 20, e['team'], e['tile'] in PK)] += 1
        print('game', g, 'us', us, 'mouths', MO, S['result']['endReason'], S['result'][us], S['result'][th])
        print('win   units(us/th) total      pocketEats  otherEats  headsNearMouth(us/th)')
        for w0 in range(0, S['last_round'] + 1, 20):
            rs = [rounds[r] for r in range(w0, w0 + 20) if r in rounds]
            if not rs: continue
            last = rs[-1]
            hn = [sum(1 for j, (t, L, T) in R['heads'].items() if T == X and near(t)) for R in rs for X in (us, th)]
            print('r%3d  %2d/%2d  %3d/%3d   %3d/%3d     %3d/%3d     %.1f/%.1f' % (w0, last[us]['n'], last[th]['n'], last[us]['total'], last[th]['total'],
                  E[(w0 // 20, us, True)], E[(w0 // 20, th, True)], E[(w0 // 20, us, False)], E[(w0 // 20, th, False)],
                  sum(hn[0::2]) / len(rs), sum(hn[1::2]) / len(rs)))
