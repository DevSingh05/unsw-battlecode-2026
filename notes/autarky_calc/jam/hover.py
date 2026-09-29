"""Every one of our L<=3 dragon-turns at a pocket mouth (BFS<=3 of the mouth, not inside) that does not eat, classified:
  busy-ally      an ally head is inside that pocket (queue; one diver at a time is the geometry)
  busy-enemy     an enemy head is inside that pocket
  behind-ally    pocket free but another of our heads is strictly closer to the pocket (pearlValue x0.25/x0.55 'someone closer')
  empty          pocket free and holds 0 pearls
  front:<why>    we are the closest head to a free pocket with pearls: reason from the reconstructed v29 decision
Same ground-truth split for calc's heads at the mouths (no decision reasons).  Prints dragon-rounds per game."""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
from parsedbg import parse
ALL = collections.Counter(); per = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]; th = 'B' if us == 'A' else 'A'
    MO = mouths(m, PK); MD = [bfsd(m, x, 3) for x in MO]
    pocket_of = {u: min(range(4), key=lambda i: m.dist(u, MO[i])) for u in PK}
    tips = [[u for u in PK if pocket_of[u] == i and PK[u] == 1][0] for i in range(4)]
    DT = [bfsd(m, tips[i], 14) for i in range(4)]
    ate = collections.Counter((e['id'], e['round']) for e in S['eats'])
    L = pickle.load(open('life_%d.pkl' % g, 'rb'))
    turn = {(i, x['round']): x for i, lst in L.items() for x in lst}
    R = dict(S['rounds'])
    for r in sorted(R):
        if r + 1 not in R: continue
        st = R[r]
        for j, (t, Lh, T) in st['heads'].items():
            if Lh > 3 or t in PK: continue
            ii = [i for i in range(4) if t in MD[i]]
            if not ii: continue
            i = ii[0]
            if ate[(j, r + 1)]: continue
            ins = [T2 for k, (t2, L2, T2) in st['heads'].items() if pocket_of.get(t2) == i]
            pp = sum(1 for p in st['pearls'] if pocket_of.get(p) == i)
            who = 'us' if T == us else 'calc'
            if T in ins: c = 'busy-ally'
            elif ins: c = 'busy-enemy'
            elif pp == 0: c = 'empty'
            else:
                mine = DT[i].get(t, 99)
                closer = [k for k, (t2, L2, T2) in st['heads'].items() if T2 == T and k != j and t2 not in PK and DT[i].get(t2, 99) < mine]
                if closer: c = 'behind-ally'
                elif who == 'calc': c = 'front'
                else:
                    x = turn.get((j, r + 1))
                    if not x: c = 'front:nodata'
                    else:
                        P = parse(x['dbg']); real = x['real'] or ''
                        nxt = m.step(t, real[5]) if real.startswith('MOVE') else None
                        if nxt is not None and DT[i].get(nxt, 99) < mine: c = 'front:advanced'
                        elif real.startswith('SPLIT'): c = 'front:split'
                        elif P['branch'] and P['branch'].startswith('ram'): c = 'front:ram'
                        else:
                            adv = [cc for d, cc in P['cands'].items() if DT[i].get(cc['t'], 99) < mine]
                            if not adv:
                                blk = [m.step(t, d) for d in 'NESW']
                                blk = [v for v in blk if v is not None and DT[i].get(v, 99) < mine]
                                own_body = any(v in st['bodies'].get(j, []) for v in blk)
                                c = 'front:blocked-own-neck' if own_body else 'front:blocked-other'
                            else:
                                a = min(adv, key=lambda cc: DT[i].get(cc['t'], 99))
                                if a.get('pocket') and a['pocket'] != 'YES' and a.get('areaP', 0) > 0: c = 'front:POCKET-' + a['pocket']
                                elif a.get('box', 0) <= -60: c = 'front:box-60'
                                elif a.get('threatP', 0) > 0: c = 'front:threat'
                                elif a.get('depthP', 0) > 0 or a.get('areaP', 0) > 0: c = 'front:area/depth'
                                else: c = 'front:pearl-value'
                            ex[c].append((g, r + 1, j, t))
            per[(g, who)][c] += 1
cats = sorted({c for v in per.values() for c in v})
print('%-26s' % 'dragon-rounds at a mouth' + ''.join('%14s' % ('%d %s' % (g, w)) for g in GAMES for w in ('us', 'calc')))
for c in cats:
    print('%-26s' % c + ''.join('%14d' % per[(g, w)][c] for g in GAMES for w in ('us', 'calc')))
print('%-26s' % 'TOTAL' + ''.join('%14d' % sum(per[(g, w)].values()) for g in GAMES for w in ('us', 'calc')))
pickle.dump(dict(per=dict(per), ex=dict(ex)), open('hover.pkl', 'wb'))
for c, v in ex.items():
    print(c, v[:6])
