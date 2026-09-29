#!/usr/bin/env python3
"""PORTAL_ECHO_GUARD false blocks: our dragon on a portal-exit tile probes through the portal (warn ray), the ray
hits a HEAD k>=2 tiles past the exit (exit itself free), next turn the guard marks the exit occupied.
What does the dragon do next turn, and what does it cost?
   python3 notes/forensics/portals/echoscan.py [GAME...]   (default: all Portals games in replays/auto/games)"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
games = [int(a) for a in sys.argv[1:]] or sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
TOT = collections.Counter(); LEN = collections.Counter(); rows = []
for gid in games:
    g = led[gid]; T = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid)); m = S['map']
    act = {(a['round'], a['id']): a for a in S['moves']}
    spl = {(s['round'], s['parent']): s for s in S['splits']}
    dd = {d['id']: d for d in S['deaths']}
    # rays per (round, sender)
    rays = collections.defaultdict(list)
    for s in S['sonars']:
        if s['team'] == T: rays[(s['round'], s['id'])].append(s)
    for (r, i), rs in rays.items():
        for s in rs:
            if s['hitKind'] not in ('allyHead', 'enemyHead'): continue
            o = s['origin']; d = s['dir']
            x = m.step(o, d)
            if x is None or x == m.wrap(o[0] + {'N': 0, 'E': 1, 'S': 0, 'W': -1}[d], o[1] + {'N': -1, 'E': 0, 'S': 1, 'W': 0}[d]):
                continue  # not a portal crossing
            # distance along the ray to the hit
            k = 1; y = x
            while y != s['end'] and k < 80:
                y = m.step(y, d); k += 1
                if y is None: break
            nxt = act.get((r + 1, i)); sp = spl.get((r + 1, i))
            if nxt is None and sp is None: continue
            if nxt is not None and nxt['head'] != o: continue  # moved elsewhere (sprint) before
            L = (nxt or {}).get('len_before') or sp['L']
            if sp: what = 'split%d' % sp['k']
            elif 'move' in nxt['act']: what = 'cross' if nxt['act']['move'][0] == d else 'other'
            else: what = 'suicide'
            died = dd.get(i); dsoon = died and died['round'] <= r + 3
            key = ('exit_occupied' if k == 1 else 'head_%d_past' % min(k - 1, 4))
            TOT[(key, what)] += 1
            if L >= 6: LEN[(key, what, 'L>=6')] += 1
            if k >= 2 and what != 'cross' and L >= 4:
                rows.append((gid, r + 1, i, L, d, o, x, s['end'], s['hitKind'], s['hitId'], k - 1, what, 'died r%d L%d %s' % (died['round'], died['len'], died['reason']) if dsoon else ''))
for k, v in sorted(TOT.items()): print(k, v)
print('--- L>=6'); [print(k, v) for k, v in sorted(LEN.items())]
print('--- non-crossing with free exit, L>=4')
for r in rows: print(r)
