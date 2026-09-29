#!/usr/bin/env python3
"""Per-game overview of every Slithery Fight game in replays/auto/games (ledger), top-15 flagged.
Prints timelines (units/total/longest us|them), final, and every death of OUR dragons with L>=6
(round, id, len, reason, head, age, killer).  Run from project root:
    python3 notes/forensics/slithery_fight/overview.py [game ...]
Caches sims in notes/forensics/slithery_fight/sims.pkl"""
import json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
games = [g for g in L if g['map'] == 'Slithery Fight']
games.sort(key=lambda g: g['game'])
cache_p = os.path.join(HERE, 'sims.pkl')
cache = pickle.load(open(cache_p, 'rb')) if os.path.exists(cache_p) else {}
want = set(int(a) for a in sys.argv[1:])
changed = False
for g in games:
    if want and g['game'] not in want: continue
    gid = g['game']; us = g['side']; th = 'B' if us == 'A' else 'A'
    if gid not in cache:
        S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid))
        rs = {r: s for r, s in S['rounds']}
        cache[gid] = {'rounds': {r: {T: {k: rs[r][T][k] for k in ('n', 'max', 'total', 'lens', 'king')} for T in 'AB'} for r in rs},
                      'deaths': S['deaths'], 'splits': S['splits'], 'last': S['last_round'], 'result': S['result']}
        changed = True
    C = cache[gid]
    print('=== %d %s opp=%s top=%s ranked=%s side=%s %s' % (gid, 'WIN ' if g['win'] else 'LOSS', g['opp'], top.get(g['opp']), g['ranked'], us, g['at'][:16]))
    line = []
    for r in (50, 100, 150, 200, 250, 300, 350, 400, 450, C['last']):
        if r in C['rounds']:
            a = C['rounds'][r][us]; b = C['rounds'][r][th]
            line.append('r%d u%d/%d t%d/%d L%d/%d' % (r, a['n'], b['n'], a['total'], b['total'], a['max'], b['max']))
    print('   ' + ' | '.join(line))
    f = C['rounds'][C['last']]
    print('   final lens us', f[us]['lens'][:6], 'them', f[th]['lens'][:6])
    for d in C['deaths']:
        if d['team'] == us and d['len'] >= 6:
            k = ''
            if d.get('killer') is not None: k = 'killer %d L%d %s' % (d['killer'], d['killer_len'], d['killer_team'])
            if d.get('hit'): k = 'hit %s' % (d['hit'],)
            print('   DEATH r%d id%d L%d %s head%s age%d %s king%s' % (d['round'], d['id'], d['len'], d['reason'], d['head'], d['age'], k, d.get('king')))
if changed: pickle.dump(cache, open(cache_p, 'wb'))
