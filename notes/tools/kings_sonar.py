"""Test whether sonar values encode the king head (x,y) / length in simple bit fields; U-turn context of kings."""
import json, os, pickle, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kings_analyze as K
RD = K.RD
idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
M = {m['id']: m for m in json.load(open(os.path.join(RD, 'kings_metrics.json')))}
res = collections.defaultdict(collections.Counter)
ut = collections.Counter(); utex = collections.Counter(); uten = []
for mid, meta in sorted(idx.items()):
    R = M[mid]
    if R['end'] != 'roundLimit': continue
    g = K.load(mid); m = g['map']; W = g['result']['winner']
    lin = R['lineage']; owner = {}
    for n, (i, b) in enumerate(lin):
        e = lin[n + 1][1] if n + 1 < len(lin) else g['last_round'] + 1
        for r in range(b, e): owner[r] = i
    heads = {mv['round']: (mv['head'], mv['len_before']) for mv in g['moves'] if mv['team'] == W and owner.get(mv['round']) == mv['id']}
    name = R['W']
    for s in g['sonars']:
        if s['team'] != W or s['round'] < 300 or s['round'] not in heads: continue
        v = s['value']; (kx, ky), kl = heads[s['round']]
        res[name]['n'] += 1
        # try every 6-bit aligned offset pair for x,y
        for off in range(0, 58, 1):
            x = (v >> off) & 63; y = (v >> (off + 6)) & 63
            if x == kx and y == ky: res[name][f'xy@{off}'] += 1
        if s['id'] == owner.get(s['round']): res[name]['from_king'] += 1
    for sp in g['splits']:
        if sp['parent'] in owner.values() and sp['team'] == W and sp['k'] > sp['L'] - sp['k'] and sp['L'] >= 8:
            ut[name] += 1; utex[sp['exits']] += 1; uten.append(sp['enemy_dist'])
for name, c in res.items():
    n = c['n']; best = sorted(((v, k) for k, v in c.items() if k.startswith('xy@')), reverse=True)[:3]
    print(f"{name[:14]:14s} pings r300+ {n} from_king {c['from_king']/max(1,n):.2f} king-xy matches {[(k, round(v/n,3)) for v,k in best]}")
print('king U-turn (reverse split, L>=8) exits at split', dict(utex), 'enemy dist med', sorted(uten)[len(uten)//2] if uten else None, 'per team', dict(ut))
