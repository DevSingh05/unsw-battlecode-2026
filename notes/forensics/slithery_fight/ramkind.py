#!/usr/bin/env python3
"""For every ram of our L>=MINL dragons (enemy head moved into our head): the killer's exact move (steps), its
length before the move, whether its head was inside our 7x7 view at our last decision, whether its tail was
visible, and pearls eaten on its sprint path (a pearl on step 1 lets even an L2 sprint twice).
    python3 .../ramkind.py MINL GAME...   (project root)"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
MINL = int(sys.argv[1]); agg = collections.Counter()
for gid in map(int, sys.argv[2:]):
    g = led[gid]; us = g['side']; path = os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)
    S = simulate(path)
    for d in S['deaths']:
        if d['team'] != us or d['len'] < MINL or d['reason'] != 'HitHeadToHead' or d.get('killer') is None or d.get('killer_team') == us: continue
        i, k, r = d['id'], d['killer'], d['round']
        st = simulate(path, stop=(r, k))  # board right before the killer acts
        steps = st['act'].get('move', [])
        kb = st['body'][k]; m = st['map']
        # our last decision board
        rd = r if i < k else r - 1
        so = simulate(path, stop=(rd, i))
        mh = so['body'][i][0]; kh = so['body'][k][0] if k in so['body'] else None
        inview = kh is not None and m.cheb(mh, kh) <= 3
        tailvis = k in so['body'] and m.cheb(mh, so['body'][k][-1]) <= 3
        visl = sum(1 for s in so['body'].get(k, []) if m.cheb(mh, s) <= 3)
        # pearls on the killer's path
        p = kb[0]; pe = 0; pe1 = 0
        for n, sd in enumerate(steps):
            p = m.step(p, sd)
            if p in st['pearls']:
                pe += 1; pe1 += (n == 0)
        kind = ('OUT-OF-VIEW' if not inview else
                'PEARL-SPRINT' if (pe1 and len(steps) > len(kb) - 1) else
                'TAIL-HIDDEN' if (not tailvis and len(steps) > max(1, visl - 1)) else
                'LONG-SPRINT>4' if len(steps) > 4 else 'IN-MODEL')
        agg[kind] += 1; agg['len_' + kind] += d['len']
        print('%d r%d our id%d L%d | killer %d L%d move %s (%d steps, pearls on path %d, first-step pearl %d) | killer head in view %s, visible segs %d, tail visible %s -> %s' % (
            gid, r, i, d['len'], k, len(kb), ''.join(steps), len(steps), pe, pe1, inview, visl, tailvis, kind), flush=True)
print(dict(agg))
