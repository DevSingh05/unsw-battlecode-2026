#!/usr/bin/env python3
"""Full-map render at the start of ROUND: our dragons with L>=MINL get their own letter (head upper case,
body lower case: a/A = longest, b/B = 2nd, ...), other allies '+', enemy dragons 'x' (enemy L>=MINL heads 'X'),
kelp shown as '|' between tiles; pearls '*'.   python3 .../bigmap.py GAME ROUND [MINL=10]"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as RD
from sim2 import Map
def render(gid, R, MINL=10):
    led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
    us = led[gid]['side']
    o = RD.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = Map(o['map'])
    body = {}; team = {}; alive = set(); pearls = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    for e in o['events']:
        t = e['t']
        if t == 'roundStart' and e['round'] == R: break
        if t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'tileChange': (pearls.add if e['hasPearl'] else pearls.discard)(e['tile'])
        elif t == 'dragonSplit':
            p, c = e['parent'], e['child']; body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t == 'dragonDeath': alive.discard(e['id'])
    ours = sorted([j for j in alive if team[j] == us and len(body[j]) >= MINL], key=lambda j: -len(body[j]))
    lab = {j: 'abcdefghijklmnop'[k] for k, j in enumerate(ours)}
    occ = {}
    for j in alive:
        for k, s in enumerate(body[j]):
            if j in lab: occ[s] = lab[j].upper() if k == 0 else lab[j]
            elif team[j] == us: occ[s] = '+'
            else: occ[s] = ('X' if (k == 0 and len(body[j]) >= MINL) else 'x')
    lines = ['    ' + ''.join(str(x // 10) if x % 10 == 0 else ' ' for x in range(m.w))]
    for y in range(m.h):
        row = '%2d  ' % y
        for x in range(m.w):
            row += occ.get((x, y), '*' if (x, y) in pearls else '.')
        lines.append(row)
    leg = '  '.join('%s=%d L%d@%s' % (lab[j].upper(), j, len(body[j]), body[j][0]) for j in ours)
    th = sorted([len(body[j]) for j in alive if team[j] != us], reverse=True)[:5]
    lines.append('ours (L>=%d): %s | enemy top %s' % (MINL, leg, th))
    return '\n'.join(lines)
if __name__ == '__main__':
    print(render(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 10))
