#!/usr/bin/env python3
"""MODE=ramahead env: instead sample L<=5 decisions with an enemy head within 2, locally ahead, units<8, r<100.
How often does a variant binary change our decision in contact situations (L<=5, enemy head within
Chebyshev 3, not locally ahead)?  Random sample of our real decisions.
    python3 notes/tools/devdil/changerate.py MAP BIN_BASE BIN_VARIANT [N=120] [seed]"""
import os, sys, pickle, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import replay_decode as R
from sim2 import Map
import botview as BV
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M, B0, B1 = sys.argv[1], sys.argv[2], sys.argv[3]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 120
random.seed(int(sys.argv[5]) if len(sys.argv) > 5 else 1)
cands = []
for g in GS:
    if not g['map'].startswith(M): continue
    o = R.load(g['path']); m = Map(o['map']); us = g['us']
    body = {}; team = {}; alive = set(); born = {}; rnd = 0
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i); born[i] = 0
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']
        elif t == 'dragonAction':
            i = e['id']
            if team.get(i) != us or i not in alive or len(body[i]) > 5: continue
            me = body[i][0]
            al = sum(1 for j in alive if team[j] == us and m.cheb(body[j][0], me) <= 3)
            en = sum(1 for j in alive if team[j] != us and m.cheb(body[j][0], me) <= 3)
            if os.environ.get('MODE') == 'ramahead':
                near = min((m.dist(body[j][0], me) for j in alive if team[j] != us), default=99)
                units = sum(1 for j in alive if team[j] == us)
                if near <= 2 and al > en and units < 8 and rnd < 100: cands.append((g['game'], i, rnd, born[i], g['win']))
            elif en >= 1 and al <= en: cands.append((g['game'], i, rnd, born[i], g['win']))
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); c = e['child']; body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c); born[c] = rnd
        elif t == 'dragonDeath': alive.discard(e['id'])
print(len(cands), 'contact decisions (not locally ahead); sampling', N)
G = {g['game']: g for g in GS}
C = collections.Counter()
for (gid, i, r, b, win) in random.sample(cands, min(N, len(cands))):
    mm, turns = BV.capture(G[gid]['path'], i, max(b, r - 40), r)
    if not turns or turns[-1]['round'] != r: continue
    try:
        o0, _ = BV.run_bot(B0, i, turns); o1, _ = BV.run_bot(B1, i, turns)
    except Exception:
        C['timeout'] += 1; continue
    a0 = o0[-1] if o0 else ''; a1 = o1[-1] if o1 else ''
    C['n'] += 1; C['changed'] += (a0 != a1)
    if a0 != a1 and len(C) < 99: print(gid, i, r, 'win' if win else 'loss', a0, '->', a1)
print(dict(C))
