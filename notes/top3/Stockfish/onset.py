"""Feeding onset per game: first round R such that the team's longest-at-the-time ate >=4 own-corpse pearls in [R, R+20).
Also king length at onset, units at onset, and king length at 350/450/500. Round-limit games only.
Usage: python3 onset.py SF,SFu,U,US"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',')
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and r['end'] == 'roundLimit': bypath[r['path']].append(r)
res = collections.defaultdict(list)
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); RS = dict(g['rounds'])
    for r in rs:
        T = r['T']
        ke = [e['round'] for e in g['eats'] if e['team'] == T and e['corpse'] and e['corpse'][1] == T and RS.get(e['round'] - 1) and e['id'] == RS[e['round'] - 1][T]['king'] and e['round'] >= 100]
        on = None
        for i, x in enumerate(ke):
            if sum(1 for y in ke[i:] if y < x + 20) >= 4: on = x; break
        s = RS.get(on) if on else None
        res[(r['grp'], r['map'])].append((on or 999, s[T]['max'] if s else 0, s[T]['n'] if s else 0, RS[350][T]['max'], RS[450][T]['max'], RS[min(499, g['last_round'])][T]['max'], r['win'], r['gid']))
for gname in want:
    print('==', gname)
    for (gg, mp), l in sorted(res.items()):
        if gg != gname: continue
        print(f'  {mp[:14]:14s} n={len(l):2d} onset med {st.median(x[0] for x in l):5.0f}  [' + ' '.join(str(x[0]) for x in sorted(l)) + f']  kingAtOnset {st.mean(x[1] for x in l):4.1f} units {st.mean(x[2] for x in l):4.1f}  max350 {st.mean(x[3] for x in l):4.1f} max450 {st.mean(x[4] for x in l):4.1f} max500 {st.mean(x[5] for x in l):4.1f}')
