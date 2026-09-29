#!/usr/bin/env python3
"""Re-run a compiled bot on one of our dragons' reconstructed views and print the debug blocks.
    python3 notes/forensics/schooltime/botrun.py BIN GAME ID R_FROM R_TO [--all] [--grep PAT]
R_FROM should be the dragon's birth round (a split child is a fresh process; a parent keeps its memory from r0,
so use R_FROM=0 for original starters or the child birth round).  --all prints every round's block (default: last).
Pearl countdowns are approximated (tile mid gap, from the best-matching local map file)."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams')); sys.path.insert(0, HERE)
import botview as BV
from board import path_of

def run(b, gid, did, r0, r1):
    m, turns = BV.capture(path_of(gid), did, r0, r1)
    outs, dbg = BV.run_bot(b, did, turns)
    return turns, outs, dbg

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    b, gid, did, r0, r1 = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4])
    turns, outs, dbg = run(b, gid, did, r0, r1)
    print('turns', len(turns), 'real action at r%d:' % r1, turns[-1].get('act') if turns else None, '| bot outputs (last 3):', outs[-3:])
    blocks = re.split(r'\n(?=R\d+ id=)', dbg)
    for bl in blocks:
        mm = re.match(r'R(\d+) ', bl)
        if not mm: continue
        if '--all' in sys.argv or int(mm.group(1)) == r1:
            if '--brief' in sys.argv:
                print('\n'.join(l for l in bl.splitlines() if l.startswith('R') or 'cand' in l or '->' in l or 'POCKET' in l))
            else:
                print(bl)
