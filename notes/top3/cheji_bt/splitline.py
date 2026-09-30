"""Splits (non-reverse L<=5 'growth' splits vs all) and deaths per 25-round window, round-limit games."""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
for grp in sys.argv[1].split(','):
    S = collections.Counter(); D = collections.Counter(); E = collections.Counter(); ng = 0
    for r in rows:
        if r['grp'] != grp or r['last'] < 499: continue
        ng += 1
        g = sim2.simulate(r['path']); T = r['T']
        for s in g['splits']:
            if s['team'] == T: S[s['round'] // 25 * 25] += 1
        for d in g['deaths']:
            if d['team'] == T: D[d['round'] // 25 * 25] += 1
        for e in g['eats']:
            if e['team'] == T: E[e['round'] // 25 * 25] += 1
    print(grp, ng, 'games; per game per 25 rounds: splits / deaths / eats')
    print('   ' + ' '.join('r%d:%.0f/%.0f/%.0f' % (w, S[w] / ng, D[w] / ng, E[w] / ng) for w in range(200, 500, 25)))
