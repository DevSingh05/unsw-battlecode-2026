#!/usr/bin/env python3
"""Why don't our big non-king dragons feed?  For every one of our dragons that is L>=MINL at some round >= R0,
re-run the debug binary (mkdbg.py build) from its birth to its death/end and read the FEEDDBG line of every turn
r>=R0.  Per turn, with best = the longest king in its kingsSeen heard <= 20 rounds ago:
  CROWN   kingSelf=1 although best >= myLen+2                      (bug B: KING_V2 declared/never stepped down)
  DEMOTED kingSelf=0, iAmKing=1 because kingId points at a king shorter than us while best >= myLen+2
          (bug A: readMessages replaced the long king by a short fresh one after 6 silent rounds)
  FEEDOK  feeding=1 and kingLen >= best-2
  FEEDLES feeding=1 but kingLen < best-2 (feeding a lesser king)
  NOKING  nothing longer heard within 20 rounds (can't feed: coverage)
  KING    it is (one of) the longest known: fine
Also reports the actual real longest ally.  python3 .../kingstate.py DBGBIN MINL R0 GAME...   (project root)"""
import json, os, sys, re, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate
import botview as BV
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
BIN = sys.argv[1]; MINL = int(sys.argv[2]); R0 = int(sys.argv[3]); gids = [int(a) for a in sys.argv[4:]]
tot = collections.Counter()
for gid in gids:
    g = led[gid]; us = g['side']; path = os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)
    S = simulate(path); snap = dict(S['rounds'])
    death = {d['id']: d['round'] for d in S['deaths']}
    ids = set()
    for r, s in S['rounds']:
        if r >= R0:
            for j, L in s[us]['ids'].items():
                if L >= MINL: ids.add(j)
    gc = collections.Counter()
    for i in sorted(ids):
        born = S['born'].get(i, 0); end = min(death.get(i, 500), S['last_round'])
        m, turns = BV.capture(path, i, born, end)
        if not turns: continue
        outs, dbg = BV.run_bot(BIN, i, turns)
        c = collections.Counter()
        for blk in re.split(r'\n(?=R\d+ id=)', dbg):
            mm = re.match(r'R(\d+) id=\d+ len=(\d+)', blk)
            if not mm or int(mm.group(1)) < R0: continue
            r = int(mm.group(1)); L = int(mm.group(2))
            f = re.search(r'FEEDDBG feeding=(\d) kingId=(-?\d+) kingLen=(\d+).*?kingSelf=(\d) iAmKing=(\d) myLen=\d+ nKings=\d+ seen=(.*)', blk)
            if not f: continue
            feeding, kid, klen, ks, iak = int(f.group(1)), int(f.group(2)), int(f.group(3)), int(f.group(4)), int(f.group(5))
            seen = [(int(a), int(b), int(cc)) for a, b, cc in re.findall(r'\[(\d+) L(\d+) age(\d+)\]', f.group(6))]
            best = max([b for a, b, cc in seen if cc <= 20] or [0])
            if best >= L + 2:
                if ks: st = 'CROWN'
                elif iak: st = 'DEMOTED'
                elif feeding: st = 'FEEDOK' if klen >= best - 2 else 'FEEDLES'
                else: st = 'OTHER'
            else:
                st = 'KING' if iak else 'NOKING'
            c[st] += 1
        realmax = snap[S['last_round']][us]['max']
        print('%d id%d born r%d end r%d len@end %s  %s' % (gid, i, born, end, snap.get(end, snap[S['last_round']])[us]['ids'].get(i, '-'), dict(c)), flush=True)
        gc.update(c)
    print('  GAME %d: %s' % (gid, dict(gc)))
    tot.update(gc)
print('TOTAL dragon-turns r>=%d of L>=%d dragons: %s' % (R0, MINL, dict(tot)))
