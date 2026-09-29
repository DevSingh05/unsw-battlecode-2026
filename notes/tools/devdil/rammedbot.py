#!/usr/bin/env python3
"""For our dragons that got rammed (enemy moved into our head) on MAP, re-run two bot binaries on OUR last
decision before the ram and check whether each binary's move lands inside the killer's reach.
    python3 notes/tools/devdil/rammedbot.py MAP BIN_BASE BIN_VARIANT [W|L|all]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate
import botview as BV
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M, B0, B1 = sys.argv[1], sys.argv[2], sys.argv[3]; RES = sys.argv[4] if len(sys.argv) > 4 else 'L'


def reach(m, head, L, occ):
    Rr = min(2, max(1, L - 1)); seen = {head: 0}; fr = [head]; out = {}
    while fr:
        nf = []
        for t in fr:
            if seen[t] >= Rr: continue
            for d in 'NESW':
                v = m.step(t, d)
                if v is None or v in seen: continue
                seen[v] = seen[t] + 1; out[v] = seen[v]
                if v not in occ: nf.append(v)
        fr = nf
    return out


C = collections.Counter()
for g in GS:
    if not g['map'].startswith(M) or (RES != 'all' and ('W' if g['win'] else 'L') != RES): continue
    S = simulate(g['path']); us = g['us']; m = S['map']
    for d in S['deaths']:
        if d['team'] != us or d['reason'] != 'HitHeadToHead' or 'killer' not in d or d['killer_team'] == us: continue
        k = d['killer']; r = d['round']
        prev = (r, d['id']) if d['id'] < k else (r - 1, d['id'])
        sp = simulate(g['path'], stop=prev)
        if 'act' not in sp or d['id'] not in sp['body'] or 'move' not in sp['act']: continue
        occ = set()
        for j, b in sp['body'].items(): occ.update(b)
        me = sp['body'][d['id']][0]
        danger = set()
        for j, b in sp['body'].items():
            if sp['team'][j] != us and m.cheb(b[0], me) <= 6: danger |= set(reach(m, b[0], len(b), occ))
        r0 = max(S['born'].get(d['id'], 0), prev[0] - 40)
        mm, turns = BV.capture(g['path'], d['id'], r0, prev[0])
        if not turns or turns[-1]['round'] != prev[0]: C['skip'] += 1; continue
        try:
            o0, _ = BV.run_bot(B0, d['id'], turns); o1, _ = BV.run_bot(B1, d['id'], turns)
        except Exception:
            C['timeout'] += 1; continue
        a0 = o0[-1] if o0 else ''; a1 = o1[-1] if o1 else ''
        real = 'MOVE ' + ''.join(sp['act']['move'])
        def land(a):
            if not a.startswith('MOVE'): return None
            t = me
            for ch in a[5:]:
                t = m.step(t, ch)
                if t is None: return None
            return t
        C['n'] += 1; C['base==real'] += (a0 == real)
        C['base_in_reach'] += (land(a0) in danger); C['var_in_reach'] += (land(a1) in danger)
        C['var_changed'] += (a1 != a0)
        if a1 != a0 and land(a1) in danger: C['var_changed_but_still_in_reach'] += 1
        if not a1.startswith('MOVE'): C['var_split'] += 1
print(M, RES, dict(C))
