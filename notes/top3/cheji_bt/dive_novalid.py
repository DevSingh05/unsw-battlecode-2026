"""What are cheji's NoValidAction deaths? action kind, len, free nbrs, phase, near own king / enemy."""
import json, os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
C = collections.Counter(); ex = []
for r in rows:
    if r['grp'] not in ('cheji',): continue
    g = sim2.simulate(r['path']); T = r['T']
    MV = {(a['round'], a['id']): a for a in g['moves']}
    for d in g['deaths']:
        if d['team'] != T or d['reason'] != 'NoValidAction': continue
        a = MV.get((d['round'], d['id']))
        act = a['act'] if a else None
        kind = 'none' if act is None else ('suicide' if 'suicide' in act else ('move%d' % len(act['move']) if 'move' in act else ('split' if 'split' in act else str(list(act)))))
        free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        k = d.get('king'); nearking = k and k[1] >= 8 and k[2] <= 3
        C[(kind, d['len'], 'free%d' % min(free, 1), 'nearKing' if nearking else '-')] += 1
        if len(ex) < 12 and kind.startswith('move') and d['round'] > 200: ex.append((r['gid'], d['round'], d['id'], d['len'], act, d['nbrs'], k))
for k, v in C.most_common(30): print(v, k)
for e in ex: print(e)
