"""Reconstruct every one of OUR dragons' exact per-turn input (botview.view format) from a replay, for its whole
life, and pipe each life through a compiled bot with BOTDBG. Differences to botview.capture:
  * one pass over the replay for all our dragons; each dragon's process sees its whole life (memory is right);
  * pre-round-0 dragonUpdate events are skipped (no duplicated starter head);
  * pearl countdowns: the tile's next observed spawn round minus now, clamped to [1, gmax] (replays hide countdowns;
    botview used the mid gap for every tile).
    python3 lifeview.py BIN GAME  -> life_<GAME>.pkl  {id: [ {round, act_real, act_bot, dbg} ... ]}
"""
import os, sys, re, pickle, subprocess, tempfile, collections, bisect
from common import *
import replay_decode as R
import botview as BV

def spawn_table(o):
    sp = collections.defaultdict(list); inturn = False
    for e in o['events']:
        if e['t'] == 'roundStart': inturn = False; rnd = e['round']
        elif e['t'] == 'turnStart': inturn = True
        elif e['t'] == 'tileChange' and e['hasPearl'] and not inturn: sp[e['tile']].append(rnd)
    return sp

def view(m, rnd, us, body, team, alive, facing, pearls, msgs, echoes, sp):
    hx, hy = body[us][0]; W, H = m.w, m.h
    tiles = []
    for r in range(7):
        for c in range(7):
            x = (hx + c - 3) % W; y = (hy + r - 3) % H
            g = m.tiles.get((x, y))
            if g is None or g[1] == 0: cd = -1
            else:
                lst = sp.get((x, y), []); i = bisect.bisect_right(lst, rnd)
                cd = (lst[i] - rnd) if i < len(lst) else (g[0] + g[1]) // 2
                cd = max(1, min(cd, g[1]))
            tiles.append('%d %d %d %d' % (x, y, 1 if (x, y) in pearls else 0, cd))
    inview = lambda p: m.cheb(p, (hx, hy)) <= 3
    parts = []
    for j in sorted(alive):
        b = body[j]
        for i, s in enumerate(b):
            if inview(s):
                parts.append('%s %d %d %d %s %d' % (team[j], j, s[0], s[1], BV.seg_facing(m, b, i, facing[j]), 1 if i == 0 else 0))
    def tok(e):
        k, pid = m.edges.get(e, (0, -1))
        return '.' if k == 0 else ('w' if k == 1 else str(pid))
    hl = [' '.join(tok(('H', (hx + c - 3) % W, (hy + r - 3) % H)) for c in range(7)) for r in range(8)]
    vl = [' '.join(tok(('V', (hx + c - 3) % W, (hy + r - 3) % H)) for c in range(8)) for r in range(7)]
    units = sum(1 for j in alive if team[j] == team[us])
    txt = ['ROUND %d' % rnd, 'DIR %s' % facing[us], 'LENGTH %d' % len(body[us]), 'UNIT_COUNT %d' % units,
           'NUM_MSGS %d' % len(msgs)] + [str(v) for v in msgs] + ['ECHOES ' + ' '.join(map(str, echoes))] + tiles + \
          ['DRAGON_BODIES %d' % len(parts)] + parts + hl + vl
    return '\n'.join(txt) + '\n'

def capture_all(g):
    us = GAMES[g]; o = R.load(path(g)); m = sim2.Map(o['map'])
    m.tiles = BV.gap_source(o, m); sp = spawn_table(o)
    body = {}; team = {}; alive = set(); facing = {}
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
        facing[i] = BV.seg_facing(m, pts, 1, None) if len(pts) > 1 else 'N'
    pearls = set(); inbox = collections.defaultdict(list); echo = collections.defaultdict(lambda: [0] * 5)
    EK = {'kelp': 0, 'ally': 1, 'allyHead': 2, 'enemy': 3, 'enemyHead': 4}
    rnd = -1; lives = collections.defaultdict(list); started = False
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']; started = True
        elif t == 'dragonAction':
            i = e['id']
            if team.get(i) == us and i in alive:
                lives[i].append({'round': rnd, 'text': view(m, rnd, i, body, team, alive, facing, pearls, inbox[i], echo[i], sp),
                                 'act': e['action'], 'len': len(body[i]), 'head': body[i][0]})
            inbox[i] = []; echo[i] = [0] * 5
        elif t == 'dragonUpdate':
            if not started:
                facing[e['id']] = e['facing']; continue
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
            facing[i] = e['facing']
        elif t == 'tileChange':
            (pearls.add if e['hasPearl'] else pearls.discard)(e['tile'])
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
            cb = body[c]; facing[c] = e.get('childFacing') or (BV.seg_facing(m, cb, 1, None) if len(cb) > 1 else 'N')
        elif t == 'dragonDeath':
            alive.discard(e['id'])
        elif t == 'sonarPing':
            if e['hitId'] is not None and e['hitKind'] != 'kelp':
                inbox[e['hitId']].append(e['value'])
            if e['hitKind'] in EK:
                echo[e['sender']][EK[e['hitKind']]] += 1
    return m, lives

def fmt_act(a):
    if a is None: return None
    if 'move' in a: return 'MOVE ' + ''.join(a['move'])
    if 'split' in a: return 'SPLIT %d' % a['split']
    return 'SUICIDE'

def run_life(binp, g, i, turns, W, H):
    us = GAMES[g]
    inp = 'ID %d\nTEAM %s\nMAP %d %d\nUNIT_LIMIT 64\n' % (i, us, W, H) + ''.join(t['text'] for t in turns)
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, BOTDBG=td)
        p = subprocess.run([binp], input=inp, capture_output=True, text=True, env=env, timeout=300)
        fp = os.path.join(td, '%d.txt' % i)
        dbg = open(fp).read() if os.path.exists(fp) else ''
    acts = []
    for chunk in p.stdout.split('ENDTURN')[:len(turns)]:
        a = [l for l in chunk.splitlines() if l.startswith('MOVE') or l.startswith('SPLIT')]
        acts.append(a[-1] if a else None)
    blocks = {}
    for b in re.split(r'\n(?=R\d+ id=)', dbg):
        mm = re.match(r'R(\d+) id=', b)
        if mm: blocks[int(mm.group(1))] = b
    out = []
    for k, t in enumerate(turns):
        out.append({'round': t['round'], 'len': t['len'], 'head': t['head'], 'real': fmt_act(t['act']),
                    'bot': acts[k] if k < len(acts) else None, 'dbg': blocks.get(t['round'], '')})
    return out

if __name__ == '__main__':
    binp, g = sys.argv[1], int(sys.argv[2])
    m, lives = capture_all(g)
    res = {}
    agree = tot = 0
    for i, turns in sorted(lives.items()):
        res[i] = run_life(binp, g, i, turns, m.w, m.h)
        for x in res[i]:
            tot += 1; agree += (x['real'] == x['bot'])
    pickle.dump(res, open(os.path.join(H, 'life_%d.pkl' % g), 'wb'))
    print(g, 'dragons', len(res), 'turns', tot, 'agree %.3f' % (agree / max(1, tot)))
