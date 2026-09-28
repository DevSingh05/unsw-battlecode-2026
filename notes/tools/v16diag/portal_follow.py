#!/usr/bin/env python3
"""For our fatal portal crossings into an ally body: did that ally cross the same portal pair shortly before,
from the SAME entrance (we followed it: visible to us beforehand) or from the OTHER side (head-on traffic)?
    python3 notes/tools/v16diag/portal_follow.py [Default]
"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'midgame')); sys.path.insert(0, os.path.join(HERE, '..'))
from sim2 import simulate
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAP = sys.argv[1] if len(sys.argv) > 1 else 'Default'
tot = collections.Counter(); ng = 0
for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
    if g['map'] != MAP: continue
    ng += 1
    G = simulate(os.path.join(ROOT, 'replays/v16/%d.replay' % g['game']))
    m = G['map']; us = g['side']
    cross = collections.defaultdict(list)  # id -> [(round, entry edge, entry tile)]
    for mv in G['moves']:
        steps = mv['act'].get('move', [])
        p = mv['head']
        for k, s in enumerate(steps):
            e = m.side_edge(p, s)
            if m.edges.get(e, (0, -1))[0] == 2:
                cross[mv['id']].append((mv['round'], e, p))
            q = m.step(p, s)
            if q is None: break
            p = q
    for d in G['deaths']:
        if d['team'] != us or not d.get('move'): continue
        k = d.get('step_failed', 1) - 1; mvs = d['move']
        if k >= len(mvs): continue
        e = m.side_edge(d['head'], mvs[k])
        if m.edges.get(e, (0, -1))[0] != 2: continue
        tot['portal_deaths'] += 1
        h = d.get('hit')
        cat = d['reason']
        if h is None:
            tot['other:' + cat] += 1; continue
        if h['team'] != us:
            tot['enemy_body'] += 1; continue
        j = h['id']; pe = m.partner[e]
        prev = [c for c in cross.get(j, []) if c[0] <= d['round'] and c[1] in (e, pe)]
        if not prev:
            tot['ally_not_crossed(standing/passing near exit) seg%d' % min(h['seg'], 2)] += 1; continue
        r, ee, tile = prev[-1]
        ago = d['round'] - r
        same = (ee == e and tile == d['head'])
        tot[('FOLLOWED same entrance' if same else 'OPPOSITE direction') + (' <=%d' % (3 if ago <= 3 else 10 if ago <= 10 else 99))] += 1
print(MAP, ng, 'games; per game:')
for k, v in sorted(tot.items(), key=lambda kv: -kv[1]): print('  %-55s %.1f' % (k, v / ng))
