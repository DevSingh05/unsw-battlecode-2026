#!/usr/bin/env python3
"""Endgame tracker for one game: every STEP rounds from R0, our dragons with L>=MINL (id, len, head, age,
whether it broadcast as king (hop-0 king msg with own id) in the last 10 rounds, and which king it last
HEARD (decoded id/len from a king msg ray that hit it)), plus the enemy's top dragons.
Also: per-window eats of each of our big dragons, and who ate the corpses of our dead dragons.
    python3 notes/forensics/slithery_fight/endgame.py GAME [R0=380] [STEP=10] [MINL=8]"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as RD
from sim2 import Map

def dec(v):
    x = v & ((1 << 43) - 1)
    return dict(x=x & 63, y=(x >> 6) & 63, L=(x >> 12) & 255, id=(x >> 20) & 1023, hop=(x >> 30) & 3, rnd=(x >> 34) & 511)

def main():
    gid = int(sys.argv[1]); R0 = int(sys.argv[2]) if len(sys.argv) > 2 else 380
    STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 10; MINL = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
    us = led[gid]['side']
    o = RD.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = Map(o['map'])
    body = {}; team = {}; alive = set(); born = {}
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i); born[i] = 0
    rnd = 0; actor = None
    lastk = {}      # id -> last round it broadcast as king (hop0 self)
    heard = {}      # id -> (round, decoded)
    eats = collections.Counter()  # (window, id) -> eats
    corpse = {}     # tile -> dead id
    corpse_eat = collections.defaultdict(collections.Counter)  # dead id -> eater id -> n
    deaths = []
    def show():
        ours = sorted([j for j in alive if team[j] == us and len(body[j]) >= MINL], key=lambda j: -len(body[j]))
        th = sorted([len(body[j]) for j in alive if team[j] != us], reverse=True)[:5]
        print('r%d  us(%d units, total %d): ' % (rnd, sum(1 for j in alive if team[j] == us), sum(len(body[j]) for j in alive if team[j] == us)) +
              '  '.join('%d:L%d@%s a%d%s%s' % (j, len(body[j]), body[j][0], rnd - born[j], ' K' if rnd - lastk.get(j, -99) <= 10 else '',
                        (' h%d/L%d/%d' % (heard[j][1]['id'], heard[j][1]['L'], rnd - heard[j][0])) if j in heard and rnd - heard[j][0] <= 12 else '') for j in ours))
        print('        them top', th)
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            rnd = e['round']
            if rnd >= R0 and (rnd - R0) % STEP == 0: show()
        elif t == 'turnStart': actor = e['id']
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'tileChange':
            if not e['hasPearl'] and actor is not None and actor in team and team[actor] == us and rnd >= R0 - 50:
                eats[((rnd // 25) * 25, actor)] += 1
                if e['tile'] in corpse: corpse_eat[corpse[e['tile']]][actor] += 1
            if not e['hasPearl']: corpse.pop(e['tile'], None)
        elif t == 'dragonSplit':
            p, c = e['parent'], e['child']; body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c); born[c] = rnd
            if team[c] == us and rnd >= R0 - 50 and len(body[c]) >= MINL:
                print('   r%d SPLIT parent %d -> L%d, child %d L%d head %s' % (rnd, p, len(body[p]), c, len(body[c]), body[c][0]))
        elif t == 'dragonDeath':
            i = e['id']
            if team[i] == us and rnd >= R0 - 50 and len(body[i]) >= MINL:
                print('   r%d DEATH %d L%d %s at %s (age %d)' % (rnd, i, len(body[i]), e['reason'], body[i][0], rnd - born[i]))
                deaths.append(i)
            for s in body[i][::2]: corpse[s] = i
            alive.discard(i)
        elif t == 'sonarPing':
            s = e['sender']
            if s in team and team[s] == us and rnd >= R0 - 20:
                d = dec(e['value'])
                if 2 <= d['L'] <= 255 and (rnd - d['rnd']) % 512 <= 4:
                    if d['hop'] == 0 and d['id'] == (s & 1023): lastk[s] = rnd
                    h = e['hitId']
                    if h is not None and h in team and team[h] == us: heard[h] = (rnd, d)
    show()
    print('eats per 25 rounds of our dragons that ended/lived >= %d:' % MINL)
    byw = collections.defaultdict(list)
    for (wdw, i), n in sorted(eats.items()):
        if len(body[i]) >= MINL or i in deaths: byw[wdw].append('%d:%d' % (i, n))
    for wdw in sorted(byw): print('  r%d' % wdw, ' '.join(byw[wdw]))
    print('corpses of our big dead dragons eaten by:')
    for i in deaths: print('  ', i, dict(corpse_eat[i]))

main()
