#!/usr/bin/env python3
"""'Box' moves on Devil: a head steps onto the LAST free neighbour of an enemy head (boxEffect() in v29 rewards
this with +25+2*len). What happens next? The enemy's next action: rams our head (trade, both die), dies alone
(kelp/body/self/NVA), splits, or escapes because a tail moved. Counted for both teams, split W/L, r<=150.
Also the local odds at the box move and corpse pearls eaten within 8 rounds after a resulting trade.
    python3 notes/forensics/devil/box.py
"""
import collections, os, sys
from common import games, sim, GDIR, ROOT, REFMAP as m
sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
import replay_decode as RD
from sim2 import Map

res = collections.Counter(); harvest = collections.defaultdict(lambda: [0, 0, 0])
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']; W = 'W' if g['win'] else 'L'
    o = RD.load(os.path.join(GDIR, '%d.replay' % g['game']))
    mm = Map(o['map']); body = {}; team = {}
    for i, (t, pts) in enumerate(mm.dragons): body[i] = list(pts); team[i] = 'AB'[t]
    alive = set(body); rnd = 0; actor = None; pending = {}  # enemy id -> (boxer id, round, team, local)
    watch = []
    def exits(h):
        occ = set(s for j in alive for s in body[j])
        return sum(1 for d in 'NESW' if m.step(h, d) is not None and m.step(h, d) not in occ)
    pre = {}
    for e in o['events']:
        t_ = e['t']
        if t_ == 'roundStart':
            rnd = e['round']
            if rnd > 150: break
        elif t_ == 'dragonAction':
            actor = e['id']
            # resolve pending boxes when the boxed enemy acts
            if actor in pending:
                bx, br, bt, loc = pending.pop(actor)
                a = e['action'] or {}
                out = 'split' if 'split' in a else 'moves'
                pending_res = (actor, bx, bt, loc, out, rnd)
                watch.append(pending_res)
            if actor in alive:
                h = body[actor][0]
                pre = {j: exits(body[j][0]) for j in alive if team[j] != team[actor] and m.dist(body[j][0], h) <= 2}
        elif t_ == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
            i = e['id']
            if i == actor:
                h = body[i][0]
                for j, ex0 in pre.items():
                    if j in alive and m.dist(body[j][0], h) == 1 and ex0 > 0 and exits(body[j][0]) == 0:
                        loc = (sum(1 for k in alive if k != i and team[k] == team[i] and m.cheb(body[k][0], h) <= 3),
                               sum(1 for k in alive if team[k] != team[i] and m.cheb(body[k][0], h) <= 3))
                        pending[j] = (i, rnd, team[i], loc)
                pre = {}
        elif t_ == 'dragonSplit':
            p, c = e['parent'], e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t_ == 'dragonDeath':
            alive.discard(e['id'])
    dd = {(d['id']): d for d in S['deaths']}
    for (enemy, boxer, bt, loc, out, r) in watch:
        de = dd.get(enemy); db = dd.get(boxer)
        if de and de['round'] == r and de['reason'] == 'HitHeadToHead' and db and db['round'] == r:
            kind = 'rammed-us (trade)'
            ce = collections.Counter(x['team'] for x in S['eats'] if x['corpse'] and r <= x['round'] <= r + 8 and x['corpse'][0] in (enemy, boxer))
            key = (W, 'US' if bt == us else 'THEM', 'ahead' if loc[0] >= loc[1] else 'behind')
            harvest[key][0] += 1; harvest[key][1] += ce[bt]; harvest[key][2] += ce['A' if bt == 'B' else 'B']
        elif de and de['round'] == r:
            kind = 'died alone (%s)' % de['reason']
        elif out == 'split':
            kind = 'split'
        else:
            kind = 'escaped'
        res[(W, 'US' if bt == us else 'THEM', kind)] += 1
ng = collections.Counter('W' if g['win'] else 'L' for g in games())
for k in sorted(res): print('%s boxer=%-4s -> %-28s n=%4d (%.1f/g)' % (k + (res[k], res[k] / ng[k[0]])))
print('trades after a box move: corpse pearls eaten in 8 rounds, boxer team / other team')
for k in sorted(harvest):
    n, a, b = harvest[k]
    print('  %s boxer=%-4s local %-6s n=%3d  boxer %.2f / other %.2f  net %+.2f' % (k + (n, a / n, b / n, (a - b) / n)))
