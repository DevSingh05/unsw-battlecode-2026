"""The r~330 consolidation wave: per-round unit counts and deaths for a team, in a list of games."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp = sys.argv[1] if len(sys.argv) > 1 else 'cheji'
lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (300, 380)
for r in rows:
    if r['grp'] != grp or r['last'] < 499: continue
    g = sim2.simulate(r['path']); T = r['T']; s = dict(g['rounds'])
    dth = collections.Counter(d['round'] for d in g['deaths'] if d['team'] == T)
    line = ' '.join('%d:%d%s' % (t, s[t][T]['n'], ('-' + str(dth[t])) if dth[t] else '') for t in range(lo, hi) if t in s)
    # biggest single-round death burst
    burst = max(range(250, 480), key=lambda t: dth[t])
    print(r['gid'], r['map'][:9], 'W' if r['win'] else 'L', 'burst r%d x%d' % (burst, dth[burst]))
    print('   ', line[:900])
