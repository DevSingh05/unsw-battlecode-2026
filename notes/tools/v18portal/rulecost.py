#!/usr/bin/env python3
"""Cost/benefit of the echo rule (PORTAL_ECHO_GUARD) on our single-step crossings: what the blocked crossings
were (fatal / safe, pearl on the exit, safe alternatives available), per game, for v18 and v16.
usage (from project root): python3 notes/tools/v18portal/rulecost.py ab_v18_Default ab_v16_dt_Default
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent


def fatal(r):
    return r['died'] is not None and r['died_step'] == r['k']


for name in sys.argv[1:] or ['ab_v18_Default']:
    G = pickle.load(open(HERE / f'{name}.pkl', 'rb')); NG = len(G)
    for mode in ('heads', 'any'):
        c = collections.Counter()
        for g in G:
            for r in g['recs']:
                if not r['us']:
                    continue
                ps = [p for p in g['pings'].get(r['id'], []) if p['round'] == r['round'] - 1]
                kinds = ('allyHead', 'enemyHead') if mode == 'heads' else ('ally', 'allyHead', 'enemy', 'enemyHead')
                blocked = len(r['move']) == 1 and r['age'] > 0 and any(p['hitKind'] in kinds for p in ps)
                safe_alt = sum(1 for d, a in r['alts'].items() if d != r['dir'] and a['st'] == 'free')
                if blocked:
                    c['blocked'] += 1
                    if fatal(r):
                        c['blocked_fatal'] += 1
                        c['blocked_fatal_noalt'] += safe_alt == 0
                        c['blocked_fatal_hit_' + (r['hit'][2] == r['team'] and 'ally' or 'enemy') if r['hit'] and r['hit'][0] != 'self' else 'blocked_fatal_self'] += 1
                    else:
                        c['blocked_safe'] += 1
                        c['blocked_safe_pearl_on_exit'] += r['exit_pearl']
                else:
                    c['kept_fatal'] += fatal(r)
                c['cross'] += 1; c['fatal'] += fatal(r)
        print(f'{name} [{mode}] per game: ' + ', '.join(f'{k} {v / NG:.1f}' for k, v in sorted(c.items())))
