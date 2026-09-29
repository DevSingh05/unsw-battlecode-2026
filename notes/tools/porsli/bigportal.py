#!/usr/bin/env python3
"""Every fatal portal crossing of OUR dragons with L>=MINLEN (default 8) on a map: the crosser's own rays
on the previous round (what they hit, where), free alternatives, and the blocker's history.
    python3 notes/tools/porsli/bigportal.py Portals|Slithery [v28|old|all] [MINLEN]"""
import collections, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.dirname(__file__))
from sim2 import simulate
from board import path_of
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
minlen = int(sys.argv[3]) if len(sys.argv) > 3 else 8
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
C = collections.Counter()
for g in gs:
    want = [d for d in g['us']['deaths'] if d['len'] >= minlen and d['cls'].startswith('portal')]
    if not want:
        continue
    S = simulate(path_of(g['game'])); m = S['map']
    heads = collections.defaultdict(dict)  # id -> round -> head after move
    for mv in S['moves']:
        if mv.get('head_after'): heads[mv['id']][mv['round']] = mv['head_after']
    for d in want:
        r = d['round']; i = d['id']
        prev = [s for s in S['sonars'] if s['id'] == i and s['round'] == r - 1]
        mvdir = d['move'][-1]
        ray = [s for s in prev if s['dir'] == mvdir]
        dest = m.step(d['head'], mvdir)
        free = [k for k, v in (d['nbrs'] or {}).items() if v in ('free', 'pearl')]
        hit = d['hit']
        blk = ''
        if hit:
            j = hit['id']
            hist = [(rr, heads[j].get(rr)) for rr in range(r - 4, r + 1) if heads[j].get(rr)]
            blk = 'blocker id%d L%d seg%d heads %s' % (j, hit['len'], hit['seg'], hist[-4:])
        rays = ['%s->%s@%s' % (s['dir'], s['hitKind'], s['end']) for s in prev]
        cat = ('noray' if not ray else ray[0]['hitKind'] + ('@exit' if ray[0]['end'] == dest else '@beyond' if ray[0]['hitKind'] != 'kelp' else ''))
        C[cat] += 1; C['alt%d' % len(free)] += 1
        print('%d %s r%d id%d L%d %s at %s move %s -> %s | alts %s | prev rays: %s | %s' % (
            g['game'], 'W' if g['win'] else 'L', r, i, d['len'], d['cls'], d['head'], d['move'], dest, free, ' '.join(rays) or 'none', blk))
print(dict(C))
