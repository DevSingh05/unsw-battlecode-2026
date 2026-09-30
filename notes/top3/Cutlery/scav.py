"""King own-corpse eats r300-500: dropper distance to the eating king at death, delay to eat, dropper len,
dropper free neighbours at death, dropper age, and whether dropper was moving toward the king in its last 5 moves.
Usage: scav.py GROUPS [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grps = sys.argv[1].split(','); maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
G = [x for x in collect.games() if x['grp'] in grps and (not maps or x['map'] in maps)]
M = lambda v: st.mean(v) if v else float('nan')
dist = collections.Counter(); delay = []; lens = collections.Counter(); free = collections.Counter(); ng = 0; appro = []; ages = []
perdrop = collections.Counter()
for it in G:
    g = sim2.simulate(it['path'])
    if g['result'].get('endReason') != 'roundLimit': continue
    ng += 1; T = it['T']; R = dict(g['rounds']); m = g['map']
    dd = {d['id']: d for d in g['deaths']}
    hist = collections.defaultdict(list)
    for a in g['moves']:
        if a['team'] == T and a['round'] >= 290: hist[a['id']].append((a['round'], a['head']))
    seen = set()
    for e in g['eats']:
        if e['team'] != T or e['round'] < 300 or e['corpse'] is None or e['corpse'][1] != T: continue
        s = R.get(e['round'] - 1)
        if not s or s[T]['king'] != e['id']: continue
        d = dd.get(e['corpse'][0])
        if not d: continue
        # king head at death round
        sd = R.get(d['round'] - 1) or R.get(d['round'])
        kh = sd['heads'].get(e['id'], (None,))[0]
        kd = m.dist(kh, d['head']) if kh else 99
        b = kd if kd <= 6 else ('7-12' if kd <= 12 else '13+')
        dist[b] += 1; delay.append(e['round'] - d['round'])
        if d['id'] in seen: continue
        seen.add(d['id']); perdrop[b] += 1
        lens[min(d['len'], 8)] += 1; free[sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))] += 1; ages.append(d['age'])
        # approaching: distance to king 5 rounds before vs at death
        h = [x for x in hist[d['id']] if d['round'] - 6 <= x[0] < d['round']]
        s5 = R.get(d['round'] - 6)
        if h and s5 and e['id'] in s5['heads']:
            appro.append(m.dist(h[0][1], s5['heads'][e['id']][0]) - kd)
print('games', ng)
print('king own-corpse eats by dropper dist at death (per game):', {k: round(v / ng, 2) for k, v in sorted(dist.items(), key=lambda kv: str(kv[0]))})
print('droppers by dist (per game):', {k: round(v / ng, 2) for k, v in sorted(perdrop.items(), key=lambda kv: str(kv[0]))})
print('delay death->king eat mean', round(M(delay), 1), 'median', st.median(delay) if delay else None, 'share <=3', round(M([x <= 3 for x in delay]), 2))
print('dropper len', sorted(lens.items()), 'free nbrs at death', sorted(free.items()), 'age mean', round(M(ages), 1), 'median', st.median(ages) if ages else None)
print('dropper approach toward king over last 6 rounds (+ = got closer):', round(M(appro), 2), 'share>0', round(M([x > 0 for x in appro]), 2))
