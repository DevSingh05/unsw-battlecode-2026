#!/usr/bin/env python3
"""Our self-declared kings (hop-0 king sonar with kid == sender id) in one game: tenure, length, how it ended.
   python3 notes/forensics/portals/kings.py GAME [minround]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GD = os.path.join(ROOT, 'replays/auto/games')
led = {g['game']: g for g in json.load(open(os.path.join(GD, 'ledger.json')))}


def kings(gid, r0=200, quiet=False):
    g = led[gid]; T = g['side']
    S = simulate(os.path.join(GD, '%d.replay' % gid))
    K = {}
    heard = collections.Counter()
    for s in S['sonars']:
        if s['team'] != T or s['round'] < r0: continue
        x = s['value'] & ((1 << 43) - 1)
        L = (x >> 12) & 255; hop = (x >> 30) & 3; kid = (x >> 20) & 1023; rnd = (x >> 34) & 511
        if L < 2 or (s['round'] - rnd) % 512 > 4: continue
        if hop == 0 and kid == (s['id'] & 1023):
            k = K.setdefault(s['id'], {'first': s['round'], 'last': s['round'], 'maxL': L, 'Ls': {}})
            k['last'] = s['round']; k['maxL'] = max(k['maxL'], L); k['Ls'][s['round']] = L
        if s['hitKind'] in ('ally', 'allyHead'):
            heard[(s['round'] // 25) * 25] += 1
    dd = {d['id']: d for d in S['deaths']}
    rows = []
    for i, k in sorted(K.items(), key=lambda kv: kv[1]['first']):
        d = dd.get(i)
        fate = ('died r%d L%d %s move=%s nbrs=%s' % (d['round'], d['len'], d['reason'], d.get('move'), d.get('nbrs'))) if d else 'alive at end L%d' % len(S['body'][i])
        rows.append((i, k, fate))
        if not quiet:
            Ls = sorted(k['Ls'].items())
            print('king %4d r%d-%d maxL %2d  L@first %d L@last %d  | %s' % (i, k['first'], k['last'], k['maxL'], Ls[0][1], Ls[-1][1], fate))
    return S, K, rows


if __name__ == '__main__':
    kings(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 200)
