#!/usr/bin/env python3
"""How many of our dragons broadcast as king (hop-0 king messages whose id == sender), per 50-round window,
and how long they are relative to the real longest.   python3 notes/tools/porsli/kings_n.py Portals|Slithery [v28|old|all]"""
import collections, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, HERE)
from sim2 import simulate
from board import path_of
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
W = [(250, 300), (300, 350), (350, 400), (400, 450), (450, 500)]
A = {k: collections.Counter() for k in 'LW'}; n = collections.Counter()
for g in gs:
    S = simulate(path_of(g['game'])); T = g['side']; grp = 'W' if g['win'] else 'L'; n[grp] += 1
    rs = dict(S['rounds'])
    per = collections.defaultdict(dict)  # window -> sender -> max len
    recv = collections.defaultdict(lambda: collections.Counter())  # window -> kind of king heard (real/fake) by receivers
    for s in S['sonars']:
        if s['team'] != T or s['round'] < 250: continue
        x = s['value'] & ((1 << 43) - 1)
        L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023; rnd = (x >> 34) & 511
        if L < 2 or (s['round'] - rnd) % 512 > 4: continue
        wi = min((s['round'] - 250) // 50, 4)
        if hop == 0 and kid == (s['id'] & 1023):
            per[wi][s['id']] = max(per[wi].get(s['id'], 0), L)
        if s['hitKind'] in ('ally', 'allyHead') and s['hitId'] is not None:
            mx = rs.get(s['round'] - 1, rs.get(s['round']))[T]['max']
            recv[wi]['real' if L >= mx - 2 else 'short(<max-2)'] += 1
    for wi in range(5):
        C = A[grp]
        ks = per[wi]
        C[(wi, 'n')] += len(ks)
        mx = rs.get(W[wi][1] - 1, rs.get(S['last_round']))[T]['max']
        C[(wi, 'small')] += sum(1 for L in ks.values() if L <= 5)
        C[(wi, 'recv_real')] += recv[wi]['real']; C[(wi, 'recv_short')] += recv[wi]['short(<max-2)']
for grp in 'LW':
    if not n[grp]: continue
    C = A[grp]
    print('== %s %s %s (%d games): distinct king broadcasters per window (of them L<=5) | king msgs received: share naming a dragon >= longest-2' % (mp, ver, grp, n[grp]))
    print('   ' + '  '.join('r%d-%d: %.1f (%.1f) | %.0f%%' % (a, b, C[(i, 'n')] / n[grp], C[(i, 'small')] / n[grp],
          100 * C[(i, 'recv_real')] / max(1, C[(i, 'recv_real')] + C[(i, 'recv_short')])) for i, (a, b) in enumerate(W)))
