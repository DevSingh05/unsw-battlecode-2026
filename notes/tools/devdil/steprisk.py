#!/usr/bin/env python3
"""usage: steprisk.py MAP [ver|-] [W|L] [maxround]
Per-step ram risk for OUR small dragons (L<=5): for every single-step move, was the destination inside an
enemy head's 1-step reach, 2-step (sprint) reach only, or neither; what were the local odds (heads within
Chebyshev 3 of our head: allies incl. self vs enemies); and was the dragon rammed (enemy moved into its head)
before its next turn. Also counts how often a free alternative outside all reach existed.
    python3 notes/tools/devdil/steprisk.py MAP [ver-filter]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1]; VF = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
RES = sys.argv[3] if len(sys.argv) > 3 else None  # W or L
RMAX = int(sys.argv[4]) if len(sys.argv) > 4 else 999


def reach(m, head, L, occ, R):
    R = min(R, max(1, L - 1))
    seen = {head: 0}; fr = [head]; out = {}
    while fr:
        nf = []
        for t in fr:
            if seen[t] >= R: continue
            for d in 'NESW':
                v = m.step(t, d)
                if v is None or v in seen: continue
                seen[v] = seen[t] + 1; out[v] = seen[v]
                if v not in occ: nf.append(v)
        fr = nf
    return out


stats = collections.defaultdict(lambda: [0, 0])  # key -> [steps, rammed]
alt = collections.Counter()
for g in GS:
    if not g['map'].startswith(M) or (VF and g['ver'] != VF) or (RES and ('W' if g['win'] else 'L') != RES): continue
    o = R.load(g['path']); m = Map(o['map']); us = g['us']
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    pending = {}  # our dragon id -> key of its last step
    rnd = 0; actor = None
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']
        elif t == 'turnStart': actor = e['id']
        elif t == 'dragonAction':
            i = e['id']; a = e['action'] or {}
            if i in pending:  # survived until its next turn
                stats[pending.pop(i)][0] += 1
            if rnd > RMAX or team.get(i) != us or i not in alive or len(body[i]) > 5 or 'move' not in a or len(a['move']) != 1: continue
            occ = set()
            for j in alive: occ.update(body[j][:-1]); occ.add(body[j][-1])
            me = body[i][0]
            r1 = set(); r2 = set()
            for j in alive:
                if team[j] == us or m.cheb(body[j][0], me) > 6: continue
                rr = reach(m, body[j][0], len(body[j]), occ, 2)
                for v, dd in rr.items(): (r1 if dd == 1 else r2).add(v)
            r2 -= r1
            al = sum(1 for j in alive if team[j] == us and m.cheb(body[j][0], me) <= 3)
            en = sum(1 for j in alive if team[j] != us and m.cheb(body[j][0], me) <= 3)
            odds = 'ahead' if al > en else ('even' if al == en else 'behind')
            dest = m.step(me, a['move'][0])
            zone = 'r1' if dest in r1 else ('r2' if dest in r2 else 'safe')
            free = [m.step(me, d) for d in 'NESW']
            free = [v for v in free if v is not None and v not in occ]
            has_safe = any(v not in r1 and v not in r2 for v in free)
            key = (odds, zone)
            pending[i] = key
            if zone != 'safe': alt[(odds, zone, has_safe)] += 1
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t == 'dragonDeath':
            i = e['id']
            if i in pending:
                k = pending.pop(i)
                if e['reason'] == 'HitHeadToHead' and actor != i and team.get(actor) != us:
                    stats[k][1] += 1
                stats[k][0] += 1
            alive.discard(i)
print('%s%s: our L<=5 single steps; P(rammed before next turn)' % (M, ' ' + VF if VF else ''))
for odds in ('ahead', 'even', 'behind'):
    print('  %-6s' % odds + ''.join('  %s: n=%5d rammed %4d (%.1f%%)' % (z, stats[(odds, z)][0], stats[(odds, z)][1], 100 * stats[(odds, z)][1] / max(1, stats[(odds, z)][0])) for z in ('safe', 'r1', 'r2')))
print('  risky steps that had a reach-free alternative:', ', '.join('%s/%s %d/%d' % (o_, z, alt[(o_, z, True)], alt[(o_, z, True)] + alt[(o_, z, False)]) for o_ in ('ahead', 'even', 'behind') for z in ('r1', 'r2')))
