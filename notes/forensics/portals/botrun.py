#!/usr/bin/env python3
"""Re-run a compiled bot on one of our dragons' reconstructed inputs from an auto/games replay.
   python3 notes/forensics/portals/botrun.py BIN GAME ID R_FROM R_TO [--all]
Prints the real action vs the bot action for every turn (--all) and the full debug block of R_TO.
A split child is a fresh process: use R_FROM = its birth round. Starters: R_FROM = 1 is exact (modulo pearl countdowns,
which replays do not contain: tiles get their mid gap)."""
import os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import botview as BV
GD = os.path.join(ROOT, 'replays/auto/games')


def fmt(a):
    if a is None: return None
    if 'move' in a: return 'MOVE ' + ''.join(a['move'])
    if 'split' in a: return 'SPLIT %s' % a['split']
    return str(a)


def run(b, gid, did, r0, r1, show_all=False):
    m, turns = BV.capture(os.path.join(GD, '%d.replay' % gid), did, r0, r1)
    outs, dbg = BV.run_bot(b, did, turns)
    return m, turns, outs, dbg


if __name__ == '__main__':
    b, gid, did, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    m, turns, outs, dbg = run(b, gid, did, r0, r1)
    blocks = re.split(r'\n(?=R\d+ id=)', dbg)
    if '--all' in sys.argv:
        # real actions for all captured turns need a second pass: capture stores 'act' only for the last; recompute cheaply
        for bl in blocks:
            h = bl.split('\n', 1)[0]
            arr = re.findall(r'-> (.*)', bl)
            print(h[:90], '|', ' / '.join(arr)[:120])
    print('real action at r%d:' % r1, turns[-1].get('act') if turns else None, '| bot outputs (last 3):', outs[-3:])
    for bl in blocks:
        if bl.startswith('R%d ' % r1):
            print(bl)
