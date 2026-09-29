#!/usr/bin/env python3
"""List splits by our longest dragon (L>=MINLEN) r300-500 in Portals games; k = child length, exits = free neighbours.
   python3 notes/forensics/portals/kingsplits.py [MINLEN] [L|W|all]"""
import json, os, sys, collections, pickle
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 8
which = sys.argv[2] if len(sys.argv) > 2 else 'L'
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994 and (which == 'all' or x['win'] == (which == 'W')))
out = []
for gid in games:
    g = led[gid]; us = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid)); R = dict(S['rounds'])
    dd = {d['id']: d for d in S['deaths']}
    for s in S['splits']:
        if s['team'] != us or s['round'] < 300 or s['L'] < MIN: continue
        if R[s['round'] - 1][us]['king'] != s['parent']: continue
        pd = dd.get(s['parent']); cd = dd.get(s['child'])
        out.append(dict(game=gid, round=s['round'], parent=s['parent'], child=s['child'], L=s['L'], k=s['k'], exits=s['exits'], born=S['born'][s['parent']],
                        pdie=(pd['round'] - s['round']) if pd else None, cdie=(cd['round'] - s['round']) if cd else None))
pickle.dump(out, open(os.path.join(os.path.dirname(__file__), 'kingsplits_%s.pkl' % which), 'wb'))
C = collections.Counter()
for o in out:
    kind = 'reverse(k>=L-3)' if o['k'] >= o['L'] - 3 else ('peel(k<=3)' if o['k'] <= 3 else 'mid')
    C[(kind, 'exits%d' % min(o['exits'], 2))] += 1
    print('%d r%d parent %d L%d -> child %d k=%d exits=%d parent_born r%d parent dies +%s child dies +%s' % (o['game'], o['round'], o['parent'], o['L'], o['child'], o['k'], o['exits'], o['born'], o['pdie'], o['cdie']))
for k, v in sorted(C.items()): print(k, v, '%.2f/game' % (v / len(games)))
