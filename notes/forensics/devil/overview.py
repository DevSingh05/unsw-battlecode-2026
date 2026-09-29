#!/usr/bin/env python3
"""Per-game table for every Devil game in replays/auto/games (ledger): units/total/max for us v them at
fixed rounds, end round, rams started by each side, corpse eats, deaths by reason.
    python3 notes/forensics/devil/overview.py
"""
import collections
from common import games, sim

RS = [10, 25, 40, 60, 80, 100, 150]
rows = []
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']; them = 'B' if us == 'A' else 'A'
    snap = dict(S['rounds'])
    def at(r):
        s = snap.get(r) or snap[max(k for k in snap if k <= r)]
        return s
    cells = []
    for r in RS:
        s = at(r)
        cells.append('%2d/%-2d' % (s[us]['n'], s[them]['n']))
    last = S['last_round']
    D = S['deaths']
    ram_by = collections.Counter(); rsn = collections.Counter()
    for d in D:
        if d['reason'] == 'HitHeadToHead' and d['id'] == d['actor']:
            ram_by[d['team']] += 1   # the mover started it
        rsn[(d['team'], d['reason'])] += 1
    ce = collections.Counter(e['team'] for e in S['eats'] if e['corpse'])
    he = collections.Counter(e['team'] for e in S['eats'] if not e['corpse'])
    rows.append(g)
    print('%d %-24s %s %s %s end%3d | units %s | rams us/them %2d/%2d | eats us %3d+%3dc them %3d+%3dc | self/body/wall us %d/%d them %d/%d' % (
        g['game'], g['opp'][:24], 'W' if g['win'] else 'L', us, 'R' if g['ranked'] else 'u', last, ' '.join(cells),
        ram_by[us], ram_by[them], he[us], ce[us], he[them], ce[them],
        rsn[(us, 'HitSelf')], rsn[(us, 'HitOtherBody')], rsn[(them, 'HitSelf')], rsn[(them, 'HitOtherBody')]))
