#!/usr/bin/env python3
"""What happens to the body of a declared king after it reverse-splits (crown dropped): the child's fate.
   python3 notes/forensics/portals/crownfate.py [GAME...]"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = [int(a) for a in sys.argv[1:]] or sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
C = collections.Counter(); lost = collections.Counter(); n = 0
for gid in games:
    g = led[gid]; T = g['side']; n += 1
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    kr = collections.defaultdict(set); kl = {}
    for s in S['sonars']:
        if s['team'] != T: continue
        x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
        if hop == 0 and kid == (s['id'] & 1023) and L >= 2: kr[s['id']].add(s['round'])
    dd = {d['id']: d for d in S['deaths']}
    lens = collections.defaultdict(dict)
    for r, snap in S['rounds']:
        for j, L in snap[T]['ids'].items(): lens[j][r] = L
    for s in S['splits']:
        if s['team'] != T: continue
        p = s['parent']
        if not any(s['round'] - 3 <= r <= s['round'] for r in kr.get(p, ())): continue
        c = s['child']; k = s['k']
        cd = dd.get(c); pd = dd.get(p)
        cmax = max(lens[c].values()) if lens[c] else k
        became = c in kr
        fate = 'died r+%d %s' % (cd['round'] - s['round'], cd['reason']) if cd and cd['round'] - s['round'] <= 5 else ('alive/grew' if not cd else 'died later')
        pf = 'parent died r+%d' % (pd['round'] - s['round']) if pd and pd['round'] - s['round'] <= 3 else 'parent lives'
        C[('child_k>=4' if k >= 4 else 'child_k<4', 'child crowned' if became else 'child NOT crowned', fate.split(' ')[0] + (' ' + fate.split(' ')[1][:3] if fate.startswith('died r') else ''), pf.split(' r')[0])] += 1
        if len(games) <= 3: print(gid, 'r%d king %d L%d -> child %d k=%d cmax=%d %s %s %s' % (s['round'], p, s['L'], c, k, cmax, 'crowned' if became else '-', fate, pf))
for k, v in sorted(C.items(), key=lambda kv: -kv[1]): print('%5.2f/g %4d  %s' % (v / n, v, k))
