#!/usr/bin/env python3
"""Re-run a compiled bot on one of our dragons' reconstructed views (rams/botview capture) and print the
debug block of the last round.  python3 notes/tools/porsli/botrun.py BIN GAME ID R_FROM R_TO
(A split child is a fresh process: use R_FROM = its birth round.)  Pearl countdowns are approximate."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams')); sys.path.insert(0, HERE)
import botview as BV
from board import path_of

if __name__ == '__main__':
    b, gid, did, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    m, turns = BV.capture(path_of(gid), did, r0, r1)
    outs, dbg = BV.run_bot(b, did, turns)
    print('real action at r%d:' % r1, turns[-1].get('act') if turns else None, '| bot outputs (last 3):', outs[-3:])
    for bl in dbg.split('\nR'):
        head = bl.split('\n', 1)[0]
        if head.startswith('%d ' % r1) or head.startswith('R%d ' % r1):
            print('R' + bl if not bl.startswith('R') else bl)
