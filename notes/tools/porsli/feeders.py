#!/usr/bin/env python3
"""What do would-be feeders do?  For our dragons that satisfy the v28 shouldFeed() conditions as far as the
replay shows them (received a king/relay message <=12 rounds old with len >= myLen+2, myLen within the KING_V2
feed cap for that round, units > reserve, round >= feedStart), per window: dragon-rounds eligible, share of
those turns spent splitting, moving closer to / farther from the king's real head (walls+portals BFS distance, bodies ignored), and how
eligible dragons end (feed death near king / other death / alive at the end).
    python3 notes/tools/porsli/feeders.py Portals|Slithery [v28|old|all]"""
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
FS, RES = (300, 3) if mp == 'Portals' else (250, 4)
cap = lambda r: 1000 if r >= 420 else (6 if r >= 380 else 3)
W = [(FS, 380), (380, 420), (420, 450), (450, 500)]
A = {k: collections.Counter() for k in 'LW'}; n = collections.Counter()


def mapbfs(m, src):
    # walls + portals, bodies ignored (reverse steps: the map is symmetric enough; use forward steps from src)
    dist = {src: 0}; q = [src]
    for u in q:
        for dd in 'NESW':
            v = m.step(u, dd)
            if v is not None and v not in dist:
                dist[v] = dist[u] + 1; q.append(v)
    return dist
for g in gs:
    S = simulate(path_of(g['game'])); T = g['side']; m = S['map']; grp = 'W' if g['win'] else 'L'; n[grp] += 1
    C = A[grp]
    msg = collections.defaultdict(list)  # receiver -> [(round, kinglen, kingid)]
    for s in S['sonars']:
        if s['team'] != T or s['hitKind'] not in ('ally', 'allyHead') or s['hitId'] is None: continue
        x = s['value'] & ((1 << 43) - 1)
        L = (x >> 12) & 255; rnd = (x >> 34) & 511; kid = (x >> 20) & 1023
        if L >= 3 and (s['round'] - rnd) % 512 <= 4:
            msg[s['hitId']].append((s['round'], L, kid))
    rs = dict(S['rounds'])
    act = {(mv['round'], mv['id']): mv for mv in S['moves']}
    spl = {(s['round'], s['parent']) for s in S['splits']}
    death = {d['id']: d for d in S['deaths']}
    elig_ids = {}
    bcache = {}
    for rn, sn in S['rounds']:
        if rn < FS or rn >= 499: continue
        wi = next(i for i, (a, b) in enumerate(W) if a <= rn < b)
        prev = rs.get(rn - 1, sn)[T]
        units = prev['n']
        kingreal = prev['king']
        for i, L in prev['ids'].items():
            if i == kingreal: continue
            ms = [x for x in msg.get(i, ()) if rn - 12 <= x[0] < rn]
            if not ms: continue
            kl = max(x[1] for x in ms)
            if not (kl >= L + 2 and L <= cap(rn) and units > RES): continue
            C[(wi, 'elig')] += 1
            elig_ids.setdefault(i, rn)
            if (rn, i) in spl:
                C[(wi, 'split')] += 1; continue
            mv = act.get((rn, i))
            if not mv or not mv.get('head_after') or kingreal not in S['body']: continue
            kh = sn[T]['ids'] and None
            # distance to the real king head before/after (plain torus distance; portals ignored)
            khead = rs.get(rn - 1, sn)['heads'].get(kingreal)
            if not khead: continue
            if (rn, kingreal) not in bcache:
                bcache[(rn, kingreal)] = mapbfs(m, khead[0])
            bd = bcache[(rn, kingreal)]
            d0 = bd.get(mv['head'], 99); d1 = bd.get(mv['head_after'], 99)
            C[(wi, 'closer' if d1 < d0 else 'farther' if d1 > d0 else 'same')] += 1
            C[(wi, 'd0sum')] += d0; C[(wi, 'dn')] += 1
    for i, r0 in elig_ids.items():
        d = death.get(i)
        if d is None: C['end_alive'] += 1
        elif d.get('king') and d['king'][2] <= 4 and d['actor'] == i: C['end_feed'] += 1
        elif d['reason'] == 'HitWall' or (d.get('nbrs') and not [k for k, v in d['nbrs'].items() if v in ('free', 'pearl')]): C['end_trapped'] += 1
        else: C['end_other_death'] += 1
for grp in 'LW':
    if not n[grp]: continue
    C = A[grp]
    print('== %s %s %s (%d games), per game' % (mp, ver, grp, n[grp]))
    for wi, (a, b) in enumerate(W):
        e = max(1, C[(wi, 'elig')])
        print('  r%d-%d eligible dragon-rounds %.0f | split %.0f%% | closer %.0f%% farther %.0f%% same %.0f%% | mean dist to king %.1f' % (
            a, b, C[(wi, 'elig')] / n[grp], 100 * C[(wi, 'split')] / e, 100 * C[(wi, 'closer')] / e, 100 * C[(wi, 'farther')] / e,
            100 * C[(wi, 'same')] / e, C[(wi, 'd0sum')] / max(1, C[(wi, 'dn')])))
    tot = sum(C[k] for k in ('end_alive', 'end_feed', 'end_trapped', 'end_other_death'))
    print('  eligible dragons %.1f/g end: fed near king %.0f%%, trapped/pocket %.0f%%, other death %.0f%%, alive at end %.0f%%' % (
        tot / n[grp], 100 * C['end_feed'] / tot, 100 * C['end_trapped'] / tot, 100 * C['end_other_death'] / tot, 100 * C['end_alive'] / tot))
