#!/usr/bin/env python3
"""Our L>=8 dragons that hit themselves while a free/pearl neighbour existed: when, how long vs our longest,
and whether a longer ally ate the dropped pearls within 10 rounds (i.e. useful feeding)."""
import collections, glob, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import replay_decode as R
games = {}
for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
    games[g['game']] = (os.path.join(ROOT, 'replays/v16/%d.replay' % g['game']), g['side'], g['map'])
for d in glob.glob(os.path.join(ROOT, 'replays/ab_*/summary.json')):
    for g in json.load(open(d)):
        p = os.path.join(os.path.dirname(d), '%d.replay' % g['id'])
        if os.path.exists(p):
            res = R.load(p)['result']; games[g['id']] = (p, 'A' if res['A'] == g['us'] else 'B', g['map'])
rows = []
for gid, (p, side, mp) in games.items():
    if not os.path.exists(p): continue
    G = simulate(p)
    snap = dict(G['rounds'])
    for d in G['deaths']:
        if d['team'] != side or d['len'] < 8 or d['actor'] != d['id'] or d['reason'] != 'HitSelf': continue
        nb = d.get('nbrs', {})
        if not [k for k, v in nb.items() if v in ('free', 'pearl')]: continue
        s = snap.get(d['round'] - 1) or snap.get(d['round'])
        mx = s[side]['max'] if s else 0
        # pearls from this corpse eaten by our team within 10 rounds
        eaten = sum(1 for e in G['eats'] if e['team'] == side and e['corpse'] and e['corpse'][0] == d['id'] and e['round'] - d['round'] <= 10)
        rows.append((mp, d['round'], d['len'], mx, eaten, d['age']))
print('n', len(rows))
bucket = collections.Counter()
for mp, r, L, mx, eaten, age in rows:
    bucket[(r // 100 * 100, 'longest' if L >= mx else 'not-longest')] += 1
for k in sorted(bucket): print(k, bucket[k])
print('mean pearls eaten back within 10r:', sum(r[4] for r in rows) / max(1, len(rows)), ' mean len', sum(r[2] for r in rows) / max(1, len(rows)))
print('longest-dragon self-hits:', [(r[0][:8], r[1], r[2], r[4]) for r in rows if r[2] >= r[3]][:20])
