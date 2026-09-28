#!/usr/bin/env python3
"""Our L>=MINL deaths in v16 Default/Trauma: killer move (sprint?), killer len, units, enemy heads near.
    python3 notes/tools/v16diag/bigdeaths.py [MINL=8]
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'midgame')); sys.path.insert(0, os.path.join(HERE, '..'))
from sim2 import simulate
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MINL = int(sys.argv[1]) if len(sys.argv) > 1 else 8
for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
    if g['map'] not in ('Default', 'Trauma'): continue
    G = simulate(os.path.join(ROOT, 'replays/v16/%d.replay' % g['game']))
    us = g['side']; m = G['map']
    snap = dict(G['rounds'])
    kill = {}
    for mv in G['moves']:
        for (vid, vt, vl) in mv['killed']:
            kill[vid] = mv
    for d in G['deaths']:
        if d['team'] != us or d['len'] < MINL: continue
        s = snap.get(d['round'] - 1)
        heads = s['heads'] if s else {}
        myh = d['head']
        en = sorted((m.dist(myh, h[0]), h[1]) for j, h in heads.items() if h[2] != us)
        al = [h for j, h in heads.items() if h[2] == us]
        k = kill.get(d['id'])
        ks = ''
        if k: ks = 'killer id%d L%d move=%s from %s' % (k['id'], k['len_before'], ''.join(k['act'].get('move', [])), k['head'])
        un = s[us]['n'] if s else '?'
        print('%s %d %s r%d L%d %-16s units %s/%s enemy heads(dist,len) prev round: %s  %s' % (
            g['map'][:3], g['game'], 'W' if g['win'] else 'L', d['round'], d['len'], d['reason'], un, s[('B' if us == 'A' else 'A')]['n'] if s else '?', en[:4], ks))
