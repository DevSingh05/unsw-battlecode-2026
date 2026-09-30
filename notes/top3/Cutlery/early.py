"""Early economy r0-150 per map (cut+cutvus vs us+usC): eats spawn/own-corpse/enemy-corpse, pocket spawn eats,
fast-tile (max gap<=5) eats, splits all/k2/tip/k>=3, deaths nonram/ram, eat sprints, units/total at r50/100/150,
share of spawn eats within 3 of an enemy head (contested), distinct spawn tiles eaten.
Usage: early.py [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
maps = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
gm = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us'}
acc = collections.defaultdict(lambda: collections.defaultdict(list))
bp = collections.defaultdict(list)
for x in collect.games():
    if x['grp'] in gm and (not maps or x['map'] in maps): bp[x['path']].append(x)
for p, its in bp.items():
    g = sim2.simulate(p); m = g['map']; PK = collect.pockets(m); R = dict(g['rounds'])
    for it in its:
        T = it['T']; k = (it['map'][:10], gm[it['grp']]); a = acc[k]
        E = [e for e in g['eats'] if e['team'] == T and e['round'] <= 150]
        a['spawn'].append(sum(1 for e in E if e['corpse'] is None)); a['own'].append(sum(1 for e in E if e['corpse'] and e['corpse'][1] == T))
        a['enemy'].append(sum(1 for e in E if e['corpse'] and e['corpse'][1] != T)); a['pocket'].append(sum(1 for e in E if e['corpse'] is None and e['tile'] in PK))
        a['fast'].append(sum(1 for e in E if e['corpse'] is None and e['gap'] and 0 < e['gap'][1] <= 5))
        a['contest'].append(sum(1 for e in E if e['corpse'] is None and e['en'] <= 3))
        a['tiles'].append(len({e['tile'] for e in E if e['corpse'] is None}))
        S = [s for s in g['splits'] if s['team'] == T and s['round'] <= 150]
        a['splits'].append(len(S)); a['tip'].append(sum(1 for s in S if s['L'] - s['k'] == 2 and s['k'] > 2)); a['k3'].append(sum(1 for s in S if s['k'] >= 3))
        D = [d for d in g['deaths'] if d['team'] == T and d['round'] <= 150]
        a['dnon'].append(sum(1 for d in D if d['reason'] != 'HitHeadToHead')); a['dram'].append(sum(1 for d in D if d['reason'] == 'HitHeadToHead'))
        a['esprint'].append(sum(1 for mv in g['moves'] if mv['team'] == T and mv['round'] <= 150 and mv['steps'] >= 2 and mv['ate'] and not mv['killed']))
        for r in (50, 100, 150):
            s = R.get(min(r, g['last_round']))
            a[f'n{r}'].append(s[T]['n']); a[f't{r}'].append(s[T]['total'])
M = lambda v: st.mean(v) if v else float('nan')
print('map        grp  n  | spawn own enemy | pocket fast contest tiles | splits tip k>=3 | dnon dram | eatsprint | r50 n/t  r100 n/t  r150 n/t')
for k in sorted(acc):
    a = acc[k]
    print(f"{k[0]:<11}{k[1]:<4}{len(a['spawn']):2d} | {M(a['spawn']):5.0f} {M(a['own']):3.0f} {M(a['enemy']):3.0f} | {M(a['pocket']):5.0f} {M(a['fast']):4.0f} {M(a['contest']):5.0f} {M(a['tiles']):4.0f} | {M(a['splits']):4.0f} {M(a['tip']):3.0f} {M(a['k3']):3.0f} | {M(a['dnon']):4.0f} {M(a['dram']):4.0f} | {M(a['esprint']):4.1f} | "
          + '  '.join(f"{M(a[f'n{r}']):3.0f}/{M(a[f't{r}']):4.0f}" for r in (50, 100, 150)))
