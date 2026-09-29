#!/usr/bin/env python3
"""Mass flow r300-500 per team: pearls eaten by the team's longest dragon (king) vs others (spawn vs corpse),
deaths (count, length), splits; per 50-round window, loss/win means.  python3 notes/forensics/portals/flow.py"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
W = [(300, 350), (350, 400), (400, 450), (450, 500)]
A = collections.defaultdict(collections.Counter); N = collections.Counter()
for gid in games:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; N[grp] += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid)); R = dict(S['rounds'])
    for e in S['eats']:
        r = e['round']
        if r < 300: continue
        wi = min((r - 300) // 50, 3); T = e['team']; who = 'us' if T == us else 'them'
        snap = R.get(r - 1) or R.get(r)
        king = snap[T]['king']
        src = 'corpse' if e['corpse'] else 'spawn'
        role = 'king' if e['id'] == king else 'other'
        A[(grp, who)][(wi, role + '_' + src)] += 1
    for d in S['deaths']:
        r = d['round']
        if r < 300: continue
        wi = min((r - 300) // 50, 3); who = 'us' if d['team'] == us else 'them'
        A[(grp, who)][(wi, 'deaths')] += 1; A[(grp, who)][(wi, 'death_len')] += d['len']
for grp in 'LW':
    n = N[grp]
    print('== %s (%d games) per game; cells us / them' % (grp, n))
    keys = ['king_spawn', 'king_corpse', 'other_spawn', 'other_corpse', 'deaths', 'death_len']
    print('   window     ' + ''.join('%-16s' % k for k in keys))
    for wi, (a, b) in enumerate(W):
        print('   r%d-%d  ' % (a, b) + ''.join('%6.1f / %-6.1f  ' % (A[(grp, 'us')][(wi, k)] / n, A[(grp, 'them')][(wi, k)] / n) for k in keys))
