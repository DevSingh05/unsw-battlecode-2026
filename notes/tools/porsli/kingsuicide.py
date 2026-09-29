#!/usr/bin/env python3
"""Deliberate backward moves (feed suicide = MOVE opposite to facing, into the own neck) by dragons that were
AT LEAST as long as every other ally: the team's longest kills itself.  All maps, replays/v28 (+old with 'all').
    python3 notes/tools/porsli/kingsuicide.py [v28|all]"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
dirs = ['v28'] + (['v19plus', 'v16'] if len(sys.argv) > 1 and sys.argv[1] == 'all' else [])
C = collections.Counter(); n = collections.Counter()
for d in dirs:
    for g in json.load(open(os.path.join(ROOT, 'replays', d, 'ledger.json'))):
        p = os.path.join(ROOT, 'replays', d, '%d.replay' % g['game'])
        if not os.path.exists(p):
            continue
        S = simulate(p); m = S['map']; rs = dict(S['rounds']); T = g['side']
        n[g['map']] += 1
        for dd in S['deaths']:
            if dd['team'] != T or dd['len'] < 10 or dd['actor'] != dd['id'] or dd['reason'] != 'HitSelf':
                continue
            mv = dd.get('move') or ''
            if len(mv) != 1 or len(dd['body']) < 2 or m.step(dd['head'], mv) != dd['body'][1]:
                continue
            prev = rs.get(dd['round'] - 1, rs.get(dd['round']))[T]
            others = [L for i, L in prev['ids'].items() if i != dd['id']]
            born_now = dd['id'] not in prev['ids']
            mx_other = max(others) if others else 0
            longest = dd['len'] >= mx_other - (2 if born_now else 0)
            tag = 'LONGEST' if longest else 'shorter'
            C[(g['map'], tag)] += 1
            if longest:
                fin = S['rounds'][-1][1]
                o = 'B' if T == 'A' else 'A'
                print('%s %d %s %s r%d L%d age %d  (other allies max %d%s)  final us %d them %d' % (
                    g['map'][:10], g['game'], 'W' if g['win'] else 'L', 'rk' if g['ranked'] else 'un', dd['round'], dd['len'], dd['age'],
                    mx_other, ', parent of this child' if born_now else '', fin[T]['max'], fin[o]['max']))
print({k: v for k, v in sorted(C.items())})
print('games per map', dict(n))
