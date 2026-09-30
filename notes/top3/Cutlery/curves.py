"""Fine-grained curves r250-500 in round-limit games: units/total/longest/2nd and deaths by length bucket per window.
Usage: curves.py [maps comma] ; groups cut(all), usall(us+usC), usopp, cutopp"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
maps = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
G = collect.games()
grpmap = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us', 'usopp': 'opp', 'cutopp': 'opp'}
W = list(range(250, 501, 25))
acc = collections.defaultdict(lambda: collections.defaultdict(list))
byp = collections.defaultdict(list)
for x in G:
    if x['grp'] in grpmap and (not maps or x['map'] in maps): byp[x['path']].append(x)
for p, items in byp.items():
    g = sim2.simulate(p)
    if g['result'].get('endReason') != 'roundLimit': continue
    R = dict(g['rounds'])
    for it in items:
        T = collect.side(it, g); k = grpmap[it['grp']]
        a = acc[k]; a['games'].append(1)
        for r in W:
            s = R.get(min(r, g['last_round']))[T]
            a[f'n{r}'].append(s['n']); a[f't{r}'].append(s['total']); a[f'm{r}'].append(s['max']); a[f's{r}'].append(s['lens'][1] if len(s['lens']) > 1 else 0)
        for w0 in W[:-1]:
            ds = [d for d in g['deaths'] if d['team'] == T and w0 < d['round'] <= w0 + 25]
            a[f'd{w0}'].append(len(ds)); a[f'dl{w0}'].append(sum(d['len'] for d in ds))
            a[f'dbig{w0}'].append(sum(1 for d in ds if d['len'] >= 6))
            es = [e for e in g['eats'] if e['team'] == T and w0 < e['round'] <= w0 + 25]
            a[f'e{w0}'].append(len(es))
            # king eats in window
            ke = 0
            for e in es:
                s = R.get(e['round'] - 1)
                if s and s[T]['king'] == e['id']: ke += 1
            a[f'ke{w0}'].append(ke)
            spl = [s for s in g['splits'] if s['team'] == T and w0 < s['round'] <= w0 + 25]
            a[f'sp{w0}'].append(len(spl))
M = lambda v: st.mean(v) if v else float('nan')
for k, a in acc.items():
    print(f'== {k}  games={len(a["games"])}')
    print('round  ' + ' '.join(f'{r:>16}' for r in W))
    print('n/t/m/2 ' + ' '.join(f'{M(a[f"n{r}"]):3.0f}/{M(a[f"t{r}"]):4.0f}/{M(a[f"m{r}"]):4.1f}/{M(a[f"s{r}"]):3.0f}' for r in W))
    print('window  ' + ' '.join(f'{r:>16}' for r in W[:-1]))
    print('dth/L/big' + ' '.join(f'{M(a[f"d{r}"]):5.1f}/{M(a[f"dl{r}"]):4.0f}/{M(a[f"dbig{r}"]):3.1f}' for r in W[:-1]))
    print('eat/king/spl' + ' '.join(f'{M(a[f"e{r}"]):5.1f}/{M(a[f"ke{r}"]):4.1f}/{M(a[f"sp{r}"]):3.0f}' for r in W[:-1]))
