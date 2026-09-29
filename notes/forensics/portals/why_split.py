#!/usr/bin/env python3
"""Re-run v29 on the king's reverse-split decisions (kingsplits_L.pkl) and print the candidates at the split turn.
   python3 notes/forensics/portals/why_split.py BIN [MINLEN] [MAXCASES]"""
import os, sys, re, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cap
B = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 10; MAXC = int(sys.argv[3]) if len(sys.argv) > 3 else 40
rows = [o for o in pickle.load(open(os.path.join(HERE, 'kingsplits_L.pkl'), 'rb')) if o['L'] >= MIN]
C = collections.Counter(); res = []
for o in rows[:MAXC]:
    r0 = max(o['born'], o['round'] - 150)
    m, turns = cap.capture(o['game'], o['parent'], r0, o['round'])
    if not turns or turns[-1]['round'] != o['round']: continue
    blocks, dbg = cap.run_full(B, o['parent'], turns)
    bot = [l for l in blocks[-1] if l.startswith(('MOVE', 'SPLIT'))] if blocks else []
    bl = [b for b in re.split(r'\n(?=R\d+ id=)', dbg) if b.startswith('R%d ' % o['round'])]
    bl = bl[-1] if bl else ''
    cands = re.findall(r'cand (\w) t=\((\d+),(\d+)\) pearls=([-\d.]+) area=(\d+) depth=(\d+) threat=\d+ freeT=\d+ score=([-\d.e+]+)', bl)
    arrow = re.findall(r'-> (.*)', bl)
    pocket = re.findall(r'POCKET (\w+)', bl)
    best = max((float(c[6]) for c in cands), default=None)
    kind = 'no candidate (all lethal)' if not cands else ('trapped: best<-100 & depth<4' if best < -100 else 'other')
    C[(kind, 'reproduced' if bot and bot[-1] == 'SPLIT %d' % o['k'] else 'differs')] += 1
    print('%d r%d id%d L%d k=%d exits=%d | bot=%s | %s | %s' % (o['game'], o['round'], o['parent'], o['L'], o['k'], o['exits'], bot[-1:] , ' '.join('%s:area%s/d%s/%s' % (c[0], c[4], c[5], c[6]) for c in cands), arrow), flush=True)
for k, v in sorted(C.items()): print(k, v)
