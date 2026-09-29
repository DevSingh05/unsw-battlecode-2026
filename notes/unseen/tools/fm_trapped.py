#!/usr/bin/env python3
"""Trapped deaths of our L>=5 dragons: could a reverse split (SPLIT L-2, child = rear) have saved the rear?

    python3 notes/unseen/tools/fm_trapped.py DIR [--us v24]

For each of our deaths where the mover had no free/pearl neighbour, look at the tail tile at that moment:
  tail_exit  = tail has a free/pearl neighbour (not counting the segment before it)  -> split would have saved L-2
  no_exit    = the tail is boxed as well
Also records what boxed the head in (own body / ally / enemy / kelp) and whether it was a self-coil
(only own body + kelp around the head), and how many rounds before death the head last had >=2 free exits.
"""
import collections, glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2

us = 'v24'
if '--us' in sys.argv: us = sys.argv[sys.argv.index('--us') + 1]
paths = []
for a in sys.argv[1:]:
    if a.startswith('-') or a == us: continue
    paths += sorted(glob.glob(os.path.join(a, '**', '*.replay'), recursive=True)) if os.path.isdir(a) else [a]
C = collections.Counter(); box = collections.Counter(); ex = collections.defaultdict(list); lostL = collections.Counter()
for p in paths:
    a, b = os.path.basename(p)[:-7].split('_vs_')
    side = 'A' if us in a else 'B'
    G = sim2.simulate(p); m = G['map']
    targets = []
    for d in G['deaths']:
        if d['team'] != side or d['len'] < 5 or d['actor'] != d['id']: continue
        nb = d.get('nbrs', {})
        if any(v in ('free', 'pearl') for v in nb.values()): continue
        if d['round'] >= 400: continue  # late merges
        targets.append(d)
    for d in targets:
        st = sim2.simulate(p, stop=(d['round'], d['id']))
        if st is None: continue
        bodies = st['body']; bd = bodies[d['id']]
        occ = set()
        for j, bb in bodies.items(): occ.update(bb)
        tail = bd[-1]; pre = bd[-2]
        texit = 0
        for dd in 'NESW':
            t = m.step(tail, dd)
            if t is None or t == pre: continue
            if t not in occ: texit += 1
        kinds = set()
        for v in d['nbrs'].values():
            kinds.add(v if isinstance(v, str) else v[0])
        k = 'self-coil' if kinds <= {'self', 'kelp'} else ('+'.join(sorted(kinds)))
        cat = 'tail_exit' if texit else 'no_exit'
        C[cat] += 1; box[k] += 1; lostL[cat] += d['len']
        if len(ex[cat]) < 6: ex[cat].append((os.path.basename(p)[:22], d['round'], d['id'], d['len'], k))
print('games', len(paths))
print('trapped L>=5 deaths r<400:', dict(C), ' length lost', dict(lostL))
print('boxed by', dict(box.most_common()))
for c, e in ex.items(): print(' ', c, e)
