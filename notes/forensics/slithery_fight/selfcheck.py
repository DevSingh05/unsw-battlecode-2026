#!/usr/bin/env python3
"""Every self-inflicted death (HitSelf/HitOtherBody/HitWall) of one of our L>=MINL dragons in the given games:
re-run the debug binary (mkdbg.py) on its last decision and report the decision type ('feed suicide',
'reverse split' parent side, plain move with cands), age, FEEDDBG king state and the real longest ally.
    python3 notes/forensics/slithery_fight/selfcheck.py DBGBIN MINL GAME...  (project root)"""
import json, os, sys, re, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
from sim2 import simulate
import botview as BV
led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
BIN = sys.argv[1]; MINL = int(sys.argv[2]); gids = [int(a) for a in sys.argv[3:]]
agg = collections.Counter()
for gid in gids:
    g = led[gid]; us = g['side']; path = os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid)
    S = simulate(path); snap = dict(S['rounds'])
    for d in S['deaths']:
        if d['team'] != us or d['len'] < MINL or d['reason'] not in ('HitSelf', 'HitOtherBody', 'HitWall'): continue
        i = d['id']; r = d['round']; born = S['born'].get(i, 0)
        m, turns = BV.capture(path, i, max(born, r - 60), r)
        if not turns or turns[-1]['round'] != r: continue
        outs, dbg = BV.run_bot(BIN, i, turns)
        blk = [b for b in re.split(r'\n(?=R\d+ id=)', dbg) if b.startswith('R%d ' % r)]
        b = blk[-1] if blk else ''
        fm = re.search(r'FEEDDBG feeding=(\d) kingId=(-?\d+) kingLen=(\d+) kingTile=\((-?\d+),(-?\d+)\) age=(-?\d+).*?kingSelf=(\d) iAmKing=(\d)', b)
        arrow = (re.findall(r'-> (.*)', b) or ['?'])[-1]
        cands = ' '.join('%s:%s/a%s/d%s' % (mm.group(1), mm.group(5), mm.group(2), mm.group(3)) for mm in re.finditer(r'cand (\w) t=\(\d+,\d+\) pearls=[-\d.]+ area=(\d+) depth=(\d+) threat=(\d+) freeT=\d+ score=([-\d.e+]+)', b))
        prev = snap.get(r - 1, snap.get(r))[us]
        age = r - born
        if 'feed' in arrow: cls = 'FEED-newborn' if age <= 3 else 'FEED'
        elif not cands: cls = 'NO-MOVE(all lethal)' + ('-newborn' if age <= 3 else '')
        else: cls = 'TRAPPED' + ('-young' if age < d['len'] else '')
        agg[cls] += 1; agg['len_' + cls] += d['len']
        ks = ('kingId %s L%s tile(%s,%s) age%s kingSelf %s' % fm.group(2, 3, 4, 5, 6, 7)) if fm else ''
        print('%d r%d id%d L%d age%d %s | real %s bot %s | %s | real longest L%d | %s' % (gid, r, i, d['len'], age, cls, d.get('move'), arrow, ks, prev['max'], cands), flush=True)
print(dict(agg))
