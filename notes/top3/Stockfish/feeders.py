"""Feeder approach: for own deaths L<=5 within Manhattan 4 of the team's longest (L>=10) at r>=200 (round-limit games),
distance feeder-head -> king-head 5/10/20 rounds before death, feeder age, and king displacement over the previous 10 rounds.
Also the direction of the death relative to the king heading: 'ahead' if the dying head is closer to the king's next tiles.
Usage: python3 feeders.py SFu,U"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(','); MAP = sys.argv[2] if len(sys.argv) > 2 else None
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and r['end'] == 'roundLimit' and (MAP is None or r['map'] == MAP): bypath[r['path']].append(r)
A = collections.defaultdict(lambda: collections.defaultdict(list)); ng = collections.Counter()
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    for r in rs:
        T = r['T']; ng[r['grp']] += 1; B = A[r['grp']]
        for d in g['deaths']:
            if d['team'] != T or d['round'] < 200 or d['len'] > 5: continue
            s = RS.get(d['round'] - 1)
            if not s: continue
            k = s[T]['king']
            if k is None or k == d['id'] or s[T]['max'] < 10: continue
            kh = s['heads'][k][0]
            if m.dist(kh, d['head']) > 4: continue
            B['n'].append(1)
            B['age'].append(d['age'])
            B['len'].append(d['len'])
            B['free'].append(sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl')))
            for back in (5, 10, 20):
                s2 = RS.get(d['round'] - back)
                if s2 and d['id'] in s2['heads'] and k in s2['heads']:
                    B[f'dist{back}'].append(m.dist(s2['heads'][d['id']][0], s2['heads'][k][0]))
            s3 = RS.get(d['round'] - 10)
            if s3 and k in s3['heads']: B['kmove10'].append(m.dist(s3['heads'][k][0], kh))
            B['reason_' + d['reason']].append(1)
for gname in want:
    B = A[gname]; n = ng[gname]
    if not B['n']: continue
    print('==', gname, n, 'team-games; feeder deaths/g', round(len(B['n']) / n, 1))
    for k in ('age', 'len', 'free', 'dist5', 'dist10', 'dist20', 'kmove10'):
        l = B[k]
        if l: print(f'  {k:8s} median {st.median(l):5.1f} mean {st.mean(l):5.1f}  p>=10: {sum(1 for x in l if x >= 10)/len(l):.2f}')
    print('  reasons', {k[7:]: round(len(v) / len(B['n']), 2) for k, v in B.items() if k.startswith('reason_')})
