"""Eat-sprints: are the pearls corpse pearls? contested (enemy head within 3 of the pearl)? which phase?"""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp = sys.argv[1]; C = collections.Counter(); ng = 0
for r in rows:
    if r['grp'] != grp: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']
    sp = {(a['round'], a['id']) for a in g['moves'] if a['team'] == T and len(a['act'].get('move', [])) >= 2}
    for e in g['eats']:
        if e['team'] != T: continue
        k = 'sprint' if (e['round'], e['id']) in sp else 'walk'
        C[k] += 1
        C[k + ('_corpse' if e['corpse'] else '_nat')] += 1
        C[k + ('_contested' if e['en'] <= 3 else '_free')] += 1
        C[k + ('_allyclose' if e['al'] <= 2 else '_allyfar')] += 1
        C[k + '_ph%d' % (0 if e['round'] <= 60 else 1 if e['round'] <= 200 else 2 if e['round'] <= 350 else 3)] += 1
print(grp, ng, {k: round(v / ng, 1) for k, v in sorted(C.items())})
