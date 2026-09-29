#!/usr/bin/env python3
"""capture() like notes/tools/rams/botview.py, but records the real action of every captured turn and the real
children ids, and supports stopping at the child's birth. Used by compare.py / botrun."""
import os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import botview as BV
import replay_decode as R
from sim2 import Map
GD = os.path.join(ROOT, 'replays/auto/games')


def capture(gid, us, r_from, r_to):
    path = os.path.join(GD, '%d.replay' % gid)
    o = R.load(path); m = Map(o['map'])
    m.tiles = BV.gap_source(o, m)
    body = {}; team = {}; alive = set(); facing = {}
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
        facing[i] = BV.seg_facing(m, pts, 1, None) if len(pts) > 1 else 'N'
    pearls = set(); inbox = collections.defaultdict(list); echo = collections.defaultdict(lambda: [0] * 5)
    EK = {'kelp': 0, 'ally': 1, 'allyHead': 2, 'enemy': 3, 'enemyHead': 4}
    rnd = 0; turns = []; started = False
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            rnd = e['round']; started = True
            if rnd > r_to: break
        elif t == 'dragonAction':
            i = e['id']
            if i == us and r_from <= rnd <= r_to and us in alive:
                v = BV.view(m, rnd, us, body, team, alive, facing, pearls, inbox[us], echo[us])
                v['act'] = e['action']; v['len'] = len(body[us]); v['head'] = body[us][0]
                turns.append(v)
            if i == us:
                inbox[us] = []; echo[us] = [0] * 5
        elif t == 'dragonUpdate':
            if not started:  # initial placement events: body already from the map (sim2 double-counts the head here)
                facing[e['id']] = e['facing']; continue
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
            facing[i] = e['facing']
        elif t == 'tileChange':
            (pearls.add if e['hasPearl'] else pearls.discard)(e['tile'])
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
            cb = body[c]; facing[c] = BV.seg_facing(m, cb, 1, None) if len(cb) > 1 else 'N'
        elif t == 'dragonDeath':
            alive.discard(e['id'])
        elif t == 'sonarPing':
            if e['hitId'] is not None and e['hitKind'] != 'kelp':
                inbox[e['hitId']].append(e['value'])
            if e['hitKind'] in EK:
                echo[e['sender']][EK[e['hitKind']]] += 1
    return m, turns


def fmt(a):
    if a is None: return 'none'
    if 'move' in a: return 'MOVE ' + ''.join(a['move'])
    if 'split' in a: return 'SPLIT %s' % a['split']
    return 'SUICIDE' if 'suicide' in a else str(a)


def run_full(binary, us, turns, env_extra=None):
    """Run the bot on captured turns; return (per-turn stdout blocks, debug text)."""
    import subprocess, tempfile
    team = turns[0]['team']
    inp = 'ID %d\nTEAM %s\nMAP %d %d\nUNIT_LIMIT 64\n' % (us, team, turns[0]['W'], turns[0]['H']) + ''.join(t['text'] for t in turns)
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, BOTDBG=td, **(env_extra or {}))
        p = subprocess.run([binary], input=inp, capture_output=True, text=True, env=env, timeout=120)
        f = os.path.join(td, '%d.txt' % us)
        dbg = open(f).read() if os.path.exists(f) else ''
    blocks = []; cur = []
    for l in p.stdout.splitlines():
        cur.append(l)
        if l.strip() == 'ENDTURN':
            blocks.append(cur); cur = []
    return blocks, dbg
