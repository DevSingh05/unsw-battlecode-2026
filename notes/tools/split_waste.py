#!/usr/bin/env python3
"""How many split children (and parents) die right after the split, and why.

Also classifies every HitSelf death by number of free neighbours (trapped vs not).
    python3 notes/tools/split_waste.py
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')

def run(gid, us):
    g = simulate(os.path.join(DIR, f'{gid}.replay'))
    death = {d['id']: d for d in g['deaths']}
    res = {'us': collections.Counter(), 'them': collections.Counter()}
    for s in g['splits']:
        k = 'us' if s['team'] == us else 'them'
        c = s['child']; p = s['parent']
        res[k]['splits'] += 1
        dc = death.get(c)
        if dc and dc['round'] - s['round'] <= 3:
            res[k]['child_dead_3'] += 1
            res[k]['child_dead_3_' + dc['reason']] += 1
            if dc['round'] == s['round']: res[k]['child_dead_0'] += 1
        if dc and dc['round'] - s['round'] <= 20: res[k]['child_dead_20'] += 1
        dp = death.get(p)
        if dp and 0 <= dp['round'] - s['round'] <= 3: res[k]['parent_dead_3'] += 1
        if s['exits'] == 0: res[k]['split_parent_no_exit'] += 1
    for d in g['deaths']:
        k = 'us' if d['team'] == us else 'them'
        nfree = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        key = 'trapped' if nfree == 0 else 'hadfree'
        res[k][f'death_{key}'] += 1
        if d['reason'] == 'HitSelf' and d['round'] < 330:
            res[k][f'hitself_{key}'] += 1
            if nfree and d['age'] == 0: res[k]['hitself_hadfree_age0'] += 1
        if d['reason'] == 'HitOtherBody':
            res[k][f'body_{key}'] += 1
    return res

if __name__ == '__main__':
    summ = json.load(open(os.path.join(DIR, 'summary.json')))
    groups = collections.defaultdict(lambda: {'us': collections.Counter(), 'them': collections.Counter(), 'n': 0})
    per = {}
    for s in summ:
        key = 'W' if s['win'] else ('L-elim' if s['end'] == 'teamEliminated' else 'L-round')
        r = run(s['id'], s['side'])
        per[s['id']] = r
        groups[key]['n'] += 1
        for k in ('us', 'them'): groups[key][k] += r[k]
    for key, G in groups.items():
        print(f'== {key} ({G["n"]} games), per game:')
        for k in ('us', 'them'):
            print('  ', k, {a: round(b / G['n'], 1) for a, b in sorted(G[k].items())})
    print('\nper game child_dead_3 / splits (us | them):')
    for s in summ:
        r = per[s['id']]
        print(f"  {s['id']} {s['map'][:16]:16s} {'W' if s['win'] else 'L'} us {r['us']['child_dead_3']:3d}/{r['us']['splits']:3d}  them {r['them']['child_dead_3']:3d}/{r['them']['splits']:3d}  hitself_trapped us {r['us']['hitself_trapped']:3d} them {r['them']['hitself_trapped']:3d}")
