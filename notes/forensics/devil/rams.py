#!/usr/bin/env python3
"""Head-on trades on Devil: who moved (starter), local odds at the starter's decision (heads within cheb 3
of the starter's head, starter excluded: allies v enemies incl. the victim), whether the starter had any
non-lethal alternative move, and corpse pearls eaten by each team within 8 rounds.
    python3 notes/forensics/devil/rams.py [maxround]  -> rams.pkl, prints per game + aggregates
"""
import sys, pickle, collections, os
from common import games, sim, state, HERE

maxr = int(sys.argv[1]) if len(sys.argv) > 1 else 150
rows = []
for g in sorted(games(), key=lambda g: g['at']):
    S = sim(g['game']); us = g['side']
    D = S['deaths']
    for i, d in enumerate(D):
        if d['round'] > maxr: break
        if d['reason'] != 'HitHeadToHead' or d['id'] != d['actor']: continue
        mover = d['id']; victim = d.get('victim')
        if victim is None: continue
        st = state(g['game'], d['round'], mover)
        m = st['map']; body = st['body']; me = body[mover][0]; T = st['team'][mover]
        loc_a = sum(1 for j, b in body.items() if j != mover and st['team'][j] == T and m.cheb(b[0], me) <= 3)
        loc_e = sum(1 for j, b in body.items() if st['team'][j] != T and m.cheb(b[0], me) <= 3)
        occ = set(t for b in body.values() for t in b)
        alt = sum(1 for dd in 'NESW' if m.step(me, dd) is not None and m.step(me, dd) not in occ)
        ce = collections.Counter(e['team'] for e in S['eats'] if e['corpse'] and d['round'] <= e['round'] <= d['round'] + 8 and e['corpse'][0] in (mover, victim))
        rows.append(dict(game=g['game'], win=g['win'], round=d['round'], ours=(T == us), mover=mover, L=d['len'], vlen=d.get('victim_len'),
                         loc_a=loc_a, loc_e=loc_e, alt=alt, steps=d.get('steps'), c_st=ce[T], c_ot=ce['A' if T == 'B' else 'B']))
pickle.dump(rows, open(os.path.join(HERE, 'rams.pkl'), 'wb'))
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in rows:
    odds = 'ahead' if r['loc_a'] >= r['loc_e'] else 'outnum'   # loc_e includes the victim
    k = ('W' if r['win'] else 'L', 'US' if r['ours'] else 'THEM', odds, 'noalt' if r['alt'] == 0 else 'alt')
    agg[k][0] += 1; agg[k][1] += r['c_st']; agg[k][2] += r['c_ot']
ng = collections.Counter('W' if g['win'] else 'L' for g in games())
for k in sorted(agg):
    n, a, b = agg[k]
    print('%s starter=%-4s %-6s %-5s n=%3d (%.1f/g) corpse starter/other %.2f/%.2f net %+.2f' % (k[0], k[1], k[2], k[3], n, n / ng[k[0]], a / n, b / n, (a - b) / n))
