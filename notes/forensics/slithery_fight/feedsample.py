#!/usr/bin/env python3
"""Re-run the debug v29 (mkdbg.py build) on a sample of our backward-into-neck deaths (feed suicides) in r250-460
of the given games, and report: did the bot decide 'feed suicide', the king it fed (id, len), the real
longest ally at that moment, and how many of the corpse pearls the target king / the final king ate.
    python3 notes/forensics/slithery_fight/feedsample.py BIN N_PER_GAME GAME...     (from project root)"""
import json, os, sys, re, random, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate
import botview as BV
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
BIN = sys.argv[1]; NPG = int(sys.argv[2]); gids = [int(a) for a in sys.argv[3:]]
random.seed(7)
agg = collections.Counter(); rows = []
for gid in gids:
    g = led[gid]; us = g['side']; path = os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)
    S = simulate(path); snap = dict(S['rounds'])
    cand = []
    for d in S['deaths']:
        b = d['body']
        if d['team'] != us or not (250 <= d['round'] <= 460) or d['reason'] != 'HitSelf' or not d.get('move') or d.get('steps', 1) != 1 or len(b) < 2: continue
        if S['map'].step(b[0], d['move'][0]) != b[1]: continue
        cand.append(d)
    for d in random.sample(cand, min(NPG, len(cand))):
        r = d['round']; i = d['id']; born = S['born'].get(i, 0)
        m, turns = BV.capture(path, i, max(born, r - 40), r)
        outs, dbg = BV.run_bot(BIN, i, turns)
        blk = [b for b in re.split(r'\n(?=R\d+ id=)', dbg) if b.startswith('R%d ' % r)]
        b = blk[-1] if blk else ''
        fm = re.search(r'FEEDDBG feeding=(\d) kingId=(-?\d+) kingLen=(\d+)', b)
        dec = 'feed' if 'feed suicide' in b else ('other:' + (re.findall(r'-> (.*)', b) or ['?'])[-1])
        prev = snap.get(r - 1, snap.get(r))[us]
        real = prev['max']; realk = prev['king']
        kid = int(fm.group(2)) if fm else -1; klen = int(fm.group(3)) if fm else 0
        # who ate this corpse
        ate = collections.Counter()
        for e in S['eats']:
            if e['corpse'] and e['corpse'][0] == i:
                ate['target' if (e['id'] & 1023) == (kid & 1023) else ('realking' if e['id'] == realk else ('ally' if e['team'] == us else 'enemy'))] += 1
        rows.append((gid, r, i, d['len'], dec, kid, klen, real, dict(ate)))
        agg['n'] += 1; agg[dec.split(':')[0]] += 1
        if dec == 'feed':
            agg['lesser'] += klen < real - 2
            agg['kl<10'] += klen < 10
            agg['pearls'] += (d['len'] + 1) // 2
            for k, v in ate.items(): agg['ate_' + k] += v
        print('%d r%d id%d L%d %s -> king %d L%d (real longest L%d) corpse eaten by %s' % rows[-1], flush=True)
print(dict(agg))
