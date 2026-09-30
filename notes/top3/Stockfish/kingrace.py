"""King race in round-limit games, per 50-round window r150-500.
Per team-game: top1/top2/#L>=10/#units at window end; eats by big (L>=10 at eat time) by source;
feeds = own deaths L<=5 within Chebyshev 2 of an own L>=10 head; feed yield = own-corpse pearls of feeders eaten by own big within 15 rounds;
late shed2 children (from L>=8 parents, r>=300): fate.
Usage: python3 kingrace.py SF,SFu,U,US  -> prints table, writes kingrace.pkl"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',') if len(sys.argv) > 1 else ['SF', 'SFu', 'U', 'US']
MAPS = sys.argv[2].split(',') if len(sys.argv) > 2 else None
W = [(150, 199), (200, 249), (250, 299), (300, 349), (350, 399), (400, 449), (450, 500)]
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and r['end'] == 'roundLimit' and (MAPS is None or r['map'] in MAPS): bypath[r['path']].append(r)
out = []
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    for r in rs:
        T = r['T']; D = {'grp': r['grp'], 'map': r['map'], 'gid': r['gid'], 'win': r['win']}
        lens_at = {}
        for rr, s in g['rounds']: lens_at[rr] = s[T]['ids']
        def wi(x):
            for i, (a, b) in enumerate(W):
                if a <= x <= b: return i
            return None
        for i, (a, b) in enumerate(W):
            s = RS.get(min(b, g['last_round']))
            ls = s[T]['lens']
            D[f't1_{i}'] = ls[0] if ls else 0; D[f't2_{i}'] = ls[1] if len(ls) > 1 else 0
            D[f'nb_{i}'] = sum(1 for x in ls if x >= 10); D[f'n_{i}'] = len(ls)
            D[f'tot_{i}'] = sum(ls)
        # eats by big
        for e in g['eats']:
            if e['team'] != T: continue
            i = wi(e['round'])
            if i is None or e['len'] is None: continue
            if e['len'] >= 10:
                src = 'own' if (e['corpse'] and e['corpse'][1] == T) else ('en' if e['corpse'] else 'sp')
                D[f'eb_{src}_{i}'] = D.get(f'eb_{src}_{i}', 0) + 1
        # feeds
        pearl_owner = {}
        for d in g['deaths']:
            if d['team'] != T: continue
            i = wi(d['round'])
            if i is None: continue
            k = d.get('king')
            if d['len'] <= 5 and k and k[1] >= 10 and k[3] <= 2:
                D[f'feed_{i}'] = D.get(f'feed_{i}', 0) + 1
                for sgm in d['body'][::2]: pearl_owner[sgm] = d['round']
            if d['len'] >= 10: D[f'bigdie_{i}'] = D.get(f'bigdie_{i}', 0) + 1
        for e in g['eats']:
            if e['team'] == T and e['tile'] in pearl_owner and e['corpse'] and e['corpse'][2] == pearl_owner[e['tile']] and e['round'] - pearl_owner[e['tile']] <= 15:
                i = wi(pearl_owner[e['tile']])
                if e['len'] is not None and e['len'] >= 10: D[f'fyield_{i}'] = D.get(f'fyield_{i}', 0) + 1
        # distance of small own heads to the king at 350 and 450
        for rr in (300, 350, 400, 450):
            s = RS.get(rr)
            if not s: continue
            kid = s[T]['king']; heads = s['heads']
            if kid is None or kid not in heads: continue
            kh = heads[kid][0]
            ds = [m.dist(kh, h) for j, (h, L, t) in heads.items() if t == T and j != kid and L <= 5]
            D[f'near6_{rr}'] = sum(1 for x in ds if x <= 6)
            D[f'medd_{rr}'] = st.median(ds) if ds else 0
        out.append(D)
pickle.dump(out, open(os.path.join(H, 'kingrace.pkl'), 'wb'))
ng = collections.Counter(d['grp'] for d in out)
print('round-limit team-games', dict(ng))
keys = ['t1', 't2', 'nb', 'n', 'tot', 'eb_own', 'eb_sp', 'eb_en', 'feed', 'fyield', 'bigdie']
print(f'{"":12s}', ' '.join(f'{w[0]:>4d}-{w[1]:<4d}' for w in W))
for gname in want:
    ds = [d for d in out if d['grp'] == gname]
    if not ds: continue
    print('==', gname, len(ds))
    for k in keys:
        vals = []
        for i in range(len(W)):
            bym = collections.defaultdict(list)
            for d in ds: bym[d['map']].append(d.get(f'{k}_{i}', 0))
            vals.append(st.mean(st.mean(l) for l in bym.values()))
        print(f'{k:12s}', ' '.join(f'{x:9.1f}' for x in vals))
    for rr in (300, 350, 400, 450):
        a = [d.get(f'near6_{rr}') for d in ds if d.get(f'near6_{rr}') is not None]
        b = [d.get(f'medd_{rr}') for d in ds if d.get(f'medd_{rr}') is not None]
        if a: print(f'  small heads within 6 of king @r{rr}: {st.mean(a):.1f}, median dist {st.mean(b):.1f}')
