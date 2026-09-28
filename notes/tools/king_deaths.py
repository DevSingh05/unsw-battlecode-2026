#!/usr/bin/env python3
"""Deaths of each team's CURRENT longest dragon (len >= 10), by cause, in all games.
    python3 notes/tools/king_deaths.py
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')
summ = json.load(open(os.path.join(DIR, 'summary.json')))
agg = {'us': collections.Counter(), 'them': collections.Counter()}; lost = {'us': 0, 'them': 0}
ex = []
for s in summ:
    us = s['side']
    g = simulate(os.path.join(DIR, f"{s['id']}.replay"))
    snap = dict(g['rounds']); m = g['map']
    for d in g['deaths']:
        sn = snap.get(d['round'] - 1)
        if not sn or d['len'] < 10: continue
        T = d['team']
        if sn[T]['king'] != d['id']: continue
        k = 'us' if T == us else 'them'
        r = d['reason']; nfree = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        if r == 'HitSelf':
            mv = d.get('move') or ''
            back = mv and m.step(d['body'][0], mv[d['step_failed'] - 1]) == d['body'][1]
            c = 'self-trapped' if nfree == 0 else ('self-backward(feed?)' if back else 'self-other')
        elif r == 'HitHeadToHead':
            ot = d.get('killer_team') or d.get('victim_team')
            c = ('friendly-' if ot == T else 'enemy-') + ('rammed' if 'killer' in d else 'we-moved-into-head')
        elif r == 'HitOtherBody':
            c = 'body-' + (('friendly' if d['hit']['team'] == T else 'enemy') if d.get('hit') else '?') + ('-trapped' if nfree == 0 else '')
        else:
            c = r
        agg[k][c] += 1; lost[k] += d['len']
        if k == 'us': ex.append((s['id'], d['round'], d['len'], c))
for k in agg: print(k, dict(agg[k].most_common()), 'total length lost', lost[k])
print('examples (us):', ex)
