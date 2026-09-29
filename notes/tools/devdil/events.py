#!/usr/bin/env python3
"""Death/split timeline of one game.  python3 notes/tools/devdil/events.py GAME [maxround]"""
import os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
G = {g['game']: g for g in pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))}
g = G[int(sys.argv[1])]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 999
print(g['game'], g['map'], g['opp'], 'win' if g['win'] else 'loss', 'we are', g['us'], 'left' if g['we_left'] else 'right', g['end'], g['last'])
ser = {x[0]: x for x in g["series"]}
ev = [(d['round'], 0, d) for d in g['dl']] + [(s['round'], 1, s) for s in g['splitlist']]
for r, k, e in sorted(ev, key=lambda t: (t[0], t[1])):
    if r > mx: break
    s = ser.get(r)
    u = '%2d/%2d' % (s[1], s[4]) if s else '     '
    if k == 0:
        extra = ''
        if e['cat'] in ('ram_enemy',): extra = 'victim L%s' % e['victim_len']
        if e['cat'] == 'rammed_by_enemy': extra = 'killer L%s' % e['killer_len']
        print('r%3d %s %-4s DIES  id%-3d L%-2d %-18s%s head%s mv=%s age%d %s nb=%s' % (r, u, e['who'], e['id'], e['len'], e['cat'], 'P' if e['portal'] else ' ', e['head'], e['move'], e['age'], extra,
              ''.join((v[0][0] if isinstance(v, tuple) else v[0]) for v in e['nbrs'].values()) if e['nbrs'] else ''))
    else:
        print('r%3d %s %-4s split id%-3d L%d -> child %d (k%d) exits%d enemy_d%d' % (r, u, e['who'], e['parent'], e['L'], e['child'], e['k'], e['exits'], e['enemy_dist']))
