"""Us vs calc from ground truth: per L<=3 dragon-turn, share with a pearl within BFS<=3 / <=8, share where a 'free' pearl
(no other head gets there first) is within 3 / 8, eat rate, own heads within Cheb 3.  Phases r0-59 / r60-199 / r200-349."""
import collections, pickle
from common import *
PH = [(0, 59), (60, 199), (200, 349)]
for g in GAMES:
    S = sim(g); us = GAMES[g]; th = 'B' if us == 'A' else 'A'
    gt = pickle.load(open('gt_%d.pkl' % g, 'rb'))
    ate = collections.Counter((e['id'], e['round']) for e in S['eats'])
    print('game', g, 'us', us)
    print('  phase    team  turns  eat%%   pearl<=3  pearl<=8  free<=3  free<=8  allies3  enemy<=3')
    for a, b in PH:
        for T, nm in ((us, 'us'), (th, 'calc')):
            xs = [(k, v) for k, v in gt.items() if v['T'] == T and a <= k[1] <= b and v['L'] <= 3]
            if not xs: continue
            n = len(xs)
            f = lambda c: 100.0 * sum(1 for k, v in xs if c(k, v)) / n
            print('  r%3d-%3d %-5s %5d  %5.1f   %6.1f   %6.1f   %6.1f   %6.1f   %5.2f   %6.1f' % (a, b, nm, n, f(lambda k, v: ate[k] > 0),
                  f(lambda k, v: v['pd'] <= 3), f(lambda k, v: v['pd'] <= 8), f(lambda k, v: v['free_pd'] <= 3), f(lambda k, v: v['free_pd'] <= 8),
                  sum(v['allies3'] for k, v in xs) / n, f(lambda k, v: v['en'] <= 3)))
