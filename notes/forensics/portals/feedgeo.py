#!/usr/bin/env python3
"""Deaths of small dragons (L<=6) r330-500 by distance of the death head to the team's longest dragon head, and
how many of the dropped pearls the longest dragon ate within 10 rounds. Us vs them, losses/wins.
   python3 notes/forensics/portals/feedgeo.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
A = collections.defaultdict(collections.Counter); N = collections.Counter()
for gid in games:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; N[grp] += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid)); m = S['map']; R = dict(S['rounds'])
    kingeat = collections.defaultdict(list)
    for e in S['eats']:
        if e['corpse']:
            kingeat[(e['corpse'][0])].append(e)
    for d in S['deaths']:
        if d['len'] > 6 or d['round'] < 330: continue
        T = d['team']; who = 'us' if T == us else 'them'
        snap = R.get(d['round'] - 1)
        if not snap: continue
        k = snap[T]['king']
        if k is None or k == d['id'] or k not in snap['heads']: continue
        dist = m.dist(d['head'], snap['heads'][k][0])
        b = 'd<=3' if dist <= 3 else 'd4-8' if dist <= 8 else 'd>8'
        A[(grp, who)]['deaths ' + b] += 1
        eaten_by_king = sum(1 for e in kingeat.get(d['id'], []) if e['id'] == k and e['round'] <= d['round'] + 10)
        A[(grp, who)]['pearls->king ' + b] += eaten_by_king
        A[(grp, who)]['pearls dropped ' + b] += (d['len'] + 1) // 2
for grp in 'LW':
    n = N[grp]; print('== %s (%d games) small-dragon deaths r330+, per game us / them' % (grp, n))
    for k in sorted(set(A[(grp, 'us')]) | set(A[(grp, 'them')])):
        print('  %-24s %6.1f / %6.1f' % (k, A[(grp, 'us')][k] / n, A[(grp, 'them')][k] / n))
