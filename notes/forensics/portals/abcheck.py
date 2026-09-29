#!/usr/bin/env python3
"""Mechanism check (no games): run several binaries on the same reconstructed decisions and print their actions.
   python3 notes/forensics/portals/abcheck.py BIN1,BIN2,... GAME:ID:R_FROM:R_TO ..."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cap
bins = sys.argv[1].split(',')
for spec in sys.argv[2:]:
    gid, did, r0, r1 = map(int, spec.split(':'))
    m, turns = cap.capture(gid, did, r0, r1)
    print('== %d id%d r%d-%d real: %s' % (gid, did, r0, r1, ' '.join('r%d:%s' % (t['round'], cap.fmt(t['act'])) for t in turns[-4:])))
    for b in bins:
        blocks, dbg = cap.run_full(b, did, turns)
        acts = [next((l for l in bl if l.startswith(('MOVE', 'SPLIT'))), '?') for bl in blocks]
        arrows = {}
        for bl in re.split(r'\n(?=R\d+ id=)', dbg):
            mm = re.match(r'R(\d+) ', bl)
            if mm: arrows[int(mm.group(1))] = ' / '.join(re.findall(r'-> (.*)', bl))
        print('  %-8s %s' % (os.path.basename(b), ' '.join('r%d:%s(%s)' % (t['round'], a, arrows.get(t['round'], '')) for t, a in list(zip(turns, acts))[-4:])))
