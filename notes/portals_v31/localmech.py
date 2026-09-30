#!/usr/bin/env python3
"""Per-side mechanism numbers for local arena Portals replays (solo race: each side is an independent sample).
Run from project root: python3 notes/portals_v31/localmech.py notes/portals_v31/runX
Side naming: arena file portals_SEED_<A>_vs_<B>.replay; 'variants_v31' tag = baseline."""
import os, sys, glob, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/porsli')); sys.path.insert(0, os.path.join(ROOT, 'notes/portals_v31'))
from sim2 import simulate
from mech import game_stats
rows = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(ROOT, sys.argv[1], '*.replay'))):
    a, b = os.path.basename(p)[:-7].split('_vs_')
    a = a.split('_', 2)[2]
    G = simulate(p)
    ecnt = collections.Counter()
    for T, name in (('A', a), ('B', b)):
        o = game_stats(G, T)
        tag = 'v31' if name.startswith('variants_v31') else 'cand'
        rows[tag].append(o)
        print('%-4s %s side %s: fin %2d share450 %.2f n450 %2d mx400 %2d mx450 %2d small450 %2d 2nd499 %2d | spSmall360-450 %d | L>=8 deaths %s | drops %s' % (
            tag, os.path.basename(p)[:40], T, o[499]['mx'], o[450]['share'], o[450]['n'], o[400]['mx'], o[450]['mx'], o[450]['small'], o[499]['second'],
            o['sp_late_small'], o['big'], o['drops']))
    fin = G['rounds'][-1][1]
    print('   final A %d B %d' % (fin['A']['max'], fin['B']['max']))
for tag, L in rows.items():
    n = len(L); f = lambda c, k: sum(o[c][k] for o in L) / n
    bigp = sum(1 for o in L for x in o['big'] if x[2].startswith('portal'))
    print('%s (%d sides): r400 longest %.1f share %.2f | r450 units %.1f longest %.1f share %.2f small %.0f | r499 longest %.1f share %.2f total %.0f | small splits 360-450 %.1f | L>=8 portal deaths %d' % (
        tag, n, f(400, 'mx'), f(400, 'share'), f(450, 'n'), f(450, 'mx'), f(450, 'share'), f(450, 'small'), f(499, 'mx'), f(499, 'share'), f(499, 'tot'),
        sum(o['sp_late_small'] for o in L) / n, bigp))
