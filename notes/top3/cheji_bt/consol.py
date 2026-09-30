"""Endgame consolidation: how the team turns a swarm into a king (games reaching r499).
Per team: timeline n/total/top3 lengths; king (= team's current longest) eats by source per window;
own deaths near the king (feeders): len, dist, cause; fate of own-corpse pearls r250+."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
GR = sys.argv[1].split(',') if len(sys.argv) > 1 else ['cheji', 'cpeer', 'cvsus', 'usvc', 'uspeer', 'uspeerop']
WIN = [(201, 300), (301, 350), (351, 400), (401, 450), (451, 500)]
def w_of(r):
    for i, (a, b) in enumerate(WIN):
        if a <= r <= b: return i
    return None
res = []
cache = {}
for r in rows:
    if r['grp'] not in GR or r['last'] < 499: continue
    if r['path'] not in cache: cache = {r['path']: sim2.simulate(r['path'])}
    g = cache[r['path']]; T = r['T']; m = g['map']
    R = dict(grp=r['grp'], gid=r['gid'], map=r['map'], win=r['win'])
    snaps = dict(g['rounds'])
    R['tl'] = {t: (snaps[t][T]['n'], snaps[t][T]['total'], snaps[t][T]['lens'][:3]) for t in range(250, 500, 25) if t in snaps}
    king = {t: s[T]['king'] for t, s in g['rounds']}
    kingL = {t: s[T]['max'] for t, s in g['rounds']}
    kinghead = {t: s['heads'].get(s[T]['king'], (None,))[0] for t, s in g['rounds']}
    D = collections.Counter()
    # eats by king
    for e in g['eats']:
        if e['team'] != T or e['round'] <= 200: continue
        w = w_of(e['round'])
        k = king.get(e['round'] - 1)
        if e['id'] == k:
            src = 'nat' if not e['corpse'] else ('own' if e['corpse'][1] == T else 'en')
            D[f'k{w}_{src}'] += 1
        else:
            D[f'o{w}_eat'] += 1
    # own deaths: near king?
    for d in g['deaths']:
        if d['team'] != T or d['round'] <= 200: continue
        w = w_of(d['round'])
        kh = kinghead.get(d['round'] - 1); k = king.get(d['round'] - 1)
        if d['id'] == k: D[f'kd{w}'] += 1; continue
        dist = m.dist(d['head'], kh) if kh else 99
        D[f'd{w}'] += 1; D[f'dL{w}'] += d['len']
        if dist <= 2: D[f'f{w}'] += 1; D[f'fL{w}'] += d['len']
    # corpse fate: own corpse pearls made r250+ (appears flagged corpse), who ate them
    made = collections.Counter(); fate = collections.Counter()
    for (t_, tile, c) in g['appears']:
        pass
    for e in g['eats']:
        if not e['corpse'] or e['corpse'][1] != T or e['corpse'][2] < 250: continue
        who = 'king' if e['id'] == king.get(e['round'] - 1) else ('ally' if e['team'] == T else 'enemy')
        fate[who] += 1
    dd = sum((d['len'] + 1) // 2 for d in g['deaths'] if d['team'] == T and d['round'] >= 250)
    R['corpse_made'] = dd; R['fate'] = dict(fate)
    R['D'] = D
    # round when n first <= 50% of max n in r200-350 and king >= 20
    nmax = max(snaps[t][T]['n'] for t in range(200, 351) if t in snaps)
    R['nmax'] = nmax
    R['half'] = next((t for t in range(250, 500) if t in snaps and snaps[t][T]['n'] <= nmax / 2), None)
    R['k20'] = next((t for t in range(200, 500) if t in snaps and snaps[t][T]['max'] >= 20), None)
    R['k30'] = next((t for t in range(200, 500) if t in snaps and snaps[t][T]['max'] >= 30), None)
    res.append(R)
pickle.dump(res, open(os.path.join(H, 'consol.pkl'), 'wb'))
def M(xs):
    xs = [x for x in xs if x is not None]
    return ('%6.1f' % st.mean(xs)) if xs else '     -'
for G in GR:
    rs = [x for x in res if x['grp'] == G]
    if not rs: continue
    print(f'\n### {G}: {len(rs)} round-limit games, maps', collections.Counter(x['map'] for x in rs))
    print(' win', M([x['win'] for x in rs]), ' nmax(200-350)', M([x['nmax'] for x in rs]), ' n<=half at', M([x['half'] for x in rs]), ' king>=20 at', M([x['k20'] for x in rs]), ' king>=30 at', M([x['k30'] for x in rs]))
    for t in range(250, 500, 25):
        print('  r%d n %s tot %s top1 %s top2 %s top3 %s' % (t, M([x['tl'][t][0] for x in rs if t in x['tl']]), M([x['tl'][t][1] for x in rs if t in x['tl']]),
              M([(x['tl'][t][2] + [0, 0, 0])[0] for x in rs if t in x['tl']]), M([(x['tl'][t][2] + [0, 0, 0])[1] for x in rs if t in x['tl']]), M([(x['tl'][t][2] + [0, 0, 0])[2] for x in rs if t in x['tl']])))
    for w, (a, b) in enumerate(WIN):
        f = lambda k: M([x['D'].get(k, 0) for x in rs])
        print(f'  r{a}-{b}: king eats nat {f(f"k{w}_nat")} own {f(f"k{w}_own")} en {f(f"k{w}_en")} | others eat {f(f"o{w}_eat")} | own deaths {f(f"d{w}")} (lenSum {f(f"dL{w}")}) near-king(<=2) {f(f"f{w}")} lenSum {f(f"fL{w}")} | king deaths {f(f"kd{w}")}')
    print('  own corpse pearls made r250+', M([x['corpse_made'] for x in rs]), ' eaten by king', M([x['fate'].get('king', 0) for x in rs]), 'ally', M([x['fate'].get('ally', 0) for x in rs]), 'enemy', M([x['fate'].get('enemy', 0) for x in rs]))
