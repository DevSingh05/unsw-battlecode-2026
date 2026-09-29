#!/usr/bin/env python3
"""Merge efficiency: for big (L>=MINL) deliberate feed deaths (backward into own neck) of the given team, the
ally that ate most of the corpse and how many of the ceil(L/2) pearls it got, plus the rounds it needed.
    python3 .../mergeeff.py MINL us|them GAME...  (default all top losses)"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
top = {}
for line in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
    d = json.loads(line)
    if d.get('rank', 99) <= 15: top.setdefault(d['team'], d['rank'])
MINL = int(sys.argv[1]); who = sys.argv[2]
gids = [int(a) for a in sys.argv[3:]] or sorted(g['game'] for g in led.values() if g['map'] == 'Slithery Fight' and not g['win'] and (g['opp'] in top or g['opp'] == '3.14159265'))
tot = collections.Counter()
for gid in gids:
    g = led[gid]; T = g['side'] if who == 'us' else ('B' if g['side'] == 'A' else 'A')
    S = simulate(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)); m = S['map']
    for d in S['deaths']:
        b = d['body']
        if d['team'] != T or d['len'] < MINL or d['round'] < 350: continue
        if not ((d['reason'] == 'HitSelf' and d.get('move') and len(b) > 1 and m.step(b[0], d['move'][0]) == b[1]) or d['reason'] == 'NoValidAction'): continue
        ate = collections.Counter(); last = collections.defaultdict(int)
        for e in S['eats']:
            if e['corpse'] and e['corpse'][0] == d['id']:
                ate[e['id']] += 1; last[e['id']] = e['round']
        P = (d['len'] + 1) // 2
        best = ate.most_common(1)[0] if ate else (None, 0)
        tot['n'] += 1; tot['P'] += P; tot['best'] += best[1]; tot['all'] += sum(v for j, v in ate.items() if S['team'].get(j) == T)
        print('%d r%d L%d pearls %d: top eater %s ate %d (by r%s), all allies %d, enemy %d' % (gid, d['round'], d['len'], P, best[0], best[1], last.get(best[0]),
              sum(v for j, v in ate.items() if S['team'].get(j) == T), sum(v for j, v in ate.items() if S['team'].get(j) != T)))
print('%s: %d big feeds, pearls %d, top eater got %d (%.0f%%), all allies %d' % (who, tot['n'], tot['P'], tot['best'], 100 * tot['best'] / max(1, tot['P']), tot['all']))
