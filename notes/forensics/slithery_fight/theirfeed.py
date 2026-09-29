#!/usr/bin/env python3
"""How the OPPONENT feeds its final king (r300-500): for each opponent death whose corpse pearls were eaten by
their final-king lineage, record reason, dead length, distance of the dead head to the king head, and what
it hit.  Same for us.   python3 notes/forensics/slithery_fight/theirfeed.py [GAME...]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
gids = [int(a) for a in sys.argv[1:]] or sorted(g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and not g['win'] and (g['opp'] in top or g['opp'] == '3.14159265'))
A = {'us': collections.Counter(), 'them': collections.Counter()}
for gid in gids:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = S['map']
    last = S['rounds'][-1][1]
    for T, lab in ((us, 'us'), (th, 'them')):
        if not last[T]['n']: continue
        k = last[T]['king']; chain = {k}; cur = k
        while True:
            sp = [s for s in S['splits'] if s['child'] == cur]
            if not sp or sp[0]['k'] < sp[0]['L'] - sp[0]['k']: break
            cur = sp[0]['parent']; chain.add(cur)
        dead = {d['id']: d for d in S['deaths'] if d['team'] == T and d['round'] >= 300}
        fed = collections.Counter()
        for e in S['eats']:
            if e['corpse'] and e['corpse'][0] in dead and e['id'] in chain: fed[e['corpse'][0]] += 1
        for i, n in fed.items():
            d = dead[i]; b = d['body']
            if d['reason'] == 'HitSelf' and d.get('move') and len(b) > 1 and m.step(b[0], d['move'][0]) == b[1]: how = 'backward-into-neck'
            elif d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['id'] in chain: how = 'into-king-body'
            elif d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] == T: how = 'into-ally-body'
            else: how = d['reason']
            A[lab][(how, 'n')] += 1; A[lab][(how, 'pearls')] += n; A[lab][(how, 'len')] += d['len']
n = len(gids)
for lab in ('us', 'them'):
    print(lab, 'per game, deaths r300+ whose corpse the final king ate, by how the feeder died:')
    for (how, kk), v in sorted(A[lab].items()):
        if kk == 'n': print('   %-20s deaths %.1f  len %.1f  pearls-to-king %.1f' % (how, v / n, A[lab][(how, 'len')] / n, A[lab][(how, 'pearls')] / n))
