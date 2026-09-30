"""Churn at the unit cap: for a map, per group, r61-300: split parent L distribution, death age/len distribution,
share of deaths with 0 free nbrs, units at time of split/death, pearls of those deaths re-eaten by own within 10 rounds.
Usage: python3 churn.py MAP SFu,U"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
MAP = sys.argv[1]; want = sys.argv[2].split(',')
R0, R1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (61, 300)
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and r['map'] == MAP: bypath[r['path']].append(r)
A = collections.defaultdict(collections.Counter); ng = collections.Counter(); ages = collections.defaultdict(list)
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); RS = dict(g['rounds'])
    for r in rs:
        T = r['T']; ng[r['grp']] += 1; C = A[r['grp']]
        for s in g['splits']:
            if s['team'] == T and R0 <= s['round'] <= R1:
                C[('splitL', min(s['L'], 9))] += 1; C[('splitk', min(s['k'], 6))] += 1
                C[('split_units', '64' if s['units_before'] >= 63 else ('56+' if s['units_before'] >= 56 else '<56'))] += 1
        drops = {}
        for d in g['deaths']:
            if d['team'] == T and R0 <= d['round'] <= R1:
                free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
                C[('dlen', min(d['len'], 6))] += 1; C[('dfree', free)] += 1
                C[('dage', 'a<=5' if d['age'] <= 5 else ('a6-20' if d['age'] <= 20 else ('a21-60' if d['age'] <= 60 else 'a>60')))] += 1
                C[('dreason', d['reason'])] += 1
                for sg in d['body'][::2]: drops[sg] = (d['round'], d['id'])
                C['dropped'] += (d['len'] + 1) // 2
        for e in g['eats']:
            if e['team'] == T and e['corpse'] and e['tile'] in drops and drops[e['tile']][1] == e['corpse'][0] and e['round'] - drops[e['tile']][0] <= 10:
                C['re_eaten_own10'] += 1; drops.pop(e['tile'])
            elif e['team'] != T and e['corpse'] and e['tile'] in drops and drops[e['tile']][1] == e['corpse'][0]:
                C['eaten_by_enemy'] += 1; drops.pop(e['tile'])
for gname in want:
    n = ng[gname]; C = A[gname]
    print('==', gname, n, f'games, r{R0}-{R1}, per game')
    for key in ('splitL', 'splitk', 'split_units', 'dlen', 'dfree', 'dage', 'dreason'):
        print(f'  {key:12s}', {k[1]: round(v / n, 1) for k, v in sorted(C.items(), key=lambda kv: str(kv[0])) if isinstance(k, tuple) and k[0] == key})
    print(f"  dropped {C['dropped']/n:.1f}  re-eaten by own<=10r {C['re_eaten_own10']/n:.1f}  eaten by enemy {C['eaten_by_enemy']/n:.1f}")
