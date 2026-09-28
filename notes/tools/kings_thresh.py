"""First round the final-king lineage reaches length 6/10/20/30, and per-game growth per 50 rounds."""
import json, os, sys, collections, statistics as S
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kings_analyze as K
idx = {m['id']: m for m in json.load(open(os.path.join(K.RD, 'index.json')))}
M = {m['id']: m for m in json.load(open(os.path.join(K.RD, 'kings_metrics.json')))}
out = collections.defaultdict(list)
for mid in sorted(idx):
    R = M[mid]
    if R['end'] != 'roundLimit': continue
    g = K.load(mid); W = g['result']['winner']; lin = R['lineage']; owner = {}
    for n, (i, b) in enumerate(lin):
        e = lin[n + 1][1] if n + 1 < len(lin) else g['last_round'] + 1
        for r in range(b, e): owner[r] = i
    first = {}; top = 0; cnt = 0
    for r, s in g['rounds']:
        L = s[W]['ids'].get(owner.get(r, -1), 0)
        for t in (6, 10, 20, 30):
            if L >= t and t not in first: first[t] = r
        if r >= 300: cnt += 1; top += (L == s[W]['max'])
    out[R['map']].append((R['W'][:10], first.get(6), first.get(10), first.get(20), first.get(30), round(top / max(cnt, 1), 2)))
for mp, rows in out.items():
    print(mp)
    for r in rows: print('  ', r)
    for j, t in enumerate((6, 10, 20, 30)):
        xs = [r[j + 1] for r in rows if r[j + 1] is not None]
        print(f'   first>={t}: median {S.median(xs) if xs else None} range {min(xs) if xs else None}-{max(xs) if xs else None} n={len(xs)}')
