"""Harvest quality: spawn eats by tile max_gap class (hot<=5, warm 6-40, cold>40), per phase; heads within 2 of a hot tile;
per-phase spawn eats per head-round. Uses maps/*.map for gaps (replays hide them).
Usage: python3 harvest.py SF,SFu,U,US"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',')
FILES = {'Portals': 'portals', 'Slithery Fight': 'slithery_fight', 'Autarky': 'autarky', 'Default': 'default', 'Devil': 'devil',
         'Prisoners Dilemma': 'dilemma', 'Queen Of Spades': 'queen_of_spades', 'Schooltime': 'schooltime', 'Trauma': 'trauma', 'Trophy': 'trophy'}
GAPS = {}
for mp, f in FILES.items():
    gm = {}
    for line in open(os.path.join(ROOT, 'maps', f + '.map')):
        x = line.split()
        if x and x[0] == 'TILE': gm[(int(x[1]), int(x[2]))] = (int(x[3]), int(x[4]))
    GAPS[mp] = gm
def cls(gp):
    if not gp or gp[1] == 0: return 'none'
    return 'hot' if gp[1] <= 5 else ('warm' if gp[1] <= 40 else 'cold')
PH = ((0, 60), (61, 150), (151, 300), (301, 500))
def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want: bypath[r['path']].append(r)
A = collections.defaultdict(lambda: collections.defaultdict(list))
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    gm = GAPS.get(g['map'].name) or GAPS.get(rs[0]['map'])
    hot = [t for t, gp in gm.items() if cls(gp) == 'hot']
    near_hot = set()
    for t in hot:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 2: near_hot.add(((t[0] + dx) % m.w, (t[1] + dy) % m.h))
    for r in rs:
        T = r['T']; C = collections.Counter()
        for e in g['eats']:
            if e['team'] != T or e['corpse']: continue
            C[(ph(e['round']), cls(gm.get(e['tile'])))] += 1
        hr = collections.Counter(); nh = collections.Counter()
        for rr, s in g['rounds']:
            if rr % 5: continue
            for j, (h, L, t) in s['heads'].items():
                if t == T: hr[ph(rr)] += 1; nh[ph(rr)] += (h in near_hot)
        for i in range(4):
            for c in ('hot', 'warm', 'cold'): A[(r['grp'], r['map'])][f'{c}{i}'].append(C[(i, c)])
            A[(r['grp'], r['map'])][f'nearhot{i}'].append(nh[i] / hr[i] if hr[i] else 0)
            A[(r['grp'], r['map'])][f'spawn_per_head{i}'].append(sum(C[(i, c)] for c in ('hot', 'warm', 'cold')) / (hr[i] * 5) if hr[i] else 0)
maps = sorted({k[1] for k in A})
for key in ['hot', 'warm', 'cold', 'nearhot', 'spawn_per_head']:
    for i in range(4):
        print(f'{key}{i:<3d}', ' | '.join(f"{mp[:8]}:" + ','.join(f"{st.mean(A[(gname, mp)][f'{key}{i}']):.2f}" if A.get((gname, mp)) else '-' for gname in want) for mp in maps))
    print()
