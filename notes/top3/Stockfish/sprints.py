"""Sprint + late-ram characterisation.
Sprints (>=2 steps): by own length band, steps, outcome (kill/die/ate), distance change to nearest enemy head.
Late rams (r>=380): rammer length, victim length, victim rank in its team (1=longest), rammer distance to own king.
Usage: python3 sprints.py SF,SFu,U,US"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',')
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want: bypath[r['path']].append(r)
A = collections.defaultdict(collections.Counter); ng = collections.Counter(); L = collections.defaultdict(list)
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    for r in rs:
        T = r['T']; E = 'B' if T == 'A' else 'A'; ng[r['grp']] += 1; C = A[r['grp']]
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'): continue
            mv = a['act'].get('move', [])
            if len(mv) < 2: continue
            band = 'L<=4' if a['len_before'] <= 4 else ('L5-9' if a['len_before'] <= 9 else 'L10+')
            out = 'kill' if a['killed'] else ('die' if a['died'] else ('ate' if a['ate'] else 'plain'))
            C[(band, out)] += 1; C[(band, 'steps', min(len(mv), 5))] += 1
            if out == 'plain':
                ne = a['near_enemy_head']; ea = a['enemy_after']
                if ne and ea is not None:
                    C[(band, 'plain', 'away' if ea > ne[0] else ('toward' if ea < ne[0] else 'same'))] += 1
                    L[(r['grp'], band, 'plain_ne')].append(ne[0])
        for a in g['moves']:
            if a['team'] != T or a['round'] < 380: continue
            for kid, kt, kl in a['killed']:
                if kt == T: continue
                s = RS.get(a['round'] - 1)
                if not s: continue
                ranks = sorted(s[E]['ids'].values(), reverse=True)
                vr = ranks.index(kl) + 1 if kl in ranks else 99
                C[('lateram', 'victim_rank', min(vr, 4))] += 1
                k = s[T]['king']; kd = m.dist(s['heads'][k][0], a['head']) if k in s['heads'] and k != a['id'] else -1
                L[(r['grp'], 'lateram_kd')].append(kd)
                L[(r['grp'], 'lateram_own')].append(a['len_before']); L[(r['grp'], 'lateram_vic')].append(kl)
for gname in want:
    n = ng[gname]; C = A[gname]
    print('==', gname, n)
    for band in ('L<=4', 'L5-9', 'L10+'):
        print(f'  {band}', {k[1]: round(v / n, 2) for k, v in C.items() if k[0] == band and len(k) == 2},
              'steps', {k[2]: round(v / n, 2) for k, v in sorted(C.items(), key=str) if k[0] == band and k[1] == 'steps'},
              'plain', {k[2]: round(v / n, 2) for k, v in C.items() if k[0] == band and k[1] == 'plain' and len(k) == 3})
    print('  late rams/g', round(sum(v for k, v in C.items() if k[0] == 'lateram') / n, 2), 'victim rank', {k[2]: round(v / n, 2) for k, v in sorted(C.items(), key=str) if k[0] == 'lateram'})
    for k in ('lateram_own', 'lateram_vic', 'lateram_kd'):
        l = L[(gname, k)]
        if l: print(f'   {k} mean {st.mean(l):.1f} median {st.median(l)}')
