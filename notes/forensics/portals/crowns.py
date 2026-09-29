#!/usr/bin/env python3
"""Per game: how many times a declared king (hop-0 king broadcaster) split (crown dropped) before our longest
reached 12, and the round it reached 12. Correlates crown drops with late kings.
   python3 notes/forensics/portals/crowns.py"""
import json, os, sys, collections, pickle
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}
T_ = {r['game']: r for r in pickle.load(open(os.path.join(HERE, 'timing.pkl'), 'rb'))}
games = sorted(g for g, x in led.items() if x['map'] == 'Portals' and g != 607994)
rows = []
for gid in games:
    g = led[gid]; T = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    kr = collections.defaultdict(set)
    for s in S['sonars']:
        if s['team'] != T: continue
        x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
        if hop == 0 and kid == (s['id'] & 1023) and L >= 2: kr[s['id']].add(s['round'])
    r12 = T_[gid]['us'][1]
    drops = [s for s in S['splits'] if s['team'] == T and s['round'] < r12 and any(s['round'] - 3 <= r <= s['round'] for r in kr.get(s['parent'], ()))]
    kdeaths = [d for d in S['deaths'] if d['team'] == T and d['round'] < r12 and d['id'] in kr and max(kr[d['id']]) >= d['round'] - 3]
    nk = len([i for i, rs in kr.items() if min(rs) < r12])
    rows.append((gid, g['win'], r12, len(drops), len(kdeaths), nk, T_[gid]['fin']))
for w in (False, True):
    rs = [r for r in rows if r[1] == w]
    print('==', 'WINS' if w else 'LOSSES', len(rs), ' (game, reach L12, crown drops by split, king deaths, #kings declared before L12, final)')
    for r in sorted(rs, key=lambda r: r[2]): print('  %d r%-4d splits %2d deaths %2d kings %2d  final %s' % (r[0], r[2], r[3], r[4], r[5], r[6]))
    import statistics as st
    print('  mean crown drops by split %.1f, king deaths %.1f, kings declared %.1f' % (st.mean(r[3] for r in rs), st.mean(r[4] for r in rs), st.mean(r[5] for r in rs)))
late = [r for r in rows if r[2] >= 410]; early = [r for r in rows if r[2] < 410]
print('reach L12 >= r410: %d games, %d losses; crown drops mean %.1f' % (len(late), sum(1 for r in late if not r[1]), sum(r[3] for r in late) / max(1, len(late))))
print('reach L12 <  r410: %d games, %d losses; crown drops mean %.1f' % (len(early), sum(1 for r in early if not r[1]), sum(r[3] for r in early) / max(1, len(early))))
