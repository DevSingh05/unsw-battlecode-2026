#!/usr/bin/env python3
"""All maps, replays/v28: our fatal portal crossings, by crosser length band, with (a) free alternatives and
(b) what the crosser's own ray through that portal hit on the previous round (exit tile / beyond / clean / none).
The 'hold' candidates are: no free alternative AND the previous ray echoed a dragon at the exit.
    python3 notes/tools/porsli/exitscan.py"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
C = collections.Counter(); L_ = collections.Counter(); n = collections.Counter()
for g in json.load(open(os.path.join(ROOT, 'replays/v28/ledger.json'))):
    p = os.path.join(ROOT, 'replays/v28/%d.replay' % g['game'])
    if not os.path.exists(p): continue
    S = simulate(p); m = S['map']; T = g['side']; n[g['map']] += 1
    if not any(k == 2 for k, _ in m.edges.values()): continue
    rays = collections.defaultdict(list)
    for s in S['sonars']:
        if s['team'] == T: rays[(s['id'], s['round'])].append(s)
    for d in S['deaths']:
        if d['team'] != T or d['actor'] != d['id']: continue
        mv = d.get('move') or ''
        k = d.get('step_failed', 1) - 1
        if not mv or k >= len(mv) or m.edges.get(m.side_edge(d['head'], mv[k]), (0, -1))[0] != 2: continue
        if len(mv) > 1: continue
        band = 'L2-3' if d['len'] <= 3 else 'L4-7' if d['len'] <= 7 else 'L8+'
        dest = m.step(d['head'], mv[k])
        free = [x for x, v in (d.get('nbrs') or {}).items() if v in ('free', 'pearl')]
        ray = [s for s in rays.get((d['id'], d['round'] - 1), []) if s['dir'] == mv[k]]
        if not ray: echo = 'noray'
        elif ray[0]['hitKind'] == 'kelp': echo = 'clean'
        elif ray[0]['end'] == dest: echo = 'at_exit'
        else: echo = 'beyond'
        key = (g['map'], band, 'alt0' if not free else 'alt+', echo)
        C[key] += 1; L_[key] += d['len']
for mp in sorted(n):
    ks = [k for k in C if k[0] == mp]
    if not ks: continue
    print('== %s (%d games): fatal 1-step portal crossings per game [length lost/g]' % (mp, n[mp]))
    for band in ('L2-3', 'L4-7', 'L8+'):
        row = []
        for alt in ('alt0', 'alt+'):
            for echo in ('at_exit', 'beyond', 'clean', 'noray'):
                v = C[(mp, band, alt, echo)]
                if v: row.append('%s/%s %.2f [%.1f]' % (alt, echo, v / n[mp], L_[(mp, band, alt, echo)] / n[mp]))
        print('   %-5s %s' % (band, '  '.join(row)))
