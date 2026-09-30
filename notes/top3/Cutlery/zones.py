"""Where the spawn eats happen r0-150 (and head-rounds), on a coarse grid, oriented so the team's start is on the left/top.
Usage: zones.py MAP [r0 r1]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
mp = sys.argv[1]; r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0; r1 = int(sys.argv[3]) if len(sys.argv) > 3 else 150
gm = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us'}
acc = collections.defaultdict(collections.Counter); hr = collections.defaultdict(collections.Counter); ng = collections.Counter()
bp = collections.defaultdict(list)
for x in collect.games():
    if x['grp'] in gm and x['map'] == mp: bp[x['path']].append(x)
GX = GY = None
for p, its in bp.items():
    g = sim2.simulate(p); m = g['map']
    GX, GY = 6, 4 if m.h < m.w else 6
    sym = m.sym
    for it in its:
        T = it['T']; k = gm[it['grp']]; ng[k] += 1
        st_ = [pts[0] for t, pts in m.dragons if 'AB'[t] == T]
        cx = st.mean(x for x, y in st_); cy = st.mean(y for x, y in st_)
        fx = cx > m.w / 2; fy = cy > m.h / 2
        def cell(t):
            x, y = t
            if fx: x = m.w - 1 - x
            if fy: y = m.h - 1 - y
            return (x * GX // m.w, y * GY // m.h)
        for e in g['eats']:
            if e['team'] == T and r0 <= e['round'] <= r1 and e['corpse'] is None: acc[k][cell(e['tile'])] += 1
        for r, s in g['rounds']:
            if r0 <= r <= r1:
                for j, (h, L, t) in s['heads'].items():
                    if t == T: hr[k][cell(h)] += 1
print(mp, 'sym', sym, 'games', dict(ng))
for k in acc:
    print(f'== {k}: spawn eats per game (head-rounds per game /10) per cell')
    for y in range(GY):
        print('  '.join(f'{acc[k][(x,y)]/ng[k]:5.1f} ({hr[k][(x,y)]/ng[k]/10:4.0f})' for x in range(GX)))
