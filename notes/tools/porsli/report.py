#!/usr/bin/env python3
"""Aggregates over games.pkl.   python3 notes/tools/porsli/report.py [Portals|Slithery] [v28|old|all]"""
import collections, os, pickle, statistics as st, sys
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
PHN = ['0-100', '100-200', '200-300', '300-400', '400-500']


def mean(x):
    x = list(x)
    return sum(x) / len(x) if x else float('nan')


print('== %s %s: %d games, W %d' % (mp, ver, len(gs), sum(g['win'] for g in gs)))
print('\n-- per game')
for g in sorted(gs, key=lambda g: (g['win'], g['game'])):
    u, t = g['us'], g['them']
    big = lambda s: ' '.join('L%d@%d%s' % (d['len'], d['round'], '*' if d['was_king'] else '') for d in s['deaths'] if d['len'] >= 10)
    print('%d %s %-5s %-18s %4s end=%-14s r%d  final us %s/%s/%s them %s/%s/%s | big us: %s | them: %s' % (
        g['game'], 'W' if g['win'] else 'L', 'rk' if g['ranked'] else 'un', g['opp'][:18], g['oppElo'], g['end'], g['last'],
        *u['tl'][499], *t['tl'][499], big(u)[:120], big(t)[:80]))

for grp, sel in (('LOSS', [g for g in gs if not g['win']]), ('WIN', [g for g in gs if g['win']])):
    if not sel:
        continue
    n = len(sel)
    print('\n==== %s (%d)' % (grp, n))
    print('timeline (units / total / longest), us | them')
    for c in (50, 100, 200, 300, 400, 450, 499):
        a = [tuple(mean(g[s]['tl'][c][i] for g in sel) for i in range(3)) for s in ('us', 'them')]
        print('  r%-3d  %5.1f %6.1f %5.1f  |  %5.1f %6.1f %5.1f' % (c, *a[0], *a[1]))
    print('eats per game by phase (hot / spawn / corpse_own / corpse_enemy)')
    for i, ph in enumerate(PHN):
        row = []
        for s in ('us', 'them'):
            row.append(' / '.join('%5.1f' % mean(g[s]['eats'][(i, k)] for g in sel) for k in ('hot', 'spawn', 'corpse_own', 'corpse_enemy')))
        print('  %-8s %s  |  %s' % (ph, *row))
    print('splits per phase us | them: ', ' '.join('%.1f' % mean(g['us']['splits'][i] for g in sel) for i in range(5)), '|',
          ' '.join('%.1f' % mean(g['them']['splits'][i] for g in sel) for i in range(5)))
    print('deaths per game by class: count (length lost)   [L>=8 count]')
    for s in ('us', 'them'):
        C = collections.Counter(); Lc = collections.Counter(); B = collections.Counter()
        for g in sel:
            for d in g[s]['deaths']:
                C[d['cls']] += 1; Lc[d['cls']] += d['len']; B[d['cls']] += d['len'] >= 8
        tot = sum(C.values())
        print('  %s: total %.1f/g' % (s, tot / n))
        for k, v in C.most_common():
            print('     %-22s %6.1f (%6.1f)  [%4.2f]' % (k, v / n, Lc[k] / n, B[k] / n))
