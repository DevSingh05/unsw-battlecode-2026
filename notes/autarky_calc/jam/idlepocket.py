"""Idle-pocket jams: rounds where a pocket holds >=2 pearls, >=K of our heads are within BFS<=D of its mouth,
and none of our heads is inside the pocket. Runs of such rounds per pocket, ranked by dragon-rounds."""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
K = int(sys.argv[1]) if len(sys.argv) > 1 else 2; DD = int(sys.argv[2]) if len(sys.argv) > 2 else 3
allruns = []
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
    MO = mouths(m, PK); MD = [bfsd(m, x, DD) for x in MO]
    pocket_of = {u: min(range(len(MO)), key=lambda i: m.dist(u, MO[i])) for u in PK}
    R = dict(S['rounds']); tot = 0
    for i in range(len(MO)):
        cur = []
        for r in sorted(R) + [10**9]:
            ok = False
            if r in R:
                pp = [p for p in R[r]['pearls'] if pocket_of.get(p) == i]
                ins = [j for j, (t, L, T) in R[r]['heads'].items() if T == us and pocket_of.get(t) == i]
                H_ = [j for j, (t, L, T) in R[r]['heads'].items() if T == us and t in MD[i] and t not in PK]
                E_ = [j for j, (t, L, T) in R[r]['heads'].items() if T != us and (t in MD[i] or pocket_of.get(t) == i)]
                Ein = [j for j, (t, L, T) in R[r]['heads'].items() if T != us and pocket_of.get(t) == i]
                ok = len(pp) >= 2 and not ins and len(H_) >= K
            if ok: cur.append((r, H_, len(pp), E_, Ein))
            else:
                if len(cur) >= 2:
                    allruns.append(dict(game=g, mouth=MO[i], home=(MO[i][0] == (35 if us == 'B' else 18)), r0=cur[0][0], r1=cur[-1][0], n=len(cur),
                                        dr=sum(len(x[1]) for x in cur), ids=sorted({j for x in cur for j in x[1]}), pearls=[x[2] for x in cur],
                                        enemy=[len(x[3]) for x in cur], enemy_in=[len(x[4]) for x in cur]))
                    tot += sum(len(x[1]) for x in cur)
                cur = []
    print(g, 'idle-pocket dragon-rounds (runs>=2)', tot)
allruns.sort(key=lambda e: -e['dr'])
pickle.dump(allruns, open('idleruns.pkl', 'wb'))
for e in allruns[:40]:
    print(e['game'], e['mouth'], 'home' if e['home'] else 'away', 'r%d-%d n=%d dr=%d' % (e['r0'], e['r1'], e['n'], e['dr']), 'ids', e['ids'], 'pearls', e['pearls'], 'enemyNear', e['enemy'], 'enemyIn', e['enemy_in'])
