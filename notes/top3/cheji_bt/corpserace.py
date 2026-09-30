"""Corpse race after head-to-head fights (games vs us, symmetric): who eats the pearls dropped by h2h deaths (either team) in r1-350,
how fast, and how many via sprint. Also same for cheji-vs-peer games."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
for G, O in (('cvsus', 'usvc'), ('cheji', 'cpeer')):
    C = collections.Counter(); ng = 0; delays = collections.defaultdict(list)
    for r in rows:
        if r['grp'] != G: continue
        ng += 1
        g = sim2.simulate(r['path']); T = r['T']
        dd = {d['id']: d for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d['round'] <= 350 and ((d.get('killer_team') or d.get('victim_team')) not in (None, d['team']))}
        sp = {(a['round'], a['id']) for a in g['moves'] if len(a['act'].get('move', [])) >= 2}
        for d in dd.values(): C['pearls'] += (len(d['body']) + 1) // 2
        for e in g['eats']:
            if not e['corpse'] or e['corpse'][0] not in dd: continue
            who = G if e['team'] == T else O
            C[who] += 1
            if (e['round'], e['id']) in sp: C[who + '_sprint'] += 1
            delays[who].append(e['round'] - dd[e['corpse'][0]]['round'])
    print(G, 'vs', O, ng, 'games; per game', {k: round(v / ng, 1) for k, v in C.items()}, ' median delay', {k: st.median(v) for k, v in delays.items()})
