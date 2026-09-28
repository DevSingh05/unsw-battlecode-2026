#!/usr/bin/env python3
"""Calibration: how often does an enemy head that CAN reach our big dragon's new head actually ram it?

For every move of one of our dragons with length >= MINL (all games in rams.py's set), after the move:
for each enemy head, the BFS sprint distance to our new head (free tiles, its own tail vacating), capped
at its reach len-1 (and at 6). Outcome = our dragon rammed head-on before its next turn.
Buckets: (distance needed, enemy len class, enemy head visible from our pre-move head, enemy acts later in
this round (higher id) or next round).

    python3 notes/tools/rams/risk.py [MINL=8]   -> risk.pkl + table
"""
import collections, os, pickle, sys
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map
from rams import load_games

MINL = int(sys.argv[1]) if len(sys.argv) > 1 else 8


def need(m, occ, eb, target, maxd):
    L = len(eb); idx = {t: i for i, t in enumerate(eb)}
    dist = {eb[0]: 0}; q = deque([eb[0]])
    while q:
        u = q.popleft(); du = dist[u]
        if du >= maxd: continue
        for d in 'NESW':
            v = m.step(u, d)
            if v is None: continue
            s = du + 1
            if v == target: return s
            if v in dist: continue
            if v in idx:
                gone = (s - 1) + max(0, s - 2)
                if idx[v] < L - gone: continue
            elif v in occ: continue
            dist[v] = s; q.append(v)
    return None


def game(path, side):
    o = R.load(path); m = Map(o['map'])
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    rnd = 0; pend = {}  # our id -> record awaiting outcome
    recs = []; cur = None; start_head = None
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']
        elif t == 'turnStart':
            if cur is not None:
                finish(m, cur, body, team, alive, side, pend, recs); cur = None
        elif t == 'dragonAction':
            i = e['id']
            if i in pend:  # our dragon acts again: not rammed
                recs.append(pend.pop(i))
            a = e['action'] or {}
            if team.get(i) == side and len(body[i]) >= MINL and 'move' in a:
                cur = {'id': i, 'round': rnd, 'len': len(body[i]), 'head0': body[i][0], 'steps': len(a['move'])}
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']; alive.add(e['child'])
        elif t == 'dragonDeath':
            i = e['id']
            if cur is not None and cur['id'] == i: cur = None
            if i in pend:
                r = pend.pop(i); r['rammed'] = (e['reason'] == 'HitHeadToHead'); recs.append(r)
            alive.discard(i)
    for r in pend.values(): recs.append(r)
    return recs


def finish(m, cur, body, team, alive, side, pend, recs):
    i = cur['id']
    if i not in alive: return
    tgt = body[i][0]; occ = set()
    for j in alive: occ.update(body[j])
    thr = []
    for j in alive:
        if team[j] == side: continue
        eb = body[j]
        if m.dist(eb[0], tgt) > min(6, len(eb) - 1): continue
        dn = need(m, occ, eb, tgt, min(6, len(eb) - 1))
        if dn is not None:
            thr.append((dn, len(eb), m.cheb(eb[0], cur['head0']) <= 3, j > i))
    cur['thr'] = thr; cur['rammed'] = False
    pend[i] = cur


def main():
    games = load_games(); allr = []
    for gid, (p, side, mp, win, src) in sorted(games.items()):
        if not os.path.exists(p): continue
        for r in game(p, side): r['map'] = mp; r['game'] = gid; allr.append(r)
    pickle.dump(allr, open(os.path.join(HERE, 'risk.pkl'), 'wb'))
    report(allr)


def report(allr):
    print('our L>=%d moves' % MINL, len(allr), 'rammed', sum(r['rammed'] for r in allr))
    B = collections.defaultdict(lambda: [0, 0])
    for r in allr:
        if not r['thr']: B['no reachable enemy'][0] += 1; B['no reachable enemy'][1] += r['rammed']; continue
        dn, L, vis, later = min(r['thr'])
        lc = 'L2' if L == 2 else ('L3' if L == 3 else ('L4-5' if L <= 5 else 'L6+'))
        k = 'need%d %s %s %s' % (dn, lc, 'vis' if vis else 'unseen', 'later' if later else 'nextrnd')
        B[k][0] += 1; B[k][1] += r['rammed']
        k2 = 'need%d any' % dn; B[k2][0] += 1; B[k2][1] += r['rammed']
        k3 = 'n_threats=%d' % min(len(r['thr']), 3); B[k3][0] += 1; B[k3][1] += r['rammed']
    for k in sorted(B):
        n, x = B[k]
        if n >= 5: print('  %-32s moves %5d rammed %3d  p=%.3f' % (k, n, x, x / n))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'report':
        report(pickle.load(open(os.path.join(HERE, 'risk.pkl'), 'rb')))
    else:
        main()
