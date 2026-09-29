#!/usr/bin/env python3
"""Death-context tables for notes/23.  python3 notes/tools/bigboard/dreport.py"""
import collections, os, pickle, sys
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, 'deathctx.pkl'), 'rb'))
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']
def selfinf(c): return not (c.startswith('rammed') or c.startswith('ram_enemy') or c == 'killed_other')
for mp in BIG + STRONG:
    gs = [g for g in R if g['map'] == mp]; n = len(gs)
    print('== %s n=%d (W %d) pocket tiles %d/%d' % (mp, n, sum(g['win'] for g in gs), gs[0]['npk'], gs[0]['ntiles']))
    for tag in ('us', 'them'):
        ds = [d for g in gs for d in g['deaths'] if d['tag'] == tag]
        si = [d for d in ds if selfinf(d['cls'])]
        L = collections.Counter(min(d['len'], 8) for d in si)
        drop = sum(d['drop'] for d in si); own = sum(d['own_re'] for d in si); en = sum(d['en_re'] for d in si)
        lost = sum(d['len'] for d in si)
        print('  %-4s deaths/g %5.1f  selfinf/g %5.1f  len %5.1f  inPocket %.2f  deg<=2 %.2f  splitParent<=5r %.2f  units@death %.1f  age med %d' % (
            tag, len(ds) / n, len(si) / n, lost / n, sum(d['pocket'] for d in si) / max(1, len(si)),
            sum((d['deg'] or 4) <= 2 for d in si) / max(1, len(si)), sum(d['split5'] is not None for d in si) / max(1, len(si)),
            sum(d['units'] or 0 for d in si) / max(1, len(si)), sorted(d['age'] for d in si)[len(si) // 2] if si else -1))
        print('       selfinf L dist %s   drop/g %.1f own re-eat %.2f enemy %.2f   NET cost/g %.1f (%.2f per death)' % (
            {k: round(v / max(1, len(si)), 2) for k, v in sorted(L.items())}, drop / n, own / max(1, drop), en / max(1, drop),
            (lost - own) / n, (lost - own) / max(1, len(si))))
        sp = [s for g in gs for s in g['splits'] if s['tag'] == tag]
        print('       splits/g %.1f  L4 %.2f  k=2 %.2f  exits<=1 %.2f  cap60 rounds/g %.1f' % (
            len(sp) / n, sum(s['L'] == 4 for s in sp) / max(1, len(sp)), sum(s['k'] == 2 for s in sp) / max(1, len(sp)),
            sum(s['exits'] <= 1 for s in sp) / max(1, len(sp)), sum(g['cap60'][tag] for g in gs) / n))
