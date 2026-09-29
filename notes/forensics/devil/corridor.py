#!/usr/bin/env python3
"""1-wide corridor head-ons on Devil. For every single-step move of team T whose landing tile is a vertical
1-wide corridor tile (kelp west AND east) and whose direction is N/S, walk the corridor ahead (up to 6
tiles, inside our 7x7 view: |dy|<=3 from the landing tile... we use the true board) and look for another
head facing us (toward the mover) with no side exit between. Outcome: did the mover die within 8 rounds,
and how. Split by who is coming (ally/enemy) and by team (us/them).
    python3 notes/forensics/devil/corridor.py [W|L] [maxround]
"""
import sys, collections, pickle, os
from common import games, sim, GDIR, REFMAP as m, HERE, ROOT
sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as RD

want = sys.argv[1] if len(sys.argv) > 1 else None
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 150
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


def vcorr(t):
    x, y = t
    return m.edges.get(('V', x, y), (0,))[0] == 1 and m.edges.get(('V', (x + 1) % m.w, y), (0,))[0] == 1


def facing(b):
    if len(b) < 2: return None
    for d in 'NESW':
        if m.step(b[1], d) == b[0]: return d


res = collections.Counter(); examples = []
for g in sorted(games(), key=lambda g: g['at']):
    if want and ('W' if g['win'] else 'L') != want: continue
    S = sim(g['game']); us = g['side']
    death = {d['id']: d for d in S['deaths']}
    o = RD.load(os.path.join(GDIR, '%d.replay' % g['game']))
    # replay bodies to know facings at each action
    body = {}; team = {}
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]
    # NOTE: map dragons from the replay's own map (starting layout may be swapped)
    from sim2 import Map
    mm = Map(o['map']); body = {}; team = {}
    for i, (t, pts) in enumerate(mm.dragons): body[i] = list(pts); team[i] = 'AB'[t]
    alive = set(body); rnd = 0
    for e in o['events']:
        t_ = e['t']
        if t_ == 'roundStart': rnd = e['round']
        if rnd > maxr: break
        if t_ == 'dragonAction':
            i = e['id']; a = e['action'] or {}
            mv = a.get('move') if isinstance(a, dict) else None
            if mv and len(mv) == 1 and mv[0] in 'NS' and i in alive:
                d = mv[0]; land = m.step(body[i][0], d)
                if land is not None and vcorr(land) and not vcorr(body[i][0]) or (land is not None and vcorr(land) and vcorr(body[i][0])):
                    heads = {body[j][0]: j for j in alive if j != i}
                    occ = set(s for j in alive for s in body[j])
                    cur = land; found = None
                    for k in range(6):
                        nxt = m.step(cur, d)
                        if nxt is None or not vcorr(nxt): break
                        if nxt in heads:
                            j = heads[nxt]
                            if facing(body[j]) == OPP[d]: found = (j, k + 1)
                            break
                        if nxt in occ: break
                        cur = nxt
                    entering = not vcorr(body[i][0])
                    if found and entering:
                        j, dist = found
                        dd = death.get(i)
                        died = dd is not None and dd['round'] <= rnd + 8
                        how = dd['reason'] if died else 'alive'
                        jd = death.get(j); jdied = jd is not None and jd['round'] <= rnd + 8
                        k = ('US' if team[i] == us else 'THEM', 'ally' if team[j] == team[i] else 'enemy', how, 'other-dies' if jdied else 'other-lives')
                        res[k] += 1
                        if team[i] == us and len(examples) < 400:
                            examples.append((g['game'], rnd, i, d, body[i][0], land, j, dist, len(body[i]), len(body[j]), how))
        elif t_ == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t_ == 'dragonSplit':
            p, c = e['parent'], e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t_ == 'dragonDeath':
            alive.discard(e['id'])
ng = sum(1 for g in games() if not want or ('W' if g['win'] else 'L') == want)
print('games', ng, want or 'all')
for k in sorted(res): print('  %-5s entering corridor with %-5s head facing it: mover %-13s %-11s n=%d (%.1f/g)' % (k + (res[k], res[k] / ng)))
pickle.dump(examples, open(os.path.join(HERE, 'corridor_%s.pkl' % (want or 'all')), 'wb'))
for ex in examples[:25]: print('   ', ex)
