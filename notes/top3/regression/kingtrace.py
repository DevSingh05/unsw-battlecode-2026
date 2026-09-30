"""Our longest dragon (and its id) every 10 rounds from r250, plus deaths of our dragons len>=8.
python3 notes/top3/regression/kingtrace.py GAME SIDE"""
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
g, us = sys.argv[1], sys.argv[2]; th = 'B' if us == 'A' else 'A'
S = sim2.simulate(os.path.join(ROOT, 'replays/regcheck/%s.replay' % g))
line = []
for r, s in S['rounds']:
    if r >= 250 and r % 10 == 0:
        line.append('r%d %s:%d top3%s | them %d' % (r, s[us]['king'], s[us]['max'], s[us]['lens'][:3], s[th]['max']))
print('\n'.join(line))
for d in S['deaths']:
    if d['team'] == us and d['len'] >= 8: print('  death r%d id%d L%d %s' % (d['round'], d['id'], d['len'], d['reason']))
