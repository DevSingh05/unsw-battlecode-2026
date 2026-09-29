#!/usr/bin/env python3
"""How our dragons get rammed: killer sprint length, killer/victim lengths, distance after OUR last move,
and whether our last move had a free alternative outside every enemy head's 2-step (sprint) reach.
    python3 notes/tools/devdil/rammed.py MAP"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1]


def reach_set(st, m, head, L, occ):
    """tiles an enemy head of length L can reach this turn (<= min(2, L-1) steps; body tiles block except as target)."""
    R = min(2, max(1, L - 1))
    seen = {head: 0}; fr = [head]; out = set()
    while fr:
        nf = []
        for t in fr:
            if seen[t] >= R: continue
            for d in 'NESW':
                v = m.step(t, d)
                if v is None or v in seen: continue
                seen[v] = seen[t] + 1; out.add(v)
                if v not in occ: nf.append(v)
        fr = nf
    return out


C = collections.defaultdict(collections.Counter)
for g in GS:
    if not g['map'].startswith(M): continue
    S = simulate(g['path']); us = g['us']; m = S['map']
    for d in S['deaths']:
        if d['team'] != us or d['reason'] != 'HitHeadToHead' or 'killer' not in d or d['killer_team'] == us: continue
        k = d['killer']; r = d['round']
        st = simulate(g['path'], stop=(r, k))
        if 'act' not in st: continue
        steps = len(st['act'].get('move', []))
        wl = 'W' if g['win'] else 'L'
        c = C[wl]; c['n'] += 1; c['steps%d' % min(steps, 3)] += 1
        c['killerL%d' % min(d['killer_len'], 5)] += 1
        # our last action: the previous turn of our dragon (same round if our id < k, else previous round)
        prev = (r, d['id']) if d['id'] < k else (r - 1, d['id'])
        sp = simulate(g['path'], stop=prev)
        if 'act' not in sp or d['id'] not in sp['body']:
            c['no_prev'] += 1; continue
        occ = set()
        for j, b in sp['body'].items(): occ.update(b[:-1] if j != d['id'] else b[:-1])
        me = sp['body'][d['id']]
        threat = set(); threat1 = set()
        for j, b in sp['body'].items():
            if sp['team'][j] == us: continue
            if m.cheb(b[0], me[0]) > 6: continue
            threat |= reach_set(sp, m, b[0], len(b), occ)
            threat1 |= reach_set(sp, m, b[0], 2, occ)  # 1-step reach
        opts = [];
        for dd in 'NESW':
            v = m.step(me[0], dd)
            if v is None or v in occ: continue
            opts.append((dd, v in threat1, v in threat))
        mv = sp['act'].get('move', [])
        chosen = m.step(me[0], mv[0]) if mv else None
        was_split = 'split' in sp['act']
        c['prev_split'] += was_split
        safe2 = [o for o in opts if not o[2]]; safe1 = [o for o in opts if not o[1]]
        if not was_split and mv:
            ch2 = chosen in threat; ch1 = chosen in threat1
            c['chose_in_1reach'] += ch1; c['chose_in_2reach_only'] += (ch2 and not ch1)
            c['had_2safe_alt'] += bool(safe2); c['had_1safe_alt'] += bool(safe1)
            if ch2 and not ch1 and safe2: c['walked_into_sprint_reach_with_2safe_alt'] += 1
            if ch1 and safe1: c['walked_into_1reach_with_1safe_alt'] += 1
            if not safe1: c['no_1safe_option'] += 1
for wl, c in C.items():
    n = c['n']; ng = sum(1 for g in GS if g['map'].startswith(M) and (g['win'] == (wl == 'W')))
    print('== %s  rammed %d (%.1f/g)' % (wl, n, n / ng))
    for k, v in sorted(c.items()): print('   %-44s %4d  %.0f%%' % (k, v, 100 * v / n))
