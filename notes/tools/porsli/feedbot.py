#!/usr/bin/env python3
"""Mechanism probe (no games): sample turns of feed-eligible dragons (same test as feeders.py) and re-run
compiled bots on the reconstructed view; compare how often each binary steps closer to the real king
(walls+portals BFS distance) and whether it matches the real move.
    python3 notes/tools/porsli/feedbot.py Portals|Slithery N BIN1 [BIN2 ...]"""
import collections, os, pickle, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams')); sys.path.insert(0, HERE)
from sim2 import simulate
from board import path_of
import botview as BV
from feeders import mapbfs, cap
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
mp = sys.argv[1]; N = int(sys.argv[2]); bins = sys.argv[3:]
FS, RES = (300, 3) if mp == 'Portals' else (250, 4)
random.seed(7)
gs = [g for g in G if g['map'].startswith(mp) and g['ver'] == 'v28' and not g['win']]
cands = []
for g in gs:
    S = simulate(path_of(g['game'])); T = g['side']; m = S['map']
    msg = collections.defaultdict(list)
    for s in S['sonars']:
        if s['team'] != T or s['hitKind'] not in ('ally', 'allyHead') or s['hitId'] is None: continue
        x = s['value'] & ((1 << 43) - 1); L = (x >> 12) & 255; rnd = (x >> 34) & 511
        if L >= 3 and (s['round'] - rnd) % 512 <= 4: msg[s['hitId']].append((s['round'], L))
    rs = dict(S['rounds'])
    for rn in range(380, 480, 7):
        prev = rs[rn - 1][T]
        for i, L in prev['ids'].items():
            if i == prev['king']: continue
            ms = [x for x in msg.get(i, ()) if rn - 12 <= x[0] < rn]
            if ms and max(x[1] for x in ms) >= L + 2 and L <= cap(rn) and prev['n'] > RES:
                cands.append((g['game'], i, rn, S['born'][i], prev['king'], rs[rn - 1]['heads'][prev['king']][0]))
random.shuffle(cands)
res = collections.Counter(); done = 0
for gid, i, rn, born, k, khead in cands:
    if done >= N: break
    S0 = simulate(path_of(gid), stop=(rn, i)) if False else None
    m, turns = BV.capture(path_of(gid), i, max(born, rn - 40), rn)
    if not turns or turns[-1]['round'] != rn: continue
    real = turns[-1].get('act')
    from sim2 import Map
    bd = mapbfs(m, khead)
    # our head at rn: parse from the view text (tile line 24 is the head: row 3 col 3)
    hx, hy = map(int, turns[-1]['text'].split('\n')[5 + int(turns[-1]['text'].split('\n')[4].split()[1]) + 1 + 24].split()[:2])
    done += 1
    for b in bins:
        outs, dbg = BV.run_bot(b, i, turns)
        o = outs[-1] if outs else ''
        name = os.path.basename(b)
        if o.startswith('MOVE'):
            dd = o.split()[1][-1] if len(o.split()) > 1 else ''
            t = m.step((hx, hy), o.split()[1][0])
            res[(name, 'move')] += 1
            if t is not None and bd.get(t, 99) < bd.get((hx, hy), 99): res[(name, 'closer')] += 1
            if 'feed suicide' in dbg.split('\nR')[-1]: res[(name, 'feedsuicide')] += 1
        else:
            res[(name, 'split')] += 1
        rm = ('MOVE ' + ''.join(real['move'])) if real and 'move' in real else ('SPLIT %d' % real['split'] if real and 'split' in real else '?')
        res[(name, 'match')] += (o == rm)
print('samples', done)
for b in bins:
    nm = os.path.basename(b)
    print('%-10s match real %.0f%% | moves %d, closer to king %.0f%% | feed suicides %d | splits %d' % (
        nm, 100 * res[(nm, 'match')] / max(1, done), res[(nm, 'move')], 100 * res[(nm, 'closer')] / max(1, res[(nm, 'move')]), res[(nm, 'feedsuicide')], res[(nm, 'split')]))
