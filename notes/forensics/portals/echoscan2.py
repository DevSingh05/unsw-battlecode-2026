#!/usr/bin/env python3
"""echoscan v2: for every probe ray of ours that crossed a portal and hit a HEAD, check the real state of the exit tile
at the moment the prober acts next round (the replay truth), and what the prober did.
   python3 notes/forensics/portals/echoscan2.py [--minlen N] [GAME...]  -> echoscan2.pkl + summary"""
import json, os, sys, collections, pickle
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import replay_decode as R
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
args = [a for a in sys.argv[1:] if not a.startswith('--')]
games = [int(a) for a in args] or sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def occupancy_at(path, m, queries):
    """queries: {(round, id): [tiles]} -> {(round,id): {tile: (occupant id, seg idx) or None}} evaluated just before id acts."""
    o = R.load(path); body = {}; alive = set(); started = False
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); alive.add(i)
    rnd = 0; res = {}
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']; started = True
        elif t == 'dragonAction':
            q = queries.get((rnd, e['id']))
            if q is not None:
                occ = {}
                for j in alive:
                    for k, s in enumerate(body[j]): occ[s] = (j, k)
                res[(rnd, e['id'])] = {tile: occ.get(tile) for tile in q}
        elif t == 'dragonUpdate':
            if not started: continue
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); alive.add(e['child'])
        elif t == 'dragonDeath': alive.discard(e['id'])
    return res


EV = []
for gid in games:
    g = led[gid]; T = g['side']; path = os.path.join(GD, '%d.replay' % gid)
    S = simulate(path); m = S['map']
    act = {(a['round'], a['id']): a for a in S['moves']}
    spl = {(s['round'], s['parent']): s for s in S['splits']}
    dd = {d['id']: d for d in S['deaths']}
    cands = []
    for s in S['sonars']:
        if s['team'] != T or s['hitKind'] not in ('allyHead', 'enemyHead', 'ally', 'enemy'): continue
        o_ = s['origin']; d = s['dir']; x = m.step(o_, d)
        if x is None or x == m.wrap(o_[0] + DV[d][0], o_[1] + DV[d][1]): continue
        k = 1; y = x
        while y != s['end'] and k < 99:
            y = m.step(y, d); k += 1
            if y is None: break
        r, i = s['round'], s['id']
        nxt = act.get((r + 1, i)); sp = spl.get((r + 1, i))
        if nxt is None and sp is None: continue
        if nxt is not None and nxt['head'] != o_: continue
        # alternatives = the other 3 neighbours of the prober's head
        alts = [m.step(o_, dd_) for dd_ in 'NESW' if dd_ != d]
        back = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[d]
        xn = [m.step(x, dd_) for dd_ in 'NESW' if dd_ != back]
        xn = [t for t in xn if t is not None]
        cands.append(dict(game=gid, round=r + 1, id=i, dir=d, head=o_, exit=x, hit_end=s['end'], hitKind=s['hitKind'], hitId=s['hitId'], past=k - 1,
                          L=(nxt or {}).get('len_before') or sp['L'], nxt=nxt, sp=sp, alts=[a for a in alts if a is not None],
                          death=dd.get(i), opp=g['opp'], win=g['win'], xn=xn))
    q = collections.defaultdict(list)
    for c in cands: q[(c['round'], c['id'])] += [c['exit']] + c['alts'] + c['xn']
    occ = occupancy_at(path, m, q)
    for c in cands:
        oc = occ.get((c['round'], c['id']), {})
        c['exit_occ'] = oc.get(c['exit'])
        c['free_alts'] = sum(1 for a in c['alts'] if oc.get(a) is None)
        c['x_onward_free'] = sum(1 for a in c['xn'] if oc.get(a) is None)
        if c['sp']: c['what'] = 'split'
        elif 'move' in c['nxt']['act']: c['what'] = 'cross' if c['nxt']['act']['move'][0] == c['dir'] else 'other'
        else: c['what'] = 'suicide'
        EV.append(c)
    print(gid, len(cands), file=sys.stderr)
pickle.dump(EV, open(os.path.join(os.path.dirname(__file__), 'echoscan2.pkl'), 'wb'))
C = collections.Counter()
for c in EV:
    ex = 'exit_free' if c['exit_occ'] is None else 'exit_taken'
    C[(ex, c['what'], 'noalt' if c['free_alts'] == 0 else 'alt', 'L>=6' if c['L'] >= 6 else 'L<6')] += 1
for k, v in sorted(C.items()): print(k, v)
