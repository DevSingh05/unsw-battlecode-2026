#!/usr/bin/env python3
"""Mechanism metrics for server A/B batches (notes/23).  python3 notes/tools/bigboard/abcheck.py replays/ab_x [replays/ab_y ...]
Per batch (our side only): wins, splits/g, sealed-child share (child flood area<4 at birth) overall and at >=50 units,
stillborn/g (child dies <=3 rounds), pump cycles (self-death <=5r after own split): child k and parent death L,
retention r0-299 = 1 - (own death length - own corpse re-eaten) / (spawn + enemy corpse eats), total length r100/r150."""
import collections, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim3 import simulate
import replay_decode as RD

for d in sys.argv[1:]:
    S = json.load(open(os.path.join(ROOT, d, 'summary.json')))
    agg = collections.Counter(); n = 0; wins = 0; tot = collections.Counter()
    for s in S:
        p = os.path.join(ROOT, d, '%d.replay' % s['id'])
        if not os.path.exists(p): continue
        G = simulate(p); res = G['result']
        us = 'A' if res['A'] == s['us'] else 'B'
        n += 1; wins += s['win']
        death = {x['id']: x for x in G['deaths']}
        for sp in G['splits']:
            if sp['team'] != us or sp['round'] >= 350: continue
            agg['splits'] += 1; agg['sealed'] += sp['carea'] < 4
            if sp['units_before'] >= 50: agg['splits50'] += 1; agg['sealed50'] += sp['carea'] < 4
            cd = death.get(sp['child'])
            if cd and cd['round'] - sp['round'] <= 3: agg['stillborn'] += 1
            pd = death.get(sp['parent'])
            if pd and pd['round'] - sp['round'] <= 5 and pd['actor'] == pd['id'] and pd['reason'] != 'HitHeadToHead':
                agg['cyc'] += 1; agg['cyc_k'] += sp['k']; agg['cyc_pl'] += pd['len']
        fresh = sum(1 for e in G['eats'] if e['team'] == us and e['round'] < 300 and (not e['corpse'] or e['corpse'][1] != us))
        own = sum(1 for e in G['eats'] if e['team'] == us and e['round'] < 300 and e['corpse'] and e['corpse'][1] == us)
        dl = sum(x['len'] for x in G['deaths'] if x['team'] == us and x['round'] < 300)
        agg['fresh'] += fresh; agg['burn'] += dl - own
        rs = dict(G['rounds'])
        for r in (100, 150):
            if r in rs: tot['us%d' % r] += rs[r][us]['total']; tot['th%d' % r] += rs[r]['B' if us == 'A' else 'A']['total']
    if not n: continue
    print('%-22s n=%d W=%d | splits/g %.0f sealed %.2f (>=50u %.2f) stillborn/g %.1f | pump cycles/g %.0f child k %.2f parent dies L %.2f | retention %.2f | total r100 %.0f/%.0f r150 %.0f/%.0f' % (
        d, n, wins, agg['splits'] / n, agg['sealed'] / max(1, agg['splits']), agg['sealed50'] / max(1, agg['splits50']), agg['stillborn'] / n,
        agg['cyc'] / n, agg['cyc_k'] / max(1, agg['cyc']), agg['cyc_pl'] / max(1, agg['cyc']), 1 - agg['burn'] / max(1, agg['fresh']),
        tot['us100'] / n, tot['th100'] / n, tot['us150'] / n, tot['th150'] / n))
