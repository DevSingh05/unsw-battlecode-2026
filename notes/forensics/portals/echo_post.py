#!/usr/bin/env python3
"""Post-analysis of echoscan2.pkl: forced splits at tube exits by echo distance / length / king status / game result."""
import os, sys, pickle, collections, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, HERE)
import replay_decode as R
EV = pickle.load(open(os.path.join(HERE, 'echoscan2.pkl'), 'rb'))
kings = {}
def kingset(gid):
    if gid in kings: return kings[gid]
    o = R.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); ks = collections.defaultdict(set)
    for e in o['events']:
        if e['t'] == 'sonarPing':
            x = e['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023
            if hop == 0 and kid == (e['sender'] & 1023) and L >= 2: ks[e['sender']].add(e.get('round', 0))
    kings[gid] = ks; return ks
C = collections.Counter(); Ls = collections.Counter(); rows = []
for c in EV:
    if c['what'] != 'split' or c['free_alts'] > 0: continue
    ks = kingset(c['game'])
    isk = c['id'] in ks
    b = 'past0' if c['past'] == 0 else 'past1' if c['past'] == 1 else 'past2+'
    st = 'free' if c['exit_occ'] is None else 'taken'
    lb = 'L4-5' if c['L'] < 6 else 'L6-9' if c['L'] < 10 else 'L10+'
    C[(b, st, lb)] += 1; Ls[(b, st)] += c['L']
    if isk: C[(b, st, 'KING')] += 1
    if c['L'] >= 10 or isk:
        rows.append((c['game'], 'W' if c['win'] else 'L', c['round'], c['id'], 'L%d' % c['L'], 'king' if isk else '', c['dir'], c['head'], '->', c['exit'], 'hit', c['hit_end'], c['hitKind'], c['hitId'], 'past=%d' % c['past'], st, c['sp']['k'] if c['sp'] else ''))
ng = len(set(c['game'] for c in EV))
print('games', ng)
for k, v in sorted(C.items()): print(k, v, '%.2f/game' % (v / ng))
for k, v in sorted(Ls.items()): print('length', k, v, '%.1f/game' % (v / ng))
print('--- forced splits of L>=10 or declared kings')
for r in sorted(rows): print(*r)
