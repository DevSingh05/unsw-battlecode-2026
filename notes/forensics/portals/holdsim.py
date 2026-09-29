#!/usr/bin/env python3
"""For every forced tube-end split of an L>=8 dragon after a dirty probe (echoscan2.pkl, no free alternative):
would holding 1 or 2 turns (SPLIT 2 and re-probe) have found the exit free? Reads the replay's real occupancy of
the exit tile x and of x's onward neighbours at our turn slot 0..3 rounds after the decision.
(The held dragon itself would not be at the tail tiles it vacates by splitting 2; ignored.)
   python3 notes/forensics/portals/holdsim.py"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map
EV = [c for c in pickle.load(open(os.path.join(HERE, 'echoscan2.pkl'), 'rb')) if c['what'] == 'split' and c['free_alts'] == 0 and c['L'] >= 8]
by = collections.defaultdict(list)
for c in EV: by[c['game']].append(c)
res = collections.Counter(); per = []
for gid, cs in by.items():
    o = R.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = Map(o['map'])
    want = {}  # (round, id) -> list of (c, k)
    for c in cs:
        for k in range(4): want.setdefault((c['round'] + k, c['id']), []).append((c, k))
    body = {}; alive = set(); started = False
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); alive.add(i)
    rnd = 0; done = set()
    def evaluate(r, slot_id):
        for (rr, i), lst in want.items():
            if rr != r or (rr, i) in done or i > slot_id: continue
            done.add((rr, i))
            occ = {}
            for j in alive:
                for q, s in enumerate(body[j]): occ[s] = j
            for c, k in lst:
                xfree = c['exit'] not in occ
                onward = sum(1 for t in c['xn'] if t not in occ)
                c.setdefault('later', {})[k] = (xfree, onward)
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            if started: evaluate(rnd, 10 ** 9)
            rnd = e['round']; started = True
        elif t == 'dragonAction':
            evaluate(rnd, e['id'] - 1)
        elif t == 'dragonUpdate':
            if not started: continue
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); alive.add(e['child'])
        elif t == 'dragonDeath': alive.discard(e['id'])
    evaluate(rnd, 10 ** 9)
for c in EV:
    L = c.get('later', {})
    ok = lambda k: k in L and L[k][0] and L[k][1] > 0
    first = next((k for k in range(4) if ok(k)), None)
    res['clear_at_hold%s' % first if first is not None else 'still_blocked_after_3'] += 1
    per.append((c['game'], c['round'], c['id'], c['L'], first))
n = len(EV)
for k, v in sorted(res.items()): print('%-26s %4d  %.0f%%' % (k, v, 100 * v / n))
print('events', n, 'games', len(by))
pickle.dump(per, open(os.path.join(HERE, 'holdsim.pkl'), 'wb'))
