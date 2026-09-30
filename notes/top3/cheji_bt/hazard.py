"""Death hazard of small (L<=Lmax) own dragons per dragon-round in [lo,hi], conditioned on whether a LONGER own head
is visible (Chebyshev<=3) at round start, and on relative length. Tells whether feeding is 'die when a bigger ally is in view'."""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); Lmax = int(sys.argv[4]) if len(sys.argv) > 4 else 5
C = collections.Counter(); ng = 0
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; m = g['map']; S = dict(g['rounds'])
    died = {(d['round'], d['id']): d for d in g['deaths'] if d['team'] == T}
    for t in range(lo, hi + 1):
        s = S.get(t - 1)
        if not s: continue
        H_ = [(j, h, L) for j, (h, L, tt) in s['heads'].items() if tt == T]
        for j, h, L in H_:
            if L > Lmax: continue
            vis = [L2 for j2, h2, L2 in H_ if j2 != j and L2 > L and m.cheb(h, h2) <= 3]
            key = 'bigger_visible' if vis else 'none_visible'
            big = max(vis) if vis else 0
            if vis: key += '_L%s' % ('>=10' if big >= 10 else '5-9' if big >= 5 else '<5')
            C[key + '_n'] += 1
            if (t, j) in died: C[key + '_d'] += 1
print(grp, f'r{lo}-{hi} L<={Lmax}', ng, 'games')
for k in sorted({k[:-2] for k in C}):
    n = C[k + '_n']; d = C[k + '_d']
    print('   %-26s dragon-rounds %6d  deaths %5d  hazard %.3f' % (k, n, d, d / max(1, n)))
