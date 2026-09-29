"""Classify every one of our dragon-turns (reconstructed v29 decisions) into:
 EAT (ate this turn) | HUNT (chosen cand pearl term >= 1.0) | SUPPRESSED:<rule> (a cand with >= 0.5 more pearl value than the chosen one lost
 because of a penalty: areaP / POCKET veto / threat / depth / box) | IDLE (no cand worth >= 1.0: random walk) | SPLIT/RAM/other.
IDLE is split by zone: mouth (<=3 BFS of a pocket mouth), centre (x 19-34), side.  Per game, per phase."""
import sys, collections, pickle
from common import *
from jtl import mouths, bfsd
from parsedbg import parse
PH = [(0, 59), (60, 199), (200, 349), (350, 500)]
def phase(r): return next(i for i, (a, b) in enumerate(PH) if a <= r <= b)
TOT = collections.defaultdict(collections.Counter)
rows = []
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]
    MO = mouths(m, PK); MD = {}
    for x in MO: MD.update(bfsd(m, x, 3))
    ate = collections.Counter((e['id'], e['round']) for e in S['eats'])
    L = pickle.load(open('life_%d.pkl' % g, 'rb'))
    for i, lst in L.items():
        for x in lst:
            r = x['round']; P = parse(x['dbg']); cs = P['cands']
            zone = 'pocket' if x['head'] in PK else ('mouth' if x['head'] in MD else ('centre' if 19 <= x['head'][0] <= 34 else 'side'))
            real = x['real'] or ''
            chosen = cs.get(real[5]) if real.startswith('MOVE') and len(real) >= 6 else None
            if ate[(i, r)]: c = 'EAT'
            elif real.startswith('SPLIT'): c = 'SPLIT'
            elif P['branch'] and P['branch'].startswith('ram'): c = 'RAM'
            elif x['len'] > 5: c = 'BIG'
            elif not cs or chosen is None: c = 'other'
            else:
                best_pe = max(cs.values(), key=lambda v: v['pearls'])
                if best_pe['pearls'] >= chosen['pearls'] + 0.5 and best_pe is not chosen:
                    b = best_pe
                    if b.get('pocket') and b['pocket'] != 'YES' and b.get('areaP', 0) > 0: c = 'SUPP:POCKET ' + b['pocket']
                    elif b.get('areaP', 0) > 0 and b.get('depthP', 0) > 0: c = 'SUPP:area+depth'
                    elif b.get('areaP', 0) > 0: c = 'SUPP:area'
                    elif b.get('depthP', 0) > 0: c = 'SUPP:depth'
                    elif b.get('threatP', 0) > 0: c = 'SUPP:threat'
                    elif b.get('box', 0) < 0: c = 'SUPP:box'
                    else: c = 'SUPP:other'
                elif chosen['pearls'] >= 1.0: c = 'HUNT'
                else: c = 'IDLE-' + zone
            TOT[(g, phase(r))][c] += 1
            rows.append(dict(game=g, id=i, r=r, L=x['len'], head=x['head'], cls=c, zone=zone))
pickle.dump(rows, open('turnclass.pkl', 'wb'))
keys = sorted({k for v in TOT.values() for k in v})
for g in GAMES:
    print('game', g)
    print('   %-22s' % 'class' + ''.join('%9s' % ('r%d-%d' % PH[p]) for p in range(4)) + '    total')
    for k in keys:
        v = [TOT[(g, p)][k] for p in range(4)]
        print('   %-22s' % k + ''.join('%9d' % a for a in v) + '%9d' % sum(v))
    print('   %-22s' % 'ALL' + ''.join('%9d' % sum(TOT[(g, p)].values()) for p in range(4)))
