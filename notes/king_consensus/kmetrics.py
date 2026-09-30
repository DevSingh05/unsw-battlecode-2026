#!/usr/bin/env python3
"""King metrics per team from local replays (both sides of each game).
  - kings/50r: distinct self-crowned king broadcasters (hop-0 king sonar whose id == sender) per 50-round window r250-500
  - feeds->real: share of feed-like deaths (self-chosen death with a free alternative, r>=300, a longer ally head
    within 5 steps) whose longest nearby longer ally is the team's real longest (>= max-2)
  - longest r499
usage (project root): python3 notes/king_consensus/kmetrics.py REPLAY... ; team name is taken from the file name
  MAP_SEED_A_vs_B.replay (A = team A)."""
import collections, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/porsli'))
from sim2 import simulate
from collect import classify

agg = collections.defaultdict(lambda: collections.Counter())
for p in sys.argv[1:]:
    S = simulate(p)
    base = os.path.basename(p)[:-7]
    a, b = base.split('_vs_')
    na = a.split('_')[-1]
    names = {'A': na, 'B': b}
    rs = dict(S['rounds']); last = S['last_round']
    line = [base]
    for T in 'AB':
        C = agg[names[T]]; C['games'] += 1
        per = collections.defaultdict(set)
        for s in S['sonars']:
            if s['team'] != T or s['round'] < 250: continue
            x = s['value'] & ((1 << 43) - 1)
            L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023; rnd = (x >> 34) & 511
            if L < 2 or (s['round'] - rnd) % 512 > 4: continue
            if hop == 0 and kid == (s['id'] & 1023):
                per[min((s['round'] - 250) // 50, 4)].add(s['id'])
        nk = sum(len(per[i]) for i in range(5)) / 5
        C['kings'] += nk
        feeds = real = 0
        for d in S['deaths']:
            if d['team'] != T or d['round'] < 300 or d['actor'] != d['id']: continue
            c = classify({'map': S['map']}, d, feed_king_dist=5)
            if not (c.startswith('feed_') or c.startswith('chose_')): continue
            kg = d.get('king')
            if not kg or kg[1] <= d['len']: continue
            if c.startswith('chose_'):
                continue
            feeds += 1
            mx = rs.get(d['round'] - 1, rs.get(d['round']))[T]['max']
            if kg[1] >= mx - 2: real += 1
        # lesser-king feeds: a feed-like death next to a longer ally that is NOT the longest
        lesser = 0
        for d in S['deaths']:
            if d['team'] != T or d['round'] < 300 or d['actor'] != d['id'] or not d.get('ally_near'): continue
            c = classify({'map': S['map']}, d, feed_king_dist=5)
            if not c.startswith('chose_'): continue
            nj, nl, nd = d['ally_near']
            mx = rs.get(d['round'] - 1, rs.get(d['round']))[T]['max']
            if nl > d['len'] and nd <= 3 and nl < mx - 2: lesser += 1
        C['feeds'] += feeds; C['real'] += real; C['lesser'] += lesser
        lg = rs[min(499, last)][T]['max']
        C['long499'] += lg
        line.append('%s kings/50r %.1f feeds %d real %d lesserNear %d long499 %d' % (names[T], nk, feeds, real, lesser, lg))
    print(' | '.join(line), flush=True)
print('== per bot (means over games) ==')
for k, C in agg.items():
    g = C['games']
    print('%-28s games %d kings/50r %.1f feeds/g %.1f real-share %.0f%% lesserNear/g %.1f long499 %.1f' % (
        k, g, C['kings'] / g, C['feeds'] / g, 100 * C['real'] / max(1, C['feeds'] + C['lesser']), C['lesser'] / g, C['long499'] / g))
