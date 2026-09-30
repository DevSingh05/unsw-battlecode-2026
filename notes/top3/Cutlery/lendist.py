"""Unit length distribution at r150/r250/r320 per map (cut+cutvus vs us+usC): share of units L2, L3, L4-5, L6-9, L10+, and mean.
Also rounds spent at >=60 units. Usage: lendist.py [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
maps = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
G = collect.games()
gm = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us', 'us31': 'u31'}
acc = collections.defaultdict(lambda: collections.defaultdict(collections.Counter)); cap = collections.defaultdict(list)
bp = collections.defaultdict(list)
for x in G:
    if x['grp'] in gm and (not maps or x['map'] in maps): bp[x['path']].append(x)
for p, its in bp.items():
    g = sim2.simulate(p); R = dict(g['rounds'])
    for it in its:
        k = (it['map'][:10], gm[it['grp']]); T = collect.side(it, g)
        for r in (150, 250, 320):
            s = R.get(r)
            if not s: continue
            for L in s[T]['lens']:
                b = 'L2' if L == 2 else 'L3' if L == 3 else 'L4-5' if L <= 5 else 'L6-9' if L <= 9 else 'L10+'
                acc[k][r][b] += 1; acc[k][r]['sum'] += L; acc[k][r]['n'] += 1
            acc[k][r]['games'] += 1
        cap[k].append(sum(1 for r, s in g['rounds'] if s[T]['n'] >= 60))
for k in sorted(acc):
    line = f'{k[0]:<11}{k[1]:<4} cap60 rounds {st.mean(cap[k]):5.0f} |'
    for r in (150, 250, 320):
        c = acc[k][r]; n = max(1, c['n'])
        line += f" r{r} n{c['n']/max(1,c['games']):4.0f} mean{c['sum']/n:4.1f} " + ' '.join(f"{b}:{c[b]/n:.2f}" for b in ('L2', 'L3', 'L4-5', 'L6-9', 'L10+')) + ' |'
    print(line)
