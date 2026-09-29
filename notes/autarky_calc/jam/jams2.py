"""Tighter jam episodes for OUR team (and the same metrics for calc as a baseline):
 DENSE: a head with >=3 other own heads within Chebyshev 2 (a 5x5 box holding >=4 of our heads), no eat by any of them, >=3 consecutive
        rounds (chained while >=2 members persist).
 OSC:   a dragon whose head visits <=4 distinct tiles over 8 consecutive rounds without eating (2x2 circling).
Ranked by dragon-rounds (sum over rounds of members).  -> jams2.pkl"""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
res = []; summ = collections.defaultdict(collections.Counter)
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
    MO = mouths(m, PK); MD = {}
    for x in MO: MD.update(bfsd(m, x, 3))
    R = dict(S['rounds']); eatR = collections.defaultdict(set)
    for e in S['eats']: eatR[e['round']].add(e['id'])
    for T in 'AB':
        who = 'us' if T == us else 'calc'
        # DENSE
        per = {}
        for r in sorted(R):
            H = {j: t for j, (t, L, TT) in R[r]['heads'].items() if TT == T}
            groups = []
            for j, t in H.items():
                grp = frozenset(k for k, t2 in H.items() if m.cheb(t, t2) <= 2)
                if len(grp) >= 4 and not any(k in eatR[r] for k in grp): groups.append(grp)
            # merge overlapping
            merged = []
            for gset in groups:
                for i, mg in enumerate(merged):
                    if mg & gset: merged[i] = mg | gset; break
                else: merged.append(gset)
            per[r] = merged
        used = set()
        for r in sorted(per):
            for c in per[r]:
                if (r, c) in used: continue
                chain = [(r, c)]; used.add((r, c)); cur = c; rr = r
                while True:
                    nx = [c2 for c2 in per.get(rr + 1, []) if len(c2 & cur) >= 2 and (rr + 1, c2) not in used]
                    if not nx: break
                    cur = nx[0]; rr += 1; chain.append((rr, cur)); used.add((rr, cur))
                dr = sum(len(x) for _, x in chain)
                if len(chain) >= 3:
                    mem = sorted(set().union(*[x for _, x in chain]))
                    at_mouth = sum(1 for rx, x in chain for k in x if R[rx]['heads'][k][0] in MD or R[rx]['heads'][k][0] in PK)
                    res.append(dict(kind='DENSE', who=who, game=g, r0=chain[0][0], r1=chain[-1][0], n=len(chain), dr=dr, ids=mem,
                                    maxh=max(len(x) for _, x in chain), where=R[chain[0][0]]['heads'][sorted(chain[0][1])[0]][0], mouth_share=at_mouth / dr))
                    summ[(g, who)]['DENSE'] += dr
        # OSC
        hist = collections.defaultdict(list)
        for r in sorted(R):
            for j, (t, L, TT) in R[r]['heads'].items():
                if TT == T: hist[j].append((r, t, j in eatR[r], L))
        for j, hs in hist.items():
            cur = None
            for idx in range(7, len(hs)):
                w = hs[idx - 7: idx + 1]
                if w[-1][0] - w[0][0] == 7 and len({t for _, t, _, _ in w}) <= 4 and not any(e for _, _, e, _ in w):
                    if cur and cur['r1'] == w[-1][0] - 1: cur['r1'] = w[-1][0]
                    else:
                        cur = dict(kind='OSC', who=who, game=g, ids=[j], r0=w[0][0], r1=w[-1][0], where=w[-1][1], L=w[-1][3]); res.append(cur)
        for c in res:
            if c['kind'] == 'OSC' and c['game'] == g and c['who'] == who and 'dr' not in c:
                c['n'] = c['r1'] - c['r0'] + 1; c['dr'] = c['n']; c['maxh'] = 1
                c['at_mouth'] = c['where'] in MD
                summ[(g, who)]['OSC'] += c['dr']
pickle.dump(res, open('jams2.pkl', 'wb'))
print('dragon-rounds in jams (us / calc):')
for g in GAMES:
    print(' ', g, ' '.join('%s %d/%d' % (k, summ[(g, 'us')][k], summ[(g, 'calc')][k]) for k in ('DENSE', 'OSC')))
for kind in ('DENSE', 'OSC'):
    xs = sorted([e for e in res if e['kind'] == kind and e['who'] == 'us'], key=lambda e: -e['dr'])
    print('top', kind, 'episodes (us):')
    for e in xs[:12]:
        print('  ', e['game'], 'r%d-%d' % (e['r0'], e['r1']), 'n=%d dr=%d maxh=%d' % (e['n'], e['dr'], e['maxh']), 'at', e['where'], 'L%s' % e.get('L', ''), 'ids', e['ids'][:12],
              'mouth %.0f%%' % (100 * e['mouth_share']) if 'mouth_share' in e else ('mouth' if e.get('at_mouth') else ''))
