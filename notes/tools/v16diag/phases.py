#!/usr/bin/env python3
"""Aggregate per-phase splits/deaths/eats (us vs them), grouped by win/loss.
    python3 notes/tools/v16diag/phases.py [src=v16] [map=Default] [ph=0,100,200,330,420,501]
"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
args = dict(a.split('=') for a in sys.argv[1:])
src = args.get('src', 'v16'); mp = args.get('map', 'Default')
PH = [int(x) for x in args.get('ph', '0,100,200,330,420,501').split(',')]
PH = list(zip(PH, PH[1:]))
def ph(r): return next(i for i, (a, b) in enumerate(PH) if a <= r < b)
CATS = ['ally_body', 'ally_body_trapped', 'headon_ally', 'self', 'self_trapped', 'wall', 'wall_trapped', 'enemy_body', 'enemy_body_trapped', 'ram_enemy', 'rammed_by_enemy', 'nva']
for res in (False, True):
    gs = [g for g in G if g['src'] == src and g['map'] == mp and g['win'] == res]
    if not gs: continue
    n = len(gs)
    print('==== %s %s %s: %d games (elim %d)' % (src, mp, 'WINS' if res else 'LOSSES', n, sum(g['end'] == 'teamEliminated' for g in gs)))
    print('%-22s' % 'per game', ' '.join('%13s' % ('r%d-%d' % p) for p in PH))
    for side in ('us', 'them'):
        sp = collections.Counter(); dc = collections.Counter(); ea = collections.Counter(); portal = collections.Counter(); lost = collections.Counter()
        for g in gs:
            for s in g['splits']:
                if s['side'] == side: sp[ph(s['round'])] += 1
            for d in g['deaths']:
                if d['side'] == side:
                    dc[(ph(d['round']), d['cat'])] += 1; dc[(ph(d['round']), 'ALL')] += 1
                    lost[ph(d['round'])] += d['len']
                    if d['portal']: portal[ph(d['round'])] += 1
            for (sd, p, s_), v in g['eats'].items():
                if sd != side: continue
                # eats phases in diag are 100-wide; recompute not possible -> approximate by fixed PHASES
        print(' %s splits          ' % side[:2], ' '.join('%13.1f' % (sp[i] / n) for i in range(len(PH))))
        print(' %s deaths ALL      ' % side[:2], ' '.join('%13.1f' % (dc[(i, 'ALL')] / n) for i in range(len(PH))))
        print(' %s len lost        ' % side[:2], ' '.join('%13.1f' % (lost[i] / n) for i in range(len(PH))))
        print(' %s portal deaths   ' % side[:2], ' '.join('%13.1f' % (portal[i] / n) for i in range(len(PH))))
        for c in CATS:
            if sum(dc[(i, c)] for i in range(len(PH))) / n >= 0.5:
                print('   %-19s' % c, ' '.join('%13.1f' % (dc[(i, c)] / n) for i in range(len(PH))))
    # timeline means
    for c in (100, 200, 300, 400, 500):
        u = [g['tl'][c]['us'] for g in gs]; t = [g['tl'][c]['them'] for g in gs]
        print(' r%d  units us %.1f them %.1f | total us %.1f them %.1f | max us %.1f them %.1f' % (c, sum(x[0] for x in u) / n, sum(x[0] for x in t) / n,
              sum(x[1] for x in u) / n, sum(x[1] for x in t) / n, sum(x[2] for x in u) / n, sum(x[2] for x in t) / n))
    for side in ('us', 'them'):
        e = collections.Counter()
        for g in gs:
            for (sd, p, s_), v in g['eats'].items():
                if sd == side: e[(p, s_)] += v
        print(' eats %s (spawn+own corpse+enemy corpse) by 100r:' % side, ' '.join('%.0f+%.0f+%.0f' % (e[(p, 'spawn')] / n, e[(p, 'ownc')] / n, e[(p, 'encorpse')] / n) for p in range(5)))
    cr = collections.Counter()
    for g in gs: cr.update(g['cross'])
    print(' portal crossings us %.0f (fatal %.0f)  them %.0f (fatal %.0f)' % (cr[('us', 'n')] / n, cr[('us', 'died')] / n, cr[('them', 'n')] / n, cr[('them', 'died')] / n))
