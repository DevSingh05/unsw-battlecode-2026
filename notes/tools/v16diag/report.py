#!/usr/bin/env python3
"""Print per-game and aggregated tables from games.pkl (see diag.py).
    python3 notes/tools/v16diag/report.py [src=v16] [map=Default]
"""
import os, pickle, sys, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
args = dict(a.split('=') for a in sys.argv[1:])
src = args.get('src', 'v16'); mp = args.get('map', 'Default')
gs = [g for g in G if g['src'] == src and g['map'] == mp]
CH = [50, 100, 200, 300, 400, 500]


def f(t): return '%d/%d/%d' % t


print('== %s %s: %d games' % (src, mp, len(gs)))
for g in sorted(gs, key=lambda g: (g['win'], g['game'])):
    print('%d %-4s %-3s %-22s %5s end=%s r%d final us(n%d,L%d,T%d) them(n%d,L%d,T%d)' % (
        g['game'], 'W' if g['win'] else 'L', 'R' if g['ranked'] else 'u', g['opp'][:22], g['oppElo'], g['end'], g['last'],
        g['final']['us']['dragonCount'], g['final']['us']['longest'], g['final']['us']['total'],
        g['final']['them']['dragonCount'], g['final']['them']['longest'], g['final']['them']['total']))
    print('    n/total/max us  :', ' '.join('r%d %s' % (c, f(g['tl'][c]['us'])) for c in CH))
    print('    n/total/max them:', ' '.join('r%d %s' % (c, f(g['tl'][c]['them'])) for c in CH))
    for side in ('us', 'them'):
        e = g['eats']
        print('    eats %-4s' % side, ' '.join('%d:%d+%d+%d' % (ph, e[(side, ph, 'spawn')], e[(side, ph, 'ownc')], e[(side, ph, 'encorpse')]) for ph in range(5)),
              ' first>=8/12/16/20:', [g['first'][(side, t)] for t in (8, 12, 16, 20)])
    for side in ('us', 'them'):
        c = collections.Counter(d['cat'] for d in g['deaths'] if d['side'] == side)
        pc = sum(1 for d in g['deaths'] if d['side'] == side and d['portal'])
        print('    deaths %-4s %3d portal=%d' % (side, sum(c.values()), pc), dict(c.most_common()))
    big = [(d['round'], d['len'], d['cat'], d['head'], 'P' if d['portal'] else '') for d in g['deaths'] if d['side'] == 'us' and d['len'] >= 8]
    if big: print('    our L>=8 deaths:', big)
    bigt = [(d['round'], d['len'], d['cat'], d['head']) for d in g['deaths'] if d['side'] == 'them' and d['len'] >= 8]
    if bigt: print('    their L>=8 deaths:', bigt)
    print('    crossings us %d (died %d) them %d (died %d)' % (g['cross'][('us', 'n')], g['cross'][('us', 'died')], g['cross'][('them', 'n')], g['cross'][('them', 'died')]))
