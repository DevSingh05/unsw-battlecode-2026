#!/usr/bin/env python3
"""Portals mechanism numbers for v30/v31 server A/B replays (read-only).
   python3 notes/portals_v31/mech.py replays/ab_v30kc replays/ab_kc31     (run from project root)
   python3 notes/portals_v31/mech.py --local DIR   (arena replays; our side given by --side A/B or file name)
"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/porsli'))
from sim2 import simulate
from collect import classify
CH = [300, 350, 400, 450, 499]

def side_of(G, us):
    fin = G['rounds'][-1][1]
    for T in 'AB':
        if fin[T]['max'] == us['longest'] and fin[T]['total'] == us['total'] and fin[T]['n'] == us['dragonCount']:
            return T
    for T in 'AB':
        if fin[T]['max'] == us['longest']:
            return T
    return None

def game_stats(G, T):
    rs = dict(G['rounds']); last = G['last_round']
    o = {}
    for c in CH:
        r = rs.get(min(c, last))[T]
        L = r['lens'] + [0, 0]
        o[c] = dict(n=r['n'], tot=r['total'], mx=r['max'], share=r['max'] / max(1, r['total']), second=L[1],
                    small=sum(x for x in r['lens'] if x < 6), mid=sum(x for x in r['lens'][1:] if x >= 6))
    # peak longest and drops
    mxs = [(rn, s[T]['max']) for rn, s in G['rounds']]
    o['peak'] = max(m for _, m in mxs)
    drops = [(mxs[i][0], mxs[i - 1][1], mxs[i][1]) for i in range(1, len(mxs)) if mxs[i - 1][1] - mxs[i][1] >= 6 and mxs[i][0] >= 250]
    o['drops'] = drops
    sp = [s for s in G['splits'] if s['team'] == T]
    o['sp_late_small'] = sum(1 for s in sp if 360 <= s['round'] < 450 and s['L'] <= 5)
    o['sp_late_small_open'] = sum(1 for s in sp if 360 <= s['round'] < 450 and s['L'] <= 5 and s['exits'])
    o['sp_300_500'] = sum(1 for s in sp if s['round'] >= 300)
    o['sp_big'] = [(s['round'], s['L'], s['k'], s['exits']) for s in sp if s['round'] >= 300 and s['L'] >= 8]
    dc = collections.Counter(); dl = collections.Counter(); big = []
    for d in G['deaths']:
        if d['team'] != T or d['round'] < 250: continue
        c = classify(G, d)
        dc[c.split('_')[0] if not c.startswith('portal') else 'portal'] += 1
        if d['len'] >= 8:
            big.append((d['round'], d['len'], c)); dl[c] += d['len']
    o['deaths'] = dc; o['big'] = big; o['bigl'] = dl
    return o

def main():
    rows = []
    for d in sys.argv[1:]:
        S = json.load(open(os.path.join(ROOT, d, 'summary.json')))
        for g in S:
            if g['map'] != 'Portals': continue
            p = os.path.join(ROOT, d, '%d.replay' % g['id'])
            G = simulate(p)
            T = side_of(G, g['us']); O = 'B' if T == 'A' else 'A'
            rows.append((d, g, game_stats(G, T), game_stats(G, O)))
    for d, g, u, t in rows:
        print('%s %d %-22s %s  fin %2d v %2d | share450 %.2f v %.2f | n450 %2d v %2d | mx450 %2d v %2d | 2nd499 %2d v %2d | peak %d | spSmall360-450 %d(open %d) v %d | big deaths %s | drops %s' % (
            os.path.basename(d), g['id'], g['opp'][:22], 'W' if g['win'] else 'L', u[499]['mx'], t[499]['mx'], u[450]['share'], t[450]['share'],
            u[450]['n'], t[450]['n'], u[450]['mx'], t[450]['mx'], u[499]['second'], t[499]['second'], u['peak'], u['sp_late_small'], u['sp_late_small_open'], t['sp_late_small'],
            u['big'], u['drops']))
    def agg(sel, name):
        if not sel: return
        n = len(sel)
        print('\n== %s (%d games) ==' % (name, n))
        for c in CH:
            f = lambda k, i: sum(r[i][c][k] for r in sel) / n
            print(' r%d units %.1f v %.1f | total %.0f v %.0f | longest %.1f v %.1f | share %.2f v %.2f | 2nd %.1f v %.1f | small(<6) mass %.0f v %.0f | non-king L>=6 mass %.0f v %.0f' % (
                c, f('n', 2), f('n', 3), f('tot', 2), f('tot', 3), f('mx', 2), f('mx', 3), f('share', 2), f('share', 3), f('second', 2), f('second', 3), f('small', 2), f('small', 3), f('mid', 2), f('mid', 3)))
        print(' small splits r360-450: %.1f (open %.1f) v %.1f ; all splits r300+: %.1f v %.1f' % (
            sum(r[2]['sp_late_small'] for r in sel) / n, sum(r[2]['sp_late_small_open'] for r in sel) / n, sum(r[3]['sp_late_small'] for r in sel) / n,
            sum(r[2]['sp_300_500'] for r in sel) / n, sum(r[3]['sp_300_500'] for r in sel) / n))
        for i, who in ((2, 'us'), (3, 'them')):
            dc = collections.Counter(); dl = collections.Counter(); nb = 0
            for r in sel:
                dc.update(r[i]['deaths']); dl.update(r[i]['bigl']); nb += len(r[i]['big'])
            print(' %s deaths r250+/g: %s ; L>=8 deaths/g %.2f, length/g by class: %s' % (who, {k: round(v / n, 1) for k, v in dc.most_common()}, nb / n,
                  {k: round(v / n, 1) for k, v in dl.most_common()}))
        print(' peak longest - final longest (us): %.1f' % (sum(r[2]['peak'] - r[2][499]['mx'] for r in sel) / n))
    agg([r for r in rows if not r[1]['win']], 'LOSSES')
    agg([r for r in rows if r[1]['win']], 'WINS')
    agg(rows, 'ALL')

if __name__ == '__main__':
    main()
