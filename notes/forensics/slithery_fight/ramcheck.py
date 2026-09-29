#!/usr/bin/env python3
"""Every ram of one of our L>=MINL dragons by an enemy head (we are the victim) in the given games: re-run our
binary on the victim's last decision (round r if our id < killer id, else r-1; process started at
max(birth, r-40)) and classify it:
  SEEN-ONLY   the chosen tile had threat>0 and every candidate had threat>0 (no threat-free plain move)
  SEEN-TRAP   chosen tile threat>0, a threat-free candidate existed but it was a dead end (depth<want / area<len)
  SEEN-PREF   chosen tile threat>0 although a threat-free non-dead-end candidate existed (score preferred it)
  UNSEEN      the chosen tile had threat 0 (the rammer's reach was underestimated / it was out of view)
    python3 notes/forensics/slithery_fight/ramcheck.py BIN MINL GAME...  (project root)"""
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
    S = simulate(path)
    for d in S['deaths']:
        if d['team'] != us or d['len'] < MINL or d['reason'] != 'HitHeadToHead' or d.get('killer') is None or d.get('killer_team') == us: continue
        i = d['id']; r = d['round'] if i < d['killer'] else d['round'] - 1
        born = S['born'].get(i, 0)
        if r < born: continue
        m, turns = BV.capture(path, i, max(born, r - 40), r)
        if not turns or turns[-1]['round'] != r: continue
        outs, dbg = BV.run_bot(BIN, i, turns)
        blk = [b for b in re.split(r'\n(?=R\d+ id=)', dbg) if b.startswith('R%d ' % r)]
        b = blk[-1] if blk else ''
        cands = {mm.group(1): dict(area=int(mm.group(2)), depth=int(mm.group(3)), threat=int(mm.group(4)), score=float(mm.group(5)))
                 for mm in re.finditer(r'cand (\w) t=\(\d+,\d+\) pearls=[-\d.]+ area=(\d+) depth=(\d+) threat=(\d+) freeT=\d+ score=([-\d.e+]+)', b)}
        arrow = (re.findall(r'-> (.*)', b) or ['?'])[-1]
        real = turns[-1].get('act')
        ch = arrow[0] if arrow and arrow[0] in 'NESW' and len(arrow) == 1 else None
        L = d['len']
        if ch and ch in cands:
            c = cands[ch]
            free = [k for k, v in cands.items() if v['threat'] == 0]
            good = [k for k in free if cands[k]['depth'] >= 12 and cands[k]['area'] >= L]
            cls = 'UNSEEN' if c['threat'] == 0 else ('SEEN-ONLY' if not free else ('SEEN-PREF' if good else 'SEEN-TRAP'))
        else:
            cls = 'OTHER(%s)' % arrow
        agg[cls] += 1; agg['len_' + cls] += L
        print('%d r%d id%d L%d killer L%d  real=%s bot=%s  %s  cands %s' % (gid, d['round'], i, L, d['killer_len'], real, outs[-1] if outs else None, cls,
              ' '.join('%s:%.0f/th%d/a%d/d%d' % (k, v['score'], v['threat'], v['area'], v['depth']) for k, v in cands.items())), flush=True)
print(dict(agg))
