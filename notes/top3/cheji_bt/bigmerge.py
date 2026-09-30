"""Late (r>=300) deaths of big (L>=8) non-king dragons and big splits (L>=10): context and corpse fate."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp = sys.argv[1]; show = int(sys.argv[2]) if len(sys.argv) > 2 else 10
A = collections.Counter(); ng = 0; ex = []; spl = []
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; m = g['map']; S = dict(g['rounds'])
    eatsby = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse']: eatsby[e['corpse'][0]].append(e)
    for d in g['deaths']:
        if d['team'] != T or d['round'] < 300 or d['len'] < 8: continue
        s = S[d['round'] - 1]; k = s[T]['king']
        if d['id'] == k: A['king_died'] += 1; continue
        kh, kL, _ = s['heads'][k]
        dist = m.dist(d['head'], kh)
        es = eatsby.get(d['id'], []); byk = sum(1 for e in es if e['id'] == k); own = sum(1 for e in es if e['team'] == T)
        en_near = min((m.dist(d['head'], h) for j, (h, L, t) in s['heads'].items() if t != T), default=99)
        A['n'] += 1; A['len'] += d['len']; A['pearls'] += (d['len'] + 1) // 2; A['byking'] += byk; A['own'] += own
        cat = d['reason']
        A['cause_' + cat] += 1
        if dist <= 3: A['near_king'] += 1
        ex.append((r['gid'], r['map'][:8], d['round'], d['len'], cat, 'kingL', kL, 'dist', dist, 'enemy', en_near, 'pearls', (d['len'] + 1) // 2, 'king ate', byk, 'own ate', own, d['nbrs']))
    for sp in g['splits']:
        if sp['team'] != T or sp['round'] < 300 or sp['L'] < 10: continue
        s = S[sp['round'] - 1]; k = s[T]['king']
        A['bigsplit'] += 1
        if sp['parent'] == k: A['bigsplit_king'] += 1
        # fate of child: dies within 5 rounds?
        cd = next((d for d in g['deaths'] if d['id'] == sp['child']), None)
        pd = next((d for d in g['deaths'] if d['id'] == sp['parent']), None)
        spl.append((r['gid'], sp['round'], 'L', sp['L'], 'k', sp['k'], 'exits', sp['exits'], 'isKing', sp['parent'] == k,
                    'child dies', (cd['round'] - sp['round'], cd['reason']) if cd else None, 'parent dies', (pd['round'] - sp['round'], pd['reason']) if pd else None))
print(grp, ng, 'games; per game', {k: round(v / ng, 2) for k, v in A.items()})
for e in ex[:show]: print('  ', e)
print('big splits:')
for e in spl[:show]: print('  ', e)
c = collections.Counter((x[8], x[11][1] if x[11] else 'alive', x[13][1] if x[13] else 'alive') for x in spl)
print(c.most_common(8))
c2 = collections.Counter((x[11][0] if x[11] else 99) // 3 * 3 for x in spl); print('child death delay buckets', sorted(c2.items()))
