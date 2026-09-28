#!/usr/bin/env python3
"""Classify every death of one of OUR dragons with length >= 8 in recent server games.
    python3 notes/tools/bigdeaths/classify.py
Categories: portal (fatal step crossed a portal), doomed (no free/pearl neighbour: split would have saved part),
chose (had a free neighbour but moved into death), rammed (killed on another dragon's turn), other.
"""
import collections, glob, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import replay_decode as R
games = {}
for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
    games[g['game']] = (os.path.join(ROOT, 'replays/v16/%d.replay' % g['game']), g['side'], g['map'], g['win'])
for d in glob.glob(os.path.join(ROOT, 'replays/ab_*/summary.json')):
    for g in json.load(open(d)):
        p = os.path.join(os.path.dirname(d), '%d.replay' % g['id'])
        if not os.path.exists(p): continue
        res = R.load(p)['result']
        games[g['id']] = (p, 'A' if res['A'] == g['us'] else 'B', g['map'], g['win'])
C = collections.Counter(); byMap = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
n = 0
for gid, (p, side, mp, win) in games.items():
    if not os.path.exists(p): continue
    G = simulate(p); m = G['map']; n += 1
    for d in G['deaths']:
        if d['team'] != side or d['len'] < 8: continue
        nb = d.get('nbrs', {})
        free = [k for k, v in nb.items() if v in ('free', 'pearl')]
        if d['actor'] != d['id']:
            cat = 'rammed' if d['reason'] == 'HitHeadToHead' else 'killed_on_other_turn'
        else:
            mv = d.get('move') or ''
            k = d.get('step_failed', 1) - 1
            crossed = bool(mv) and m.edges.get(m.side_edge(d['head'], mv[k]), (0, -1))[0] == 2
            if crossed: cat = 'portal_' + d['reason']
            elif not free: cat = 'doomed_' + d['reason']
            elif d['reason'] == 'HitHeadToHead': cat = 'chose_headon(vs L%s)' % ('<=3' if (d.get('victim_len') or 0) <= 3 else '>3')
            else: cat = 'chose_' + d['reason']
        late = 'late' if d['round'] >= 400 else 'mid'
        C[cat] += 1; byMap[mp][cat] += 1
        if len(ex[cat]) < 4: ex[cat].append((gid, d['round'], d['len'], d['head']))
print('games', n)
for k, v in C.most_common(): print('%-32s %4d  (%.2f/game)  e.g. %s' % (k, v, v / n, ex[k][:3]))
print()
for mp, c in sorted(byMap.items()): print('%-18s' % mp, dict(c.most_common(5)))
