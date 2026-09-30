"""split breakdown r>=330 per team: (parent L, k, exits) counts.  python3 notes/consolidation/splits.py REPLAY"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tools/midgame'))
import sim2
S = sim2.simulate(sys.argv[1])
for T in 'AB':
    c = collections.Counter((x['L'], x['k'], x['exits']) for x in S['splits'] if x['team'] == T and x['round'] >= 330)
    print(T, sum(c.values()), c.most_common(12))
    by = collections.Counter((x['round'] // 25) * 25 for x in S['splits'] if x['team'] == T and x['round'] >= 300)
    print('   per25', sorted(by.items()))
    dr = collections.Counter((d['round'] // 25) * 25 for d in S['deaths'] if d['team'] == T and d['round'] >= 300)
    print('   deaths per25', sorted(dr.items()))
