#!/usr/bin/env python3
"""Where does the king's length come from, and where do feeders' pearls go?
    python3 notes/tools/porsli/kingflow.py Portals|Slithery [v28|old|all]
'king' = the team's longest dragon at the end of the previous round (ids change on reverse splits,
so this follows the mass, not the id). Per 50-round window from r250:
  king eats (spawn / corpse), max length gain, units, # of dragons >= 0.5*max,
  deaths of dragons within 4 of the king and whose pearls went where (king / other ally / enemy / never eaten).
"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import pickle
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
paths = {}
for d in ('v28', 'v19plus', 'v16'):
    for x in json.load(open(os.path.join(ROOT, 'replays', d, 'ledger.json'))):
        paths.setdefault(x['game'], os.path.join(ROOT, 'replays', d, '%d.replay' % x['game']))
W = [(250, 300), (300, 350), (350, 400), (400, 450), (450, 500)]
agg = {k: collections.defaultdict(float) for k in ('LOSS', 'WIN')}
cnt = collections.Counter()
for g in gs:
    S = simulate(paths[g['game']])
    rs = dict(S['rounds'])
    grp = 'WIN' if g['win'] else 'LOSS'
    cnt[grp] += 1
    A = agg[grp]
    for tag, T in (('us', g['side']), ('them', 'B' if g['side'] == 'A' else 'A')):
        kingAt = {rn: sn[T]['king'] for rn, sn in S['rounds']}
        # corpse tiles -> dead dragon id; who ate
        for e in S['eats']:
            if e['team'] != T or e['round'] < 250:
                continue
            wi = min((e['round'] - 250) // 50, 4)
            k = kingAt.get(e['round'] - 1)
            if e['id'] == k:
                A['%s_k%d_%s' % (tag, wi, 'c' if e['corpse'] else 's')] += 1
        for wi, (a, b) in enumerate(W):
            ra, rb = rs.get(a), rs.get(min(b, S['last_round']))
            if ra and rb:
                A['%s_gain%d' % (tag, wi)] += rb[T]['max'] - ra[T]['max']
                A['%s_units%d' % (tag, wi)] += ra[T]['n']
                A['%s_big%d' % (tag, wi)] += sum(1 for L in ra[T]['lens'] if L >= max(8, ra[T]['max'] // 2))
        # feeder corpses: deaths of our dragons within 4 of the king, r300+
        dead = {}
        for d in S['deaths']:
            if d['team'] == T and d['round'] >= 300 and d.get('king') and d['king'][2] <= 4 and d['len'] < d['king'][1] and d['actor'] == d['id']:
                dead[d['id']] = d
                wi = min((d['round'] - 250) // 50, 4)
                A['%s_feedn%d' % (tag, wi)] += 1
                A['%s_feedpearls%d' % (tag, wi)] += (d['len'] + 1) // 2
        for e in S['eats']:
            c = e['corpse']
            if not c or c[0] not in dead:
                continue
            d = dead[c[0]]
            wi = min((d['round'] - 250) // 50, 4)
            if e['team'] != T:
                A['%s_fate%d_enemy' % (tag, wi)] += 1
            elif e['id'] == kingAt.get(e['round'] - 1):
                A['%s_fate%d_king' % (tag, wi)] += 1
            else:
                A['%s_fate%d_other' % (tag, wi)] += 1

for grp in ('LOSS', 'WIN'):
    n = cnt[grp]
    if not n:
        continue
    A = agg[grp]
    print('==== %s %s %s (%d games), per game per window r250-300 / 300-350 / 350-400 / 400-450 / 450-500' % (mp, ver, grp, n))
    for tag in ('us', 'them'):
        f = lambda k: ' '.join('%5.1f' % (A['%s_%s' % (tag, k % i)] / n) for i in range(5))
        print(' %s' % tag)
        print('   longest gain       ', f('gain%d'))
        print('   units at start     ', f('units%d'))
        print('   dragons>=max(8,M/2)', f('big%d'))
        print('   king eats spawn    ', f('k%d_s'))
        print('   king eats corpse   ', f('k%d_c'))
        print('   feeder deaths      ', f('feedn%d'))
        print('   feeder pearls      ', f('feedpearls%d'))
        print('    -> eaten by king  ', f('fate%d_king'))
        print('    -> other ally     ', f('fate%d_other'))
