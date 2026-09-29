#!/usr/bin/env python3
"""Per-game table + loss/win aggregates from games.pkl.  python3 notes/tools/devdil/report.py [map]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else None
PH = ['0-50', '50-100', '100-200', '200-300', '300+']
for M in ('Devil', 'Prisoners Dilemma'):
    if mp and not M.startswith(mp): continue
    gs = [g for g in G if g['map'] == M]
    print('=' * 20, M, len(gs), 'games; W', sum(g['win'] for g in gs), '; ranked', sum(1 for g in gs if g['ranked']), 'W', sum(1 for g in gs if g['ranked'] and g['win']))
    print('game   ver  R res opp(elo)                  L? end@rnd       | units u/t @25 50 100 200 300 | max u/t @50 100 200 300 | final u/t')
    for g in sorted(gs, key=lambda g: (g['win'], g['game'])):
        tl = g['tl']
        f = lambda r, i: '%d/%d' % (tl[r]['us'][i], tl[r]['them'][i]) if r in tl else '-'
        print('%d %-5s %s %s %-26s %s %-8s@%3d | %s | %s | %s/%s' % (
            g['game'], g['ver'], 'R' if g['ranked'] else 'u', 'W' if g['win'] else 'L', ('%s(%s)' % (g['opp'][:18], g.get('oppElo')))[:26],
            'L' if g['we_left'] else 'R', (g['end'] or '')[:8], g['last'],
            ' '.join(f(r, 0) for r in (25, 50, 100, 200, 300)), ' '.join(f(r, 2) for r in (50, 100, 200, 300)),
            g['final']['us']['longest'], g['final']['them']['longest']))
    for W in (False, True):
        sub = [g for g in gs if g['win'] == W]
        n = len(sub)
        if not n: continue
        print('\n--', 'WINS' if W else 'LOSSES', n)
        for r in (10, 25, 50, 75, 100, 150, 200, 300):
            vals = [g['tl'][r] for g in sub if r in g['tl']]
            # eliminated games count as 0 after end
            def mean(w, i):
                s = 0
                for g in sub:
                    if r in g['tl'] and g['last'] >= r: s += g['tl'][r][w][i]
                    elif g['last'] < r:
                        s += g['final'][w]['dragonCount' if i == 0 else ('total' if i == 1 else 'longest')]
                return s / n
            print('  r%-3d units %5.1f/%5.1f  total %5.1f/%5.1f  max %4.1f/%4.1f' % (r, mean('us', 0), mean('them', 0), mean('us', 1), mean('them', 1), mean('us', 2), mean('them', 2)))
        for w in ('us', 'them'):
            e = collections.Counter(); d = collections.Counter(); s = collections.Counter()
            for g in sub:
                for k, v in g['eats'].get(w, {}).items(): e[k] += v
                for k, v in g['deaths'].get(w, {}).items(): d[k] += v
                for k, v in g['splits'].get(w, {}).items(): s[k] += v
            print('  %-4s eats/g hot|spawn|corpse per phase: %s' % (w, '  '.join('%s %.1f|%.1f|%.1f' % (PH[i], e[(i, 'hot')] / n, e[(i, 'spawn')] / n, e[(i, 'corpse')] / n) for i in range(5))))
            print('  %-4s splits/g per phase: %s' % (w, ' '.join('%s %.1f' % (PH[i], s[i] / n) for i in range(5))))
            cats = collections.Counter()
            for (i, c), v in d.items(): cats[c] += v
            print('  %-4s deaths/g: %s' % (w, ', '.join('%s %.1f' % (c, v / n) for c, v in cats.most_common(9))))
            print('  %-4s deaths/g r0-100: %s' % (w, ', '.join('%s %.1f' % (c, sum(v for (i, cc), v in d.items() if cc == c and i < 2) / n) for c, _ in cats.most_common(9))))
