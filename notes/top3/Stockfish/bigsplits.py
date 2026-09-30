"""List big splits (parent L>=8) for groups, classify: uturn (k>=L-2), half (3<=k<=L-3 with both >=4), shed (k<=2 from big)."""
import os, sys, pickle, collections, json
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',') if len(sys.argv) > 1 else ['SF', 'SFu', 'U']
C = collections.defaultdict(collections.Counter); ng = collections.Counter(); ex = collections.defaultdict(list)
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want: bypath[r['path']].append(r)
for p, rs in bypath.items():
    g = sim2.simulate(p)
    for r in rs:
        ng[r['grp']] += 1
        for s in g['splits']:
            if s['team'] != r['T'] or s['L'] < 8: continue
            L, k = s['L'], s['k']
            kind = 'uturn' if k >= L - 2 else ('shed2' if k <= 2 else ('half' if min(k, L - k) >= 4 else 'shed3'))
            w = 'r<300' if s['round'] < 300 else ('300-399' if s['round'] < 400 else '400+')
            C[r['grp']][(kind, w)] += 1
            C[r['grp']][(kind, 'exits' + str(s['exits']))] += 1
            if len(ex[(r['grp'], kind)]) < 12: ex[(r['grp'], kind)].append((r['gid'], r['map'][:8], s['round'], L, k, s['exits'], s['enemy_dist']))
for gname in want:
    print(gname, ng[gname], 'team-games')
    for k, v in sorted(C[gname].items()): print('   ', k, round(v / ng[gname], 2))
for k, v in ex.items(): print(k, v)
