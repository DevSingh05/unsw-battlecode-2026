"""Chosen deaths (not h2h, not collision into enemy) of small dragons (L<=5) in [lo,hi]: was a longer own head in view (cheb<=3)?
Who ate the corpse: that nearest longer ally / the team king / other own / enemy / nobody. Rank of the eater (1=team longest)."""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
C = collections.Counter(); rank = collections.Counter(); ng = 0; tgtL = collections.Counter()
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; m = g['map']; S = dict(g['rounds'])
    eatsby = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse']: eatsby[e['corpse'][0]].append(e)
    for d in g['deaths']:
        if d['team'] != T or not (lo <= d['round'] <= hi) or d['len'] > 5: continue
        if d['reason'] == 'HitHeadToHead' or (d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] != T): continue
        s = S[d['round'] - 1]
        own = sorted([(L, j, h) for j, (h, L, t) in s['heads'].items() if t == T], reverse=True)
        rk = {j: i + 1 for i, (L, j, h) in enumerate(own)}
        king = own[0][1]
        vis = [(m.dist(d['head'], h), -L, j, L) for L, j, h in own if j != d['id'] and L > d['len'] and m.cheb(d['head'], h) <= 3]
        tgt = min(vis)[2] if vis else None
        C['deaths'] += 1; C['vis' if vis else 'novis'] += 1
        if vis: tgtL[min(min(vis)[3] // 5 * 5, 30)] += 1
        for e in eatsby.get(d['id'], []):
            if e['team'] != T: k = 'enemy'
            elif e['id'] == tgt: k = 'target'
            elif e['id'] == king: k = 'king'
            else: k = 'other_own'
            C['pearl_' + k] += 1
            if e['team'] == T: rank[min(rk.get(e['id'], 99), 11)] += 1
        C['pearls'] += (d['len'] + 1) // 2
print(grp, f'r{lo}-{hi}', ng, 'games; per game', {k: round(v / ng, 1) for k, v in sorted(C.items())})
print('  eater rank (1=longest at death round; 11=>10 or newborn):', sorted(rank.items()))
print('  length of nearest bigger visible ally:', sorted(tgtL.items()))
