"""Feeding efficiency in the consolidation window. For every own death in [lo,hi]: corpse pearls ceil(L/2),
how many eaten by own team (and how fast), by the eater's length; distance to nearest LONGER own head at death;
cause/free nbrs. Usage: feedeff.py grp lo hi"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp = sys.argv[1]; lo, hi = int(sys.argv[2]), int(sys.argv[3])
A = collections.Counter(); ng = 0; distb = collections.Counter(); delay = []; eaterL = collections.Counter(); lenb = collections.Counter()
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; m = g['map']; S = dict(g['rounds'])
    eatsby = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse']: eatsby[e['corpse'][0]].append(e)
    for d in g['deaths']:
        if d['team'] != T or not (lo <= d['round'] <= hi): continue
        s = S.get(d['round'] - 1)
        longer = [h for j, (h, L, t) in s['heads'].items() if t == T and j != d['id'] and L > d['len']]
        dist = min((m.dist(d['head'], h) for h in longer), default=99)
        pe = (d['len'] + 1) // 2
        A['deaths'] += 1; A['len'] += d['len']; A['pearls'] += pe
        lenb[min(d['len'], 8)] += 1
        distb[min(dist, 9)] += 1
        es = eatsby.get(d['id'], [])
        own = [e for e in es if e['team'] == T]; en = [e for e in es if e['team'] != T]
        A['own_eaten'] += len(own); A['en_eaten'] += len(en)
        for e in own:
            delay.append(e['round'] - d['round'])
            eaterL[min((e['len'] or 0) // 5 * 5, 40)] += 1
        if d['reason'] == 'HitHeadToHead': A['h2h'] += 1
        if dist <= 2: A['near2'] += 1; A['near2_own'] += len(own); A['near2_pe'] += pe
print(f'{grp} r{lo}-{hi}: {ng} games; per game:', {k: round(v / ng, 1) for k, v in A.items()})
print(' own-eaten share %.2f  enemy share %.2f  near(<=2 of a longer own head) share of deaths %.2f, own-eaten share there %.2f' % (
    A['own_eaten'] / max(1, A['pearls']), A['en_eaten'] / max(1, A['pearls']), A['near2'] / max(1, A['deaths']), A['near2_own'] / max(1, A['near2_pe'])))
print(' dist to nearest longer own head:', sorted(distb.items()))
print(' len of dead:', sorted(lenb.items()))
print(' delay to own eat: median', st.median(delay) if delay else None, ' <=3 rounds share %.2f' % (sum(1 for x in delay if x <= 3) / max(1, len(delay))))
print(' eater length buckets:', sorted(eaterL.items()))
