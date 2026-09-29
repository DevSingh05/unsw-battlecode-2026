#!/usr/bin/env python3
"""Where do our declared kings drop the crown (split while broadcasting as king)? tile class of the parent head:
tube tile / sock / pocket / main; and trapped (0 free neighbours) or not. Also the kings' length at the drop.
   python3 notes/forensics/portals/crownwhere.py"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map
REF = Map(open(os.path.join(ROOT, 'notes/maps/Portals__id20.map')).read())
SOCK = {(15, y) for y in range(8)} | {(16, 7)} | {(16, y) for y in range(8, 16)} | {(15, 8)}
def cls(t):
    if t in SOCK: return 'sock'
    g = REF.tiles.get(t, (0, 0))
    if g[1] > 0 and g != (1, 1):
        # pocket = pearl tile with a single passable neighbour
        nb = sum(1 for d in 'NESW' if REF.step(t, d) is not None)
        return 'pocket' if nb <= 1 else 'tube'
    return 'main'
if __name__ == '__main__':
    GD = os.path.join(ROOT, 'replays/auto/games')
    led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
    games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
    C = collections.Counter(); LEN = collections.Counter(); n = 0
    for gid in games:
        g = led[gid]; T = g['side']; n += 1
        S = simulate(os.path.join(GD, '%d.replay' % gid))
        kr = collections.defaultdict(set)
        for s in S['sonars']:
            if s['team'] != T: continue
            x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
            if hop == 0 and kid == (s['id'] & 1023) and L >= 2: kr[s['id']].add(s['round'])
        # parent head at split time = parentBody[0]; sim2 splits don't keep it, so re-read from moves: last head_after
        lasthead = {}
        for a in S['moves']:
            if a.get('head_after'): lasthead[(a['id'], a['round'])] = a['head_after']
        heads = collections.defaultdict(dict)
        for (i, r), h in lasthead.items(): heads[i][r] = h
        for s in S['splits']:
            if s['team'] != T or not any(s['round'] - 3 <= r <= s['round'] for r in kr.get(s['parent'], ())): continue
            hs = heads[s['parent']]; prev = [r for r in hs if r < s['round']]
            if not prev: continue
            h = hs[max(prev)]
            c = cls(h); tr = 'trapped' if s['exits'] == 0 else 'open'
            kind = 'reverse' if s['k'] >= s['L'] - 3 else 'small'
            C[(c, tr, kind)] += 1; LEN[(c, tr, kind)] += s['L']
    tot = sum(C.values())
    for k, v in sorted(C.items(), key=lambda kv: -kv[1]): print('%-32s %4d  %.2f/game  %4.1f%%  mean L %.1f' % (k, v, v / n, 100 * v / tot, LEN[k] / v))
