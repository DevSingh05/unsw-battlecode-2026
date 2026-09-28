#!/usr/bin/env python3
"""How often would an escape rule fire, and how often is our big dragon rammed when it does?

At every decision of one of our dragons with length >= MINL (pre-action board), evaluate each legal 1-step
move with the bot's own threat model (visible enemy heads only, reach = min(visLen-1, 4), BFS over tiles
known free) and with a 'tail-unknown' variant (reach >= UNK when the enemy's tail is out of view).
Record: all legal moves flagged (the escape trigger), the action taken, and whether we were rammed before
our next turn.

    python3 notes/tools/rams/trigger.py [MINL=8]   -> trigger.pkl + table
"""
import collections, os, pickle, sys
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map
from rams import load_games

MINL = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8


def bot_dist(m, occ, lastidx, vis, us, start, target, reach):
    dist = {start: 0}; q = deque([start])
    while q:
        u = q.popleft()
        if dist[u] >= reach: continue
        for d in 'NESW':
            v = m.step(u, d)
            if v is None or v in dist: continue
            dist[v] = dist[u] + 1
            if v == target: return dist[v]
            j = occ.get(v)
            if j is not None and (j[0] == us or vis(v)) and j[1] < lastidx[j[0]]: continue
            q.append(v)
    return None


def decision(m, us, body, team, alive, side, pearls):
    me = body[us]; head = me[0]; L = len(me)
    occ = {}
    for j in alive:
        for i, s in enumerate(body[j]): occ[s] = (j, i)
    lastidx = {j: len(body[j]) - 1 for j in alive}
    vis = lambda p: m.cheb(p, head) <= 3
    heads = []
    for j in alive:
        if team[j] == side: continue
        eb = body[j]
        if not vis(eb[0]): continue
        vl = sum(1 for s in eb if vis(s))
        heads.append((j, eb[0], vl, vl >= len(eb), len(eb)))
    moves = []
    for d in 'NESW':
        t = m.step(head, d)
        if t is None or t in occ: continue
        dists = []
        for (j, h, vl, tk, Lj) in heads:
            if m.dist(h, t) > 4 and True:
                # manhattan lower bound only valid without portals; keep BFS for near heads
                pass
            bd = bot_dist(m, occ, lastidx, vis, us, h, t, 4)
            if bd is not None: dists.append((bd, vl, tk, Lj))
        moves.append((d, t, dists))
    return moves


def game(path, side):
    o = R.load(path); m = Map(o['map'])
    body = {}; team = {}; alive = set(); pearls = set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    rnd = 0; pend = {}; recs = []; actor = None
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']
        elif t == 'turnStart': actor = e['id']
        elif t == 'dragonAction':
            i = e['id']
            if i in pend: recs.append(pend.pop(i))
            if team.get(i) == side and i in alive and len(body[i]) >= MINL:
                a = e['action'] or {}
                mv = decision(m, i, body, team, alive, side, pearls)
                pend[i] = {'round': rnd, 'id': i, 'len': len(body[i]), 'moves': mv, 'act': a, 'rammed': False}
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'tileChange':
            (pearls.add if e['hasPearl'] else pearls.discard)(e['tile'])
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']; alive.add(e['child'])
        elif t == 'dragonDeath':
            i = e['id']
            if i in pend:
                r = pend.pop(i); r['rammed'] = e['reason'] == 'HitHeadToHead' and actor != i
                r['reason'] = e['reason']; r['own_turn'] = actor == i; recs.append(r)
            alive.discard(i)
    recs += list(pend.values())
    return recs


def flagged(dists, rule):
    for (bd, vl, tk, Lj) in dists:
        if bd <= rule(vl, tk): return True
    return False


RULES = {
    'current': lambda vl, tk: min(max(1, vl - 1), 4),
    'unk3': lambda vl, tk: min(max(1, vl - 1) if tk else max(vl - 1, 3), 4),
    'unk2': lambda vl, tk: min(max(1, vl - 1) if tk else max(vl - 1, 2), 4),
    'cap2': lambda vl, tk: min(max(1, vl - 1) if tk else max(vl - 1, 2), 2),
}


def report(recs):
    n = len(recs); ram = sum(r['rammed'] for r in recs)
    print('decisions of our L>=%d' % MINL, n, 'rammed before next turn', ram)
    for name, rule in RULES.items():
        trig = [r for r in recs if r['moves'] and all(flagged(d, rule) for (_, _, d) in r['moves'])]
        chosen_flag = 0
        print('  rule %-8s all-moves-flagged: %5d decisions (%.2f per game-dragon-100r), rammed %3d (p=%.2f); not-trig rammed %d' % (
            name, len(trig), 0, sum(r['rammed'] for r in trig), sum(r['rammed'] for r in trig) / max(1, len(trig)),
            sum(r['rammed'] for r in recs if r not in trig)))
        # decisions where the chosen move was flagged under this rule while an unflagged move existed
        some = [r for r in recs if r['moves'] and any(not flagged(d, rule) for (_, _, d) in r['moves'])]
        print('           some move unflagged: %d, rammed %d' % (len(some), sum(r['rammed'] for r in some)))


def main():
    games = load_games(); allr = []; ng = 0
    for gid, (p, side, mp, win, src) in sorted(games.items()):
        if not os.path.exists(p): continue
        ng += 1
        for r in game(p, side): r['map'] = mp; r['game'] = gid; allr.append(r)
    pickle.dump({'recs': allr, 'ngames': ng}, open(os.path.join(HERE, 'trigger.pkl'), 'wb'))
    report(allr)


if __name__ == '__main__':
    if 'report' in sys.argv:
        report(pickle.load(open(os.path.join(HERE, 'trigger.pkl'), 'rb'))['recs'])
    else:
        main()
