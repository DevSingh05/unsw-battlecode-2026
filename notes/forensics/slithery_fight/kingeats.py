#!/usr/bin/env python3
"""King growth source per team, r300-500: the final longest dragon of each team is traced back through
reverse splits (bulk lineage: at a split the bulk goes to the larger half). Its eats are counted per 50-round
window as spawn / own-team corpse / enemy corpse; plus its length at r300/350/400/450/end.
    python3 notes/forensics/slithery_fight/kingeats.py GAME [GAME...]   (default: all top losses)"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
gids = [int(a) for a in sys.argv[1:]] or [g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and not g['win'] and (g['opp'] in top or g['opp'] == '3.14159265')]
tot = {T: collections.Counter() for T in ('us', 'them')}
for gid in sorted(gids):
    g = led[gid]; S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid))
    us = g['side']; th = 'B' if us == 'A' else 'A'
    last = S['rounds'][-1][1]
    res = {}
    for T, lab in ((us, 'us'), (th, 'them')):
        if not last[T]['n']: continue
        k = last[T]['king']
        # lineage: walk back through splits where the bulk moved
        chain = {k: 501}
        cur = k; t_end = 501
        while True:
            sp = [s for s in S['splits'] if s['child'] == cur]
            if not sp: break
            s = sp[0]
            if s['k'] >= s['L'] - s['k']:  # child took the bulk -> before birth, the king was the parent
                chain[s['parent']] = s['round']; cur = s['parent']
            else: break
        # intervals: dragon id -> active until round
        def active(i, r):
            if i not in chain: return False
            # i is the king in [birth(i), chain[i])
            return r < chain[i]
        c = collections.Counter()
        for e in S['eats']:
            if e['round'] < 300 or not active(e['id'], e['round']): continue
            src = 'spawn' if not e['corpse'] else ('own' if e['corpse'][1] == T else 'enemy')
            w = min((e['round'] - 300) // 50, 3)
            c[(w, src)] += 1
            tot[lab][(w, src)] += 1
        lens = []
        for r0 in (300, 350, 400, 450):
            rs = dict(S['rounds'])[r0][T]
            lens.append(max([rs['ids'].get(i, 0) for i in chain if i in rs['ids']] or [0]))
        lens.append(last[T]['max'])
        res[lab] = (lens, c)
    print('%d %s opp=%s' % (gid, 'W' if g['win'] else 'L', g['opp']))
    for lab in ('us', 'them'):
        if lab not in res: continue
        lens, c = res[lab]
        print('   %-4s king len r300/350/400/450/end %s | eats per 50r (spawn/own-corpse/enemy-corpse): %s' % (lab, lens,
              '  '.join('%d/%d/%d' % (c[(w, 'spawn')], c[(w, 'own')], c[(w, 'enemy')]) for w in range(4))))
n = len(gids)
for lab in ('us', 'them'):
    print('MEAN %-4s eats per 50r r300..500 (spawn/own/enemy): %s' % (lab, '  '.join('%.1f/%.1f/%.1f' % (tot[lab][(w, 'spawn')] / n, tot[lab][(w, 'own')] / n, tot[lab][(w, 'enemy')] / n) for w in range(4))))
