#!/usr/bin/env python3
"""Reverse splits (U-turns, child k >= L-3) of our king-lineage dragons r350+ in losses: round, L, cost (the L2
parent left behind), ally heads within Manhattan 3 of the king head at the split (a feeder in the way?), enemy heads
within 4, and whether the child died within 10 rounds.   python3 .../kingsplit.py [GAME...]"""
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
agg = collections.Counter()
for gid in gids:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); snap = dict(S['rounds'])
    death = {d['id']: d for d in S['deaths']}
    for T, lab in ((us, 'us'), (th, 'them')):
        for s in S['splits']:
            if s['team'] != T or s['round'] < 350 or s['k'] < s['L'] - 3 or s['L'] < 12: continue
            prev = snap.get(s['round'] - 1)
            if not prev or prev[T]['max'] > s['L'] + 2: continue  # only the (near-)longest
            ph = prev['heads'].get(s['parent'])
            if not ph: continue
            al = sum(1 for j, (h, L, t) in prev['heads'].items() if t == T and j != s['parent'] and abs(h[0] - ph[0][0]) + abs(h[1] - ph[0][1]) <= 3)
            en = sum(1 for j, (h, L, t) in prev['heads'].items() if t != T and abs(h[0] - ph[0][0]) + abs(h[1] - ph[0][1]) <= 4)
            cd = death.get(s['child']); died = cd is not None and cd['round'] - s['round'] <= 10
            agg[(lab, 'n')] += 1; agg[(lab, 'ally')] += al > 0; agg[(lab, 'died')] += died; agg[(lab, 'enemy')] += en > 0
            if lab == 'us':
                print('%d r%d king-split L%d -> child %d L%d (exits %d) ally heads<=3: %d enemy heads<=4: %d child died<=10r: %s%s' % (
                    gid, s['round'], s['L'], s['child'], s['k'], s['exits'], al, en, died, (' (%s L%d r%d)' % (cd['reason'], cd['len'], cd['round'])) if died else ''))
n = len(gids)
for lab in ('us', 'them'):
    print(lab, 'per game: king U-turn splits %.2f, with ally head <=3 %.2f, enemy head <=4 %.2f, child dead <=10r %.2f' % (
        agg[(lab, 'n')] / n, agg[(lab, 'ally')] / n, agg[(lab, 'enemy')] / n, agg[(lab, 'died')] / n))
