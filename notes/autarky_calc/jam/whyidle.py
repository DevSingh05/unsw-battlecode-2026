"""For every round where one of our pockets is IDLE (>=1 pearl inside, none of our heads inside, no enemy head inside) and
we have an L<=3 head within BFS<=3 of its mouth: take our closest such head(s), look at the decision the (reconstructed,
99.5%-agreeing) v29 made on its turn in the NEXT round, and classify why it did not advance into the pocket.
Output idle_reasons.pkl + table."""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
from parsedbg import parse
out = []
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
    MO = mouths(m, PK)
    pocket_of = {u: min(range(4), key=lambda i: m.dist(u, MO[i])) for u in PK}
    tips = [max((u for u in PK if pocket_of[u] == i), key=lambda u: PK[u] * -1) for i in range(4)]  # rank 1 = tip
    tips = [[u for u in PK if pocket_of[u] == i and PK[u] == 1][0] for i in range(4)]
    DT = [bfsd(m, tips[i], 12) for i in range(4)]  # static distance to the pocket tip
    L = pickle.load(open('life_%d.pkl' % g, 'rb'))
    turn = {(i, x['round']): x for i, lst in L.items() for x in lst}
    R = dict(S['rounds'])
    for r in sorted(R):
        if r + 1 not in R: continue
        for i in range(4):
            pp = [p for p in R[r]['pearls'] if pocket_of.get(p) == i]
            ins = [j for j, (t, Lh, T) in R[r]['heads'].items() if pocket_of.get(t) == i]
            if not pp or ins: continue
            cand = [(DT[i].get(t, 99), j, t, Lh) for j, (t, Lh, T) in R[r]['heads'].items() if T == us and t not in PK and DT[i].get(t, 99) <= DT[i][MO[i]] + 3]
            if not cand: continue
            cand.sort()
            dmin = cand[0][0]
            en = [j for j, (t, Lh, T) in R[r]['heads'].items() if T != us and m.cheb(t, MO[i]) <= 3]
            for dd, j, t, Lh in cand:
                if dd > dmin: break
                x = turn.get((j, r + 1))
                rec = dict(game=g, r=r + 1, pocket=i, mouth=MO[i], id=j, head=t, L=Lh, dist_tip=dd, pearls=len(pp), n_ours=len(cand), enemy3=len(en))
                if x is None: rec['reason'] = 'died/nodata'; out.append(rec); continue
                P = parse(x['dbg']); rec['real'] = x['real']; rec['bot'] = x['bot']; rec['branch'] = P['branch']
                # which candidate advances toward the tip?
                adv = [(DT[i].get(c['t'], 99), d, c) for d, c in P['cands'].items()]
                adv.sort(key=lambda a: a[0])
                real_next = None
                if x['real'] and x['real'].startswith('MOVE'):
                    real_next = m.step(t, x['real'][5])
                advanced = real_next is not None and DT[i].get(real_next, 99) < dd
                rec['advanced'] = advanced
                if advanced: rec['reason'] = 'advanced'; out.append(rec); continue
                if x['real'] and x['real'].startswith('SPLIT'): rec['reason'] = 'split:' + (P['branch'] or ''); out.append(rec); continue
                if P['branch'] and P['branch'].startswith('ram'): rec['reason'] = 'ram'; out.append(rec); continue
                good = [a for a in adv if a[0] < dd]
                if not good:
                    # no candidate advances: next step blocked (occupied / body)
                    nb = [m.step(t, d) for d in 'NESW']
                    blk = [v for v in nb if v is not None and DT[i].get(v, 99) < dd]
                    who = []
                    for v in blk:
                        for jj, b in R[r + 1]['bodies'].items() if r + 1 in R else []:
                            pass
                    rec['reason'] = 'blocked(adv tile occupied)'; out.append(rec); continue
                _, d, c = good[0]
                chosen = P['cands'].get(x['real'][5]) if x['real'] and x['real'].startswith('MOVE') else None
                rec['adv'] = c; rec['chosen'] = chosen
                if c.get('pocket') and c['pocket'] != 'YES' and c.get('areaP', 0) > 0:
                    rec['reason'] = 'POCKET ' + c['pocket']
                elif c.get('box', 0) <= -60: rec['reason'] = 'box(ally trap -60)'
                elif c.get('threatP', 0) > 0: rec['reason'] = 'threat'
                elif c.get('depthP', 0) > 0: rec['reason'] = 'depth'
                elif c.get('areaP', 0) > 0: rec['reason'] = 'area(no pump check)'
                elif c.get('box', 0) < 0: rec['reason'] = 'box(ally -3)'
                elif chosen and chosen['pearls'] > c['pearls']: rec['reason'] = 'pearl value elsewhere'
                else: rec['reason'] = 'other'
                out.append(rec)
pickle.dump(out, open('idle_reasons.pkl', 'wb'))
C = collections.Counter(); G = collections.defaultdict(collections.Counter)
for o in out: C[o['reason']] += 1; G[o['game']][o['reason']] += 1
print('closest-head decisions while a pocket is idle (per head-turn):')
for k, v in C.most_common(): print('  %-30s %4d   %s' % (k, v, ' '.join('%d:%d' % (g, G[g][k]) for g in GAMES)))
