#!/usr/bin/env python3
"""Re-run a compiled bot on one of our dragons' reconstructed views (via rams/botview capture) and print
its debug block for the last round.  python3 notes/tools/devdil/botrun.py BIN GAME ID R_FROM R_TO [grep]"""
import os, sys, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV
GS = {g['game']: g for g in pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))}


def run(binp, gid, did, r0, r1):
    g = GS[gid]
    m, turns = BV.capture(g['path'], did, r0, r1)
    outs, dbg = BV.run_bot(binp, did, turns)
    return turns, outs, dbg


if __name__ == '__main__':
    b, gid, did, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    turns, outs, dbg = run(b, gid, did, r0, r1)
    print('real action at r%d:' % r1, turns[-1].get('act') if turns else None, '| bot outputs:', outs[-3:])
    blocks = dbg.split('\nR')
    for bl in blocks:
        head = bl.split('\n', 1)[0]
        if len(sys.argv) > 6:
            print(head)
        elif head.startswith('%d ' % r1) or head.startswith('R%d ' % r1):
            print('R' + bl if not bl.startswith('R') else bl)
