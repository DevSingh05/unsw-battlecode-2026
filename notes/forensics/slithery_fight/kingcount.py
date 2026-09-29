#!/usr/bin/env python3
"""How many king candidates we run: at r350/400/450/490, count our dragons with L>=10, how many of them broadcast
a hop-0 king message with their own id in the previous 10 rounds (= kingSelf or iAmKing), and the mass held
in non-longest L>=10 dragons; same count of L>=10 for the opponent.  Also: for each of our L>=10 non-longest
dragons at r450, did it hear (a king msg ray hit it) the real longest in r440-450?
    python3 notes/forensics/slithery_fight/kingcount.py [GAME...]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as RD
from sim2 import Map
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
gids = [int(a) for a in sys.argv[1:]] or sorted(g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and (g['opp'] in top or g['opp'] == '3.14159265'))
CK = (350, 400, 450, 490)
agg = {'L': collections.Counter(), 'W': collections.Counter()}; ng = collections.Counter()
for gid in gids:
    g = led[gid]; us = g['side']; grp = 'W' if g['win'] else 'L'; ng[grp] += 1
    o = RD.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = Map(o['map'])
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    rnd = 0; lastk = {}; heard = collections.defaultdict(list)
    out = []
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            rnd = e['round']
            if rnd in CK:
                ours = sorted([j for j in alive if team[j] == us and len(body[j]) >= 10], key=lambda j: -len(body[j]))
                th = [j for j in alive if team[j] != us and len(body[j]) >= 10]
                kb = [j for j in ours if rnd - lastk.get(j, -99) <= 10]
                real = ours[0] if ours else None
                other = sum(len(body[j]) for j in ours[1:])
                hr = sum(1 for j in ours[1:] if any(r >= rnd - 10 and kid == (real & 1023) for r, kid in heard[j]))
                out.append('r%d us L>=10: %d (broadcast %d) lens %s | heard real king in last 10r: %d/%d | them L>=10: %d %s' % (
                    rnd, len(ours), len(kb), [len(body[j]) for j in ours], hr, max(0, len(ours) - 1), len(th), sorted([len(body[j]) for j in th], reverse=True)))
                a = agg[grp]; a[(rnd, 'n')] += len(ours); a[(rnd, 'kb')] += len(kb); a[(rnd, 'them')] += len(th); a[(rnd, 'hr')] += hr; a[(rnd, 'oth')] += max(0, len(ours) - 1)
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            p, c = e['parent'], e['child']; body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t == 'dragonDeath': alive.discard(e['id'])
        elif t == 'sonarPing':
            s = e['sender']
            if s in team and team[s] == us and rnd >= 300:
                x = e['value'] & ((1 << 43) - 1)
                L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023; r0 = (x >> 34) & 511
                if 2 <= L and (rnd - r0) % 512 <= 4:
                    if hop == 0 and kid == (s & 1023): lastk[s] = rnd
                    h = e['hitId']
                    if h is not None and h in team and team[h] == us and h != s: heard[h].append((rnd, kid))
    if len(sys.argv) > 1 or True:
        print('%d %s %s' % (gid, grp, g['opp']))
        for l in out: print('   ' + l)
for grp in 'LW':
    n = ng[grp]
    if not n: continue
    a = agg[grp]
    print('MEAN %s (%d games): ' % (grp, n) + ' | '.join('r%d us L>=10 %.1f (bcast %.1f), others heard real %.0f%%, them L>=10 %.1f' % (
        r, a[(r, 'n')] / n, a[(r, 'kb')] / n, 100 * a[(r, 'hr')] / max(1, a[(r, 'oth')]), a[(r, 'them')] / n) for r in CK))
