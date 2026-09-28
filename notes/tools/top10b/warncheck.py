"""For our fatal portal crossings into an ally body (Default/Schooltime/Trophy): did the blocking ally's PORTAL_WARN sonar
reach the crosser in the previous 3 rounds? Uses sonar hitId from the replay. Usage: python3 warncheck.py"""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import analyze as A, crossing as C, sim2
G = [x for x in A.games() if x['grp'] == 'us' and x['map'] in ('Default', 'Schooltime', 'Trophy')]
res = collections.Counter()
for x in G:
    recs, _ = C.work((x['path'], {x['T']: {k: x[k] for k in ('gid', 'map', 'grp', 'name')}}))
    g = sim2.simulate(x['path'])
    son = collections.defaultdict(list)
    for s in g['sonars']:
        if s['hitId'] is not None: son[s['hitId']].append(s)
    for r in recs:
        if not r['died'] or r['exit_occ'] != 'ally': continue
        seg, j = r['occ_info'][0], r['occ_info'][1]
        got = [s for s in son.get(r['id'], []) if s['id'] == j and r['round'] - 3 <= s['round'] <= r['round']]
        got_same = [s for s in got if s['round'] == r['round']]
        res[(x['map'], 'seg%d' % min(seg, 3), 'warned_by_blocker' if got else 'no_msg', 'same_round' if got_same else '')] += 1
for k, v in sorted(res.items()): print(k, v)
