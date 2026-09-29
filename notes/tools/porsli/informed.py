#!/usr/bin/env python3
"""Does the king broadcast reach our swarm? Decodes OUR king/relay sonar values (bit layout of
encodeKing; checksum not verified, plausibility only: hop<=3, round field == round, len>=3) and marks
a dragon 'informed' in round r if it received such a message in rounds r-12..r (bot: kingId expires
after 12 silent rounds). Reports, per window, the share of our dragons alive that are informed.
    python3 notes/tools/porsli/informed.py Portals|Slithery [v28|old|all]"""
import collections, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.dirname(__file__))
from sim2 import simulate
from board import path_of
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
W = [(300, 350), (350, 400), (400, 450), (450, 500)]
agg = {k: collections.Counter() for k in 'LW'}
for g in gs:
    S = simulate(path_of(g['game'])); T = g['side']
    got = collections.defaultdict(list)
    for s in S['sonars']:
        if s['team'] != T or s['hitKind'] not in ('ally', 'allyHead') or s['hitId'] is None:
            continue
        v = s['value']; x = v & ((1 << 43) - 1)
        L = (x >> 12) & 255; hop = (x >> 30) & 3; rnd = (x >> 34) & 511
        if L < 3 or (s['round'] - rnd) % 512 > 4:
            continue
        got[s['hitId']].append(s['round'])
    A = agg['W' if g['win'] else 'L']
    for rn, sn in S['rounds']:
        if rn < 300: continue
        wi = min((rn - 300) // 50, 3)
        k = sn[T]['king']
        for i, L in sn[T]['ids'].items():
            if i == k: continue
            inf = any(rn - 12 <= r <= rn for r in got.get(i, ()))
            sz = 'small' if L <= 6 else 'mid'
            A[(wi, sz, 'n')] += 1; A[(wi, sz, 'inf')] += inf
for grp in 'LW':
    A = agg[grp]
    if not A: continue
    print('%s %s %s: share of non-king dragon-rounds informed of a king (<=12 rounds old)' % (mp, ver, grp))
    for sz in ('small', 'mid'):
        print('   %-5s ' % sz + '  '.join('r%d-%d %.2f (%.1f units)' % (a, b, A[(i, sz, 'inf')] / max(1, A[(i, sz, 'n')]), A[(i, sz, 'n')] / 50 / sum(1 for g in gs if (g['win'] == (grp == 'W')))) for i, (a, b) in enumerate(W)))
