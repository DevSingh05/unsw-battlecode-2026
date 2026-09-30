"""Where does mass go in r200-325 (round-limit games)? Per team: deaths by class, splits, eats, mass change; per map."""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
lo, hi = int(sys.argv[2]), int(sys.argv[3])
for grp in sys.argv[1].split(','):
    C = collections.Counter(); ng = 0
    for r in rows:
        if r['grp'] != grp or r['last'] < 499: continue
        ng += 1
        g = sim2.simulate(r['path']); T = r['T']; S = dict(g['rounds']); m = g['map']
        C['mass_change'] += S[hi][T]['total'] - S[lo][T]['total']
        C['top1_change'] += S[hi][T]['max'] - S[lo][T]['max']
        for d in g['deaths']:
            if d['team'] != T or not (lo < d['round'] <= hi): continue
            s = S[d['round'] - 1]
            if d['reason'] == 'HitHeadToHead':
                ot = d.get('killer_team') or d.get('victim_team')
                k = 'h2h_ally' if ot == T else 'h2h_enemy'
            elif d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] != T: k = 'into_enemy_body'
            else:
                free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
                k = 'suicide_trapped' if free == 0 else 'suicide_free'
                kk = s[T]['king']; kh = s['heads'][kk][0]
                if m.dist(d['head'], kh) <= 3 and s[T]['max'] >= 8: k += '_nearking'
            C['d_' + k] += 1; C['dL_' + k] += d['len']
        for e in g['eats']:
            if e['team'] == T and lo < e['round'] <= hi:
                C['eat_' + ('nat' if not e['corpse'] else 'own' if e['corpse'][1] == T else 'enemy')] += 1
        for s_ in g['splits']:
            if s_['team'] == T and lo < s_['round'] <= hi: C['splits'] += 1
    print(grp, f'r{lo}-{hi}', ng, 'games; per game', {k: round(v / ng, 1) for k, v in sorted(C.items())})
