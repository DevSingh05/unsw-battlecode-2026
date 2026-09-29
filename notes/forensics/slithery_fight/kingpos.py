#!/usr/bin/env python3
"""Where the final king lives r350-500 (A frame: B's tiles mirrored by (62-x, 26-y)); per team, histogram of
king-head x-band and y-band, plus mean distance (BFS-free Manhattan) from the king head to the team's
feed-eligible small dragons (L<=6).  python3 notes/forensics/slithery_fight/kingpos.py [GAME...]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
gids = [int(a) for a in sys.argv[1:]] or sorted(g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and not g['win'] and (g['opp'] in top or g['opp'] == '3.14159265'))
H = {'us': collections.Counter(), 'them': collections.Counter()}; D = {'us': [], 'them': []}
for gid in gids:
    g = led[gid]; us = g['side']; th = 'B' if us == 'A' else 'A'
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid))
    # frame: which team started on the A layout?  sim2 team letters are replay letters; the A layout = team whose
    # starting L25 coil is at x<10.  Mirror positions of the other team.
    m = S['map']
    lay = {}
    for t, pts in m.dragons:
        if len(pts) == 25: lay['AB'[t]] = pts[0][0] < 31
    snap = dict(S['rounds'])
    for T, lab in ((us, 'us'), (th, 'them')):
        for r in range(350, 500, 10):
            if r not in snap or not snap[r][T]['n']: continue
            k = snap[r][T]['king']; (x, y), L, _ = snap[r]['heads'][k]
            if not lay.get(T, True): x, y = 62 - x, 26 - y
            H[lab][('x', min(x // 16, 3))] += 1; H[lab][('y', 'top' if y < 9 else 'mid' if y < 18 else 'bot')] += 1
            sm = [snap[r]['heads'][j] for j in snap[r]['heads'] if snap[r]['heads'][j][2] == T and snap[r]['heads'][j][1] <= 6]
            if sm:
                hx, hy = snap[r]['heads'][k][0]
                D[lab].append(sum(abs(p[0][0] - hx) + abs(p[0][1] - hy) for p in sm) / len(sm))
for lab in ('us', 'them'):
    n = sum(v for (a, b), v in H[lab].items() if a == 'x')
    print(lab, 'king head x-band (A frame, 0-15/16-31/32-47/48-62):', [round(100 * H[lab][('x', i)] / n) for i in range(4)],
          ' y-band top/mid/bot:', [round(100 * H[lab][('y', b)] / n) for b in ('top', 'mid', 'bot')],
          ' mean Manhattan king->small heads %.1f' % (sum(D[lab]) / len(D[lab])))
