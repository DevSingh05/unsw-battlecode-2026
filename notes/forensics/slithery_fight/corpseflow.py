#!/usr/bin/env python3
"""Where does each team's dead mass go, r300-500?  For every death of team T (any reason) the corpse pearls
are followed: eaten by T's final-king lineage / by another T dragon that is L>=10 when eating / by a smaller T
dragon / by the enemy / never eaten.  Deaths are split into 'feed' (backward move into own neck: HitSelf with
the head moving onto segment 1) and other.  Prints per game and means, for us and them.
    python3 notes/forensics/slithery_fight/corpseflow.py [GAME...]"""
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
A = {lab: collections.Counter() for lab in ('us', 'them')}
for gid in gids:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid))
    last = S['rounds'][-1][1]
    lens_at = {}  # (round, id) -> len via rounds snapshots
    snap = dict(S['rounds'])
    line = '%d opp=%-14s' % (gid, g['opp'][:14])
    for T, lab in ((us, 'us'), (th, 'them')):
        if not last[T]['n']: continue
        k = last[T]['king']; chain = {k}; cur = k
        while True:
            sp = [s for s in S['splits'] if s['child'] == cur]
            if not sp or sp[0]['k'] < sp[0]['L'] - sp[0]['k']: break
            cur = sp[0]['parent']; chain.add(cur)
        dead = {d['id']: d for d in S['deaths'] if d['team'] == T and d['round'] >= 300}
        feed = set()
        for d in dead.values():
            b = d['body']
            if d['reason'] == 'HitSelf' and d.get('move') and len(b) >= 2 and d.get('steps', 1) == 1:
                # backward move: destination == neck
                if S['map'].step(b[0], d['move'][0]) == b[1]: feed.add(d['id'])
        c = collections.Counter()
        for d in dead.values():
            kind = 'feed' if d['id'] in feed else 'other'
            c[(kind, 'n')] += 1; c[(kind, 'len')] += d['len']; c[(kind, 'pearls')] += (d['len'] + 1) // 2
        for e in S['eats']:
            cp = e['corpse']
            if not cp or cp[0] not in dead: continue
            kind = 'feed' if cp[0] in feed else 'other'
            if e['team'] != T: dst = 'enemy'
            elif e['id'] in chain: dst = 'king'
            elif (e['len'] or 0) >= 10: dst = 'big'
            else: dst = 'small'
            c[(kind, dst)] += 1
        for kind in ('feed', 'other'):
            c[(kind, 'lost')] = c[(kind, 'pearls')] - sum(c[(kind, x)] for x in ('king', 'big', 'small', 'enemy'))
        A[lab].update(c)
        line += ' | %s feed %d deaths (%d len): ->king %d big %d small %d enemy %d none %d ; other deaths %d (%d len): ->king %d big %d' % (
            lab, c[('feed', 'n')], c[('feed', 'len')], c[('feed', 'king')], c[('feed', 'big')], c[('feed', 'small')], c[('feed', 'enemy')], c[('feed', 'lost')],
            c[('other', 'n')], c[('other', 'len')], c[('other', 'king')], c[('other', 'big')])
    print(line)
n = len(gids)
for lab in ('us', 'them'):
    c = A[lab]
    for kind in ('feed', 'other'):
        print('MEAN %-4s %-5s deaths %.1f len %.1f pearls %.1f -> king %.1f, other L>=10 %.1f, small %.1f, enemy %.1f, never %.1f' % (
            lab, kind, c[(kind, 'n')] / n, c[(kind, 'len')] / n, c[(kind, 'pearls')] / n, c[(kind, 'king')] / n, c[(kind, 'big')] / n, c[(kind, 'small')] / n, c[(kind, 'enemy')] / n, c[(kind, 'lost')] / n))
