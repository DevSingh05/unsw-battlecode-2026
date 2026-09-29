#!/usr/bin/env python3
"""Per-loss decomposition on Slithery vs top teams (uses sims.pkl from overview.py).
For each loss: final longest us/them and gap; our 2nd/3rd; merge potential (sum ceil(L/2) of our other L>=10 at
the end, i.e. what feeding them into the king would have added); L>=12 deaths of ours r300+ by reason
(ram = head-on by enemy, self = HitSelf/HitOtherBody on own move); length lost; and the king's own
biggest collapse (drop of longest >= 8 in one round)."""
import json, os, pickle, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
C = pickle.load(open(os.path.join(HERE, 'sims.pkl'), 'rb'))
L = json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
rows = []
for g in sorted(L, key=lambda g: g['game']):
    if g['map'] != 'Slithery Fight' or g['game'] not in C: continue
    if not (g['opp'] in top or g['opp'] == '3.14159265'): continue
    c = C[g['game']]; us = g['side']; th = 'B' if us == 'A' else 'A'
    f = c['rounds'][c['last']]
    lu, lt = (f[us]['lens'] or [0]), (f[th]['lens'] or [0])
    merge = sum(math.ceil(x / 2) for x in lu[1:] if x >= 10)
    ram = [d for d in c['deaths'] if d['team'] == us and d['len'] >= 12 and d['round'] >= 300 and d['reason'] == 'HitHeadToHead' and d.get('killer_team') == th]
    slf = [d for d in c['deaths'] if d['team'] == us and d['len'] >= 12 and d['round'] >= 300 and d['reason'] in ('HitSelf', 'HitOtherBody', 'HitWall')]
    coll = []
    prev = None
    for r in sorted(c['rounds']):
        mx = c['rounds'][r][us]['max']
        if prev is not None and prev - mx >= 8: coll.append('r%d %d->%d' % (r, prev, mx))
        prev = mx
    rows.append((g, lu, lt, merge, ram, slf, coll))
    print('%d %-4s %-22s %s  final %2d v %2d gap %3d | 2nd %2d 3rd %2d | merge-pot %3d %s | rams>=12 r300+: %d (%d len) | self>=12: %d (%d len) | collapses %s' % (
        g['game'], 'W' if g['win'] else 'L', g['opp'][:22], us, lu[0], lt[0], lt[0] - lu[0], lu[1] if len(lu) > 1 else 0, lu[2] if len(lu) > 2 else 0,
        merge, 'FLIP' if (not g['win'] and merge > lt[0] - lu[0]) else '    ', len(ram), sum(d['len'] for d in ram), len(slf), sum(d['len'] for d in slf), coll))
Ls = [r for r in rows if not r[0]['win']]
print('\nlosses', len(Ls), ' mean gap %.1f' % (sum(r[2][0] - r[1][0] for r in Ls) / len(Ls)),
      ' merge-pot>gap: %d' % sum(1 for r in Ls if r[3] > r[2][0] - r[1][0]),
      ' mean rams>=12 r300+ %.2f (%.1f len)' % (sum(len(r[4]) for r in Ls) / len(Ls), sum(sum(d['len'] for d in r[4]) for r in Ls) / len(Ls)),
      ' mean self>=12 %.2f (%.1f len)' % (sum(len(r[5]) for r in Ls) / len(Ls), sum(sum(d['len'] for d in r[5]) for r in Ls) / len(Ls)))
Ws = [r for r in rows if r[0]['win']]
print('wins', len(Ws), ' mean rams>=12 %.2f self>=12 %.2f' % (sum(len(r[4]) for r in Ws) / max(1, len(Ws)), sum(len(r[5]) for r in Ws) / max(1, len(Ws))))
