#!/usr/bin/env python3
"""Re-run v29 on the last decision of every ram victim that CHOSE a landing tile inside the killer's reach
while an out-of-reach tile existed (victims_L.pkl / victims_W.pkl from victims.py). Prints the bot's move,
the score/pearls/threat of the chosen tile and of the best safe tile, and the margin.
    python3 notes/forensics/devil/victims_bot.py L [binary]
"""
import sys, pickle, re, os, collections
from common import HERE
import botrun

tag = sys.argv[1] if len(sys.argv) > 1 else 'L'
binary = sys.argv[2] if len(sys.argv) > 2 else None
rows = pickle.load(open(os.path.join(HERE, 'victims_%s.pkl' % tag), 'rb'))
CRE = re.compile(r'cand (\w) t=\((\d+),(\d+)\) pearls=([-\d.]+) area=(\d+) depth=(\d+) threat=(\d+) freeT=(\d+) score=([-\d.e+]+)')
out = []; stat = collections.Counter()
for r in rows:
    if not (r['safe_alt'] and r['zone'] > 0): continue
    try:
        real, res, turns = botrun.run(r['game'], r['id'], r['lastr'], r['lastr'], binary)
    except Exception as ex:
        print('fail', r['game'], r['id'], ex); continue
    blk = res.get(r['lastr'], '')
    cands = {mm.group(1): dict(t=(int(mm.group(2)), int(mm.group(3))), pearls=float(mm.group(4)), area=int(mm.group(5)), depth=int(mm.group(6)),
                               threat=int(mm.group(7)), score=float(mm.group(9))) for mm in CRE.finditer(blk)}
    arrow = re.findall(r'-> (.*)', blk)
    bot = arrow[-1].strip() if arrow else '?'
    same = bot == r['act'][0] if len(bot) == 1 else False
    zone_of = {d: z for d, t, z in r['alts']}
    ch = cands.get(r['act'][0]); safe = [(c['score'], d, c) for d, c in cands.items() if zone_of.get(d) == 0]
    sb = max(safe) if safe else None
    stat['n'] += 1; stat['reproduced'] += same
    if ch and sb:
        margin = ch['score'] - sb[0]
        stat['z%d' % r['zone']] += 1
        stat['threat_flag_z%d' % r['zone']] += ch['threat'] > 0
        out.append(dict(r, bot=bot, ch=ch, safe=sb[2], safe_d=sb[1], margin=margin))
        print('%d r%d us%d L%d zone%d act %s bot %s | chosen %s sc %.1f p %.2f thr %d a %d | best safe %s sc %.1f p %.2f a %d | margin %.1f | local %d/%d' % (
            r['game'], r['lastr'], r['id'], r['L'], r['zone'], r['act'], bot, r['act'][0], ch['score'], ch['pearls'], ch['threat'], ch['area'],
            sb[1], sb[0], sb[2]['pearls'], sb[2]['area'], margin, r['loc_a'], r['loc_e']), flush=True)
print(dict(stat))
ms = sorted(o['margin'] for o in out)
if ms: print('margin chosen-minus-best-safe: median %.1f, <5: %d, <10: %d, <15: %d of %d' % (ms[len(ms) // 2], sum(m < 5 for m in ms), sum(m < 10 for m in ms), sum(m < 15 for m in ms), len(ms)))
pickle.dump(out, open(os.path.join(HERE, 'victims_bot_%s.pkl' % tag), 'wb'))
