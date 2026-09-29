#!/usr/bin/env python3
"""Split-child viability at birth vs early death (notes/23).  python3 notes/tools/bigboard/splitviab.py [--jobs 6]
Per split: child free neighbours / flood area (cap 30) at birth, and whether the child (and parent) die within 10 rounds."""
import collections, os, pickle, sys
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim3 import simulate
from collect import games
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']

def run(g):
    try: G = simulate(g['path'])
    except Exception: return None
    us = g['side']
    death = {d['id']: d for d in G['deaths']}
    out = []
    for s in G['splits']:
        cd = death.get(s['child']); pd = death.get(s['parent'])
        out.append({'tag': 'us' if s['team'] == us else 'them', 'round': s['round'], 'L': s['L'], 'k': s['k'], 'units': s['units_before'],
                    'cfree': s['cfree'], 'carea': s['carea'], 'parea': s['parea'],
                    'cdie': (cd['round'] - s['round']) if cd else 999, 'pdie': (pd['round'] - s['round']) if pd else 999,
                    'cdlen': cd['len'] if cd else None})
    return {'game': g['game'], 'map': g['map'], 'win': g['win'], 'splits': out}

if __name__ == '__main__':
    if '--report' not in sys.argv:
        jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 6
        gs = [g for g in games() if g['map'] in BIG + STRONG and g['top']]
        with Pool(jobs) as p:
            res = [r for r in p.imap(run, gs, chunksize=2) if r]
        pickle.dump(res, open(os.path.join(H, 'splitviab.pkl'), 'wb'))
    R = pickle.load(open(os.path.join(H, 'splitviab.pkl'), 'rb'))
    for grp, maps in (('BIG', BIG), ('STRONG', STRONG)) + tuple((m, [m]) for m in BIG + STRONG):
        gs = [g for g in R if g['map'] in maps]; n = len(gs)
        print('== %s n=%d' % (grp, n))
        for tag in ('us', 'them'):
            sp = [s for g in gs for s in g['splits'] if s['tag'] == tag and s['round'] < 350]
            if not sp: continue
            cls = lambda s: 'dead-end' if s['carea'] < 4 else ('cramped' if s['carea'] < 12 else 'open')
            c = collections.Counter(cls(s) for s in sp)
            parts = []
            for k in ('dead-end', 'cramped', 'open'):
                ss = [s for s in sp if cls(s) == k]
                parts.append('%s %.0f/g (child dies<=3r %.0f%%, <=10r %.0f%%)' % (k, len(ss) / n, 100 * sum(s['cdie'] <= 3 for s in ss) / max(1, len(ss)),
                                                                               100 * sum(s['cdie'] <= 10 for s in ss) / max(1, len(ss))))
            print('  %-4s splits<r350 %.0f/g | %s' % (tag, len(sp) / n, ' | '.join(parts)))
            print('       stillborn (child dies<=3r) %.1f/g ; child k: %s ; dead-end share %.2f' % (
                sum(s['cdie'] <= 3 for s in sp) / n, dict(collections.Counter(min(s['k'], 5) for s in sp).most_common()), c['dead-end'] / len(sp)))
