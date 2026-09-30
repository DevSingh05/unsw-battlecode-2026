"""Who survives the consolidation: dragons alive at r=a, survival to r=b by length bucket and by age; growth of survivors."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
byL = collections.defaultdict(lambda: [0, 0]); byRank = collections.defaultdict(lambda: [0, 0]); byAge = collections.defaultdict(lambda: [0, 0])
growth = []; newborn = 0; ng = 0
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; S = dict(g['rounds'])
    A = S[a][T]['ids']; B = S[b][T]['ids']
    order = sorted(A, key=lambda j: -A[j])
    for rank, j in enumerate(order):
        s = j in B
        L = A[j]; byL[min(L, 12)][0] += 1; byL[min(L, 12)][1] += s
        byRank[min(rank, 10) if rank < 10 else (10 if rank < 20 else 20)][0] += 1; byRank[min(rank, 10) if rank < 10 else (10 if rank < 20 else 20)][1] += s
        age = a - g['born'].get(j, 0); ab = 0 if age < 20 else (20 if age < 50 else (50 if age < 100 else 100))
        byAge[ab][0] += 1; byAge[ab][1] += s
        if s: growth.append(B[j] - L)
    newborn += sum(1 for j in B if j not in A)
print(f'{grp} alive r{a} -> r{b} ({ng} games)')
print(' by len  :', ' '.join('L%d:%d/%d=%.2f' % (k, v[1], v[0], v[1] / v[0]) for k, v in sorted(byL.items())))
print(' by rank :', ' '.join('#%d:%.2f' % (k, v[1] / v[0]) for k, v in sorted(byRank.items())))
print(' by age  :', ' '.join('age>=%d:%d/%d=%.2f' % (k, v[1], v[0], v[1] / v[0]) for k, v in sorted(byAge.items())))
print(' survivors growth mean %.1f; new dragons (born in window) alive at end per game %.1f' % (st.mean(growth), newborn / ng))
