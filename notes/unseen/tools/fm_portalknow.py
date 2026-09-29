#!/usr/bin/env python3
"""How many portal pairs could our dragons know on an unknown map, alone vs if they shared what they see?

    python3 notes/unseen/tools/fm_portalknow.py REPLAY... [--us v24]

A pair is 'known' by a dragon once it has seen both of its edges in its own 7x7 window (LEARN_PORTALS rule;
children start with no memory). 'team' = union over all our dragons ever (what perfect sonar sharing would give).
Prints, at r50/100/200/300: pairs total, pairs known by the team union, and the mean pairs known per living dragon.
"""
import collections, glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map

us = 'v24'
if '--us' in sys.argv: us = sys.argv[sys.argv.index('--us') + 1]
paths = []
for a in sys.argv[1:]:
    if a.startswith('-') or a == us: continue
    paths += sorted(glob.glob(os.path.join(a, '**', '*.replay'), recursive=True)) if os.path.isdir(a) else [a]
for p in paths:
    a, b = os.path.basename(p)[:-7].split('_vs_'); side = 'A' if us in a else 'B'
    o = R.load(p); m = Map(o['map'])
    pid = {e: k[1] for e, k in m.edges.items() if k[0] == 2}
    pairs = collections.defaultdict(set)
    for e, i in pid.items(): pairs[i].add(e)
    npairs = len(pairs)
    if npairs == 0: continue
    body = {}; team = {}; seen = {}; teamseen = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; seen[i] = set()
    def look(i):
        hx, hy = body[i][0]
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                t = m.wrap(hx + dx, hy + dy)
                for d in 'NESW':
                    e = m.side_edge(t, d)
                    if e in pid: seen[i].add(e); teamseen.add(e)
    def known(s): return sum(1 for i, es in pairs.items() if es <= s)
    rnd = 0; report = {}
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            if rnd in (50, 100, 200, 300):
                alive = [i for i in body if team[i] == side]
                per = [known(seen[i]) for i in alive]
                report[rnd] = (known(teamseen), sum(per) / max(1, len(per)), sum(1 for x in per if x > 0) / max(1, len(per)))
            rnd = e['round']
        elif t == 'dragonUpdate':
            bb = body[e['id']]; bb.insert(0, e['head'])
            while bb and bb[-1] != e['tail']: bb.pop()
            if team[e['id']] == side: look(e['id'])
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']; seen[e['child']] = set()
        elif t == 'dragonDeath':
            body.pop(e['id'], None)
    print(os.path.relpath(p, ROOT)[-70:], 'pairs', npairs)
    for r, (tk, mean, frac) in sorted(report.items()):
        print('   r%3d  team-union knows %2d/%d pairs | per living dragon mean %.2f, %.0f%% know >=1' % (r, tk, npairs, mean, 100 * frac))
