#!/usr/bin/env python3
"""Re-run our actual bot binary on the reconstructed view of a rammed dragon (from the replay), to get its
per-candidate scores at the decision before the ram.

For each ram in rams.pkl: replays the game once, captures OUR dragon's exact 7x7 input (tiles, visible
segments, edges, sonar messages that hit it, echoes of its own rays) for its turns from
max(birth, R0-WARM) to R0, pipes them through the compiled bot of the version that played (BOTDBG on),
and parses the 'cand' lines of the R0 turn.  Pearl countdowns are not in new replays: we send the tile's
mid gap (or -1 for never-spawn tiles), so pearl value is approximate.

    python3 notes/tools/rams/botview.py BIN_DIR [variant-override]   -> rams_bot.pkl
BIN_DIR holds binaries named v15 v16 v18 v19 v20 v21 (c++ -std=c++20 -O2 variants/vX/main.cpp).
"""
import os, pickle, re, subprocess, sys, tempfile, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import Map

WARM = 40
SRC2VER = {'v16': 'v16', 'ab_v16': 'v16', 'ab_v16_dt': 'v16', 'ab_v18': 'v18', 'ab_v19': 'v19', 'ab_v20': 'v20', 'ab_base': 'v15'}
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def seg_facing(m, b, i, headfacing):
    if i == 0: return headfacing
    for d in 'NESW':
        if m.step(b[i], d) == b[i - 1]: return d
    for d in 'NESW':
        if m.wrap(b[i][0] + DV[d][0], b[i][1] + DV[d][1]) == b[i - 1]: return d
    return 'N'


_MAPS = None
def gap_source(o, m):
    """New replays hide pearl gaps: take them from the local map file with this name whose spawnable tiles
    best explain the round-start spawns seen in the replay (Schooltime has several pearl layouts)."""
    global _MAPS
    if _MAPS is None:
        import glob
        _MAPS = []
        for f in glob.glob(os.path.join(ROOT, 'maps', '*.map')):
            mm = Map(open(f).read()); _MAPS.append(mm)
    if any(g[1] > 0 for g in m.tiles.values()): return m.tiles
    spawns = set(); inturn = False
    for e in o['events']:
        if e['t'] == 'roundStart': inturn = False
        elif e['t'] == 'turnStart': inturn = True
        elif e['t'] == 'tileChange' and e['hasPearl'] and not inturn: spawns.add(e['tile'])
    best = None
    for mm in _MAPS:
        if mm.name != m.name or (mm.w, mm.h) != (m.w, m.h): continue
        sc = sum(1 for t in spawns if mm.tiles.get(t, (0, 0))[1] > 0)
        if best is None or sc > best[0]: best = (sc, mm)
    return best[1].tiles if best else m.tiles


def capture(path, us, r_from, r_to):
    o = R.load(path); m = Map(o['map'])
    m.tiles = gap_source(o, m)
    body = {}; team = {}; alive = set(); facing = {}
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
        facing[i] = seg_facing(m, pts, 1, None) if len(pts) > 1 else 'N'
    pearls = set(); inbox = collections.defaultdict(list); echo = collections.defaultdict(lambda: [0] * 5)
    EK = {'kelp': 0, 'ally': 1, 'allyHead': 2, 'enemy': 3, 'enemyHead': 4}
    rnd = 0; turns = []
    for e in o['events']:
        t = e['t']
        if t == 'roundStart': rnd = e['round']
        elif t == 'dragonAction':
            i = e['id']
            if i == us and r_from <= rnd <= r_to and us in alive:
                turns.append(view(m, rnd, us, body, team, alive, facing, pearls, inbox[us], echo[us]))
                if rnd == r_to:
                    turns[-1]['act'] = e['action']
                    break
            if i == us:
                inbox[us] = []; echo[us] = [0] * 5
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
            facing[i] = e['facing']
        elif t == 'tileChange':
            (pearls.add if e['hasPearl'] else pearls.discard)(e['tile'])
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
            cb = body[c]; facing[c] = seg_facing(m, cb, 1, None) if len(cb) > 1 else 'N'
        elif t == 'dragonDeath':
            alive.discard(e['id'])
        elif t == 'sonarPing':
            if e['hitId'] is not None and e['hitKind'] != 'kelp':
                inbox[e['hitId']].append(e['value'])
            if e['hitKind'] in EK and not (e['hitKind'] == 'kelp' and False):
                echo[e['sender']][EK[e['hitKind']]] += 1
    return m, turns


def view(m, rnd, us, body, team, alive, facing, pearls, msgs, echoes):
    hx, hy = body[us][0]; W, H = m.w, m.h
    tiles = []
    for r in range(7):
        for c in range(7):
            x = (hx + c - 3) % W; y = (hy + r - 3) % H
            g = m.tiles.get((x, y))
            cd = -1 if (g is None or g[1] == 0) else max(1, (g[0] + g[1]) // 2)
            tiles.append('%d %d %d %d' % (x, y, 1 if (x, y) in pearls else 0, cd))
    inview = lambda p: m.cheb(p, (hx, hy)) <= 3
    parts = []
    for j in sorted(alive):
        b = body[j]
        for i, s in enumerate(b):
            if inview(s):
                parts.append('%s %d %d %d %s %d' % (team[j], j, s[0], s[1], seg_facing(m, b, i, facing[j]), 1 if i == 0 else 0))
    def tok(e):
        k, pid = m.edges.get(e, (0, -1))
        return '.' if k == 0 else ('w' if k == 1 else str(pid))
    hl = [' '.join(tok(('H', (hx + c - 3) % W, (hy + r - 3) % H)) for c in range(7)) for r in range(8)]
    vl = [' '.join(tok(('V', (hx + c - 3) % W, (hy + r - 3) % H)) for c in range(8)) for r in range(7)]
    units = sum(1 for j in alive if team[j] == team[us])
    txt = ['ROUND %d' % rnd, 'DIR %s' % facing[us], 'LENGTH %d' % len(body[us]), 'UNIT_COUNT %d' % units,
           'NUM_MSGS %d' % len(msgs)] + [str(v) for v in msgs] + ['ECHOES ' + ' '.join(map(str, echoes))] + tiles + \
          ['DRAGON_BODIES %d' % len(parts)] + parts + hl + vl
    return {'round': rnd, 'text': '\n'.join(txt) + '\n', 'team': team[us], 'W': W, 'H': H}


def run_bot(binary, us, turns):
    team = turns[0]['team']
    inp = 'ID %d\nTEAM %s\nMAP %d %d\nUNIT_LIMIT 64\n' % (us, team, turns[0]['W'], turns[0]['H']) + ''.join(t['text'] for t in turns)
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, BOTDBG=td)
        p = subprocess.run([binary], input=inp, capture_output=True, text=True, env=env, timeout=60)
        dbg = open(os.path.join(td, '%d.txt' % us)).read() if os.path.exists(os.path.join(td, '%d.txt' % us)) else ''
    outs = [l for l in p.stdout.splitlines() if l.startswith('MOVE') or l.startswith('SPLIT')]
    return outs, dbg


def parse_last(dbg, rnd):
    blocks = re.split(r'\n(?=R\d+ id=)', dbg)
    blk = [b for b in blocks if b.startswith('R%d ' % rnd)]
    if not blk: return None
    b = blk[-1]
    cands = {}
    for mm in re.finditer(r'cand (\w) t=\((\d+),(\d+)\) pearls=([-\d.]+) area=(\d+) depth=(\d+) threat=(\d+) freeT=(\d+) score=([-\d.e+]+)', b):
        cands[mm.group(1)] = dict(t=(int(mm.group(2)), int(mm.group(3))), pearls=float(mm.group(4)), area=int(mm.group(5)),
                                  depth=int(mm.group(6)), threat=int(mm.group(7)), score=float(mm.group(9)))
    arrow = re.findall(r'-> (.*)', b)
    return {'cands': cands, 'arrow': arrow, 'raw': b}


def main():
    bindir = sys.argv[1]; override = sys.argv[2] if len(sys.argv) > 2 else None
    D = pickle.load(open(os.path.join(os.path.dirname(__file__), 'rams.pkl'), 'rb'))
    res = {}
    for r in D['rams']:
        path = [p for p in [os.path.join(ROOT, 'replays', r['src'], '%d.replay' % r['game'])] if os.path.exists(p)][0]
        ver = override or SRC2VER.get(r['src'], 'v21')
        # warm-up from birth (a child is a fresh process) or WARM rounds back
        r_from = r['R0'] - WARM  # a child born later is captured from its birth (fresh process)
        m, turns = capture(path, r['id'], r_from, r['R0'])
        if not turns or turns[-1]['round'] != r['R0']:
            print('skip', r['game'], r['round']); continue
        outs, dbg = run_bot(os.path.join(bindir, ver), r['id'], turns)
        pr = parse_last(dbg, r['R0'])
        key = (r['game'], r['round'], r['id'])
        res[key] = {'ver': ver, 'bot_out': outs[-1] if outs else None, 'real': turns[-1].get('act'), 'parsed': pr}
        cs = pr['cands'] if pr else {}
        print(key, ver, 'real', turns[-1].get('act'), 'bot', outs[-1] if outs else None,
              ' '.join('%s:%.0f/th%d/p%.1f/d%d' % (k, v['score'], v['threat'], v['pearls'], v['depth']) for k, v in cs.items()), flush=True)
    tag = override or 'played'
    pickle.dump(res, open(os.path.join(os.path.dirname(__file__), 'rams_bot_%s.pkl' % tag), 'wb'))


if __name__ == '__main__':
    main()
