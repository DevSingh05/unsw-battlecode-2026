#!/usr/bin/env python3
"""Longest-dragon trajectory + big events for one Portals game.
   python3 notes/forensics/portals/traj.py GAME [from_round]"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
gid = int(sys.argv[1]); r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 250
g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
G = simulate(os.path.join(GD, '%d.replay' % gid))
print(gid, g['opp'], 'win' if g['win'] else 'LOSS', 'us=', us)
R = dict(G['rounds'])
for r in range(r0, 500, 10):
    s = R.get(r)
    if not s: continue
    print('r%3d us top5 %-22s n=%2d tot=%3d | them top5 %-22s n=%2d tot=%3d' % (r, s[us]['lens'][:5], s[us]['n'], s[us]['total'], s[th]['lens'][:5], s[th]['n'], s[th]['total']))
print('--- our deaths L>=6 from r%d' % r0)
for d in G['deaths']:
    if d['team'] == us and d['len'] >= 6 and d['round'] >= r0:
        print(' r%d id%d L%d %s actor=%s head=%s move=%s hit=%s king=%s nbrs=%s age=%d' % (d['round'], d['id'], d['len'], d['reason'], d['actor'], d['head'], d.get('move'), d.get('hit'), d.get('king'), d.get('nbrs'), d['age']))
print('--- splits by L>=8 of ours from r%d' % r0)
for s in G['splits']:
    if s['team'] == us and s['L'] >= 8 and s['round'] >= r0:
        print(' r%d parent%d L%d -> child%d k=%d exits=%s' % (s['round'], s['parent'], s['L'], s['child'], s['k'], s['exits']))
