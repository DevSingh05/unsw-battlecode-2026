#!/usr/bin/env python3
"""Re-run the v29 binary on the exact reconstructed input of one of OUR dragons (from its birth, a fresh
process) and print, for every round in [R0, R1], the real action vs the bot's action and the candidate scores.
    python3 notes/forensics/devil/botrun.py GAME ID R0 [R1] [binary] [extra BOTDBG grep]
Uses notes/tools/rams/botview.py (pearl countdowns are not in replays: mid gap is sent, hot tiles = 1).
"""
import os, sys, re
from common import ROOT, GDIR
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV

SCR = os.environ.get('SCR', '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad')


def born(path, did):
    import replay_decode as R
    o = R.load(path); rnd = 0
    for e in o['events']:
        if e['t'] == 'roundStart': rnd = e['round']
        elif e['t'] == 'dragonAction' and e['id'] == did: return rnd
    return None


def run(gid, did, r0, r1=None, binary=None, quiet=False):
    r1 = r1 or r0
    path = os.path.join(GDIR, '%d.replay' % gid)
    b = born(path, did)
    m, turns = BV.capture(path, did, b, r1)
    # capture stops at r1 and records the real action there; also record real actions of every turn
    import replay_decode as R
    real = {}
    rnd = 0
    for e in R.load(path)['events']:
        if e['t'] == 'roundStart': rnd = e['round']
        elif e['t'] == 'dragonAction' and e['id'] == did: real[rnd] = e['action']
    outs, dbg = BV.run_bot(binary or os.path.join(SCR, 'v29'), did, turns)
    blocks = re.split(r'\n(?=R\d+ id=)', dbg)
    res = {}
    for blk in blocks:
        mm = re.match(r'R(\d+) ', blk)
        if not mm: continue
        r = int(mm.group(1))
        if r0 <= r <= r1:
            res[r] = blk
    # map bot outputs to rounds
    outs_all = []
    p_out = None
    return real, res, turns


def fmt_act(a):
    if a is None: return 'None'
    if 'move' in a: return 'MOVE ' + ''.join(a['move'])
    if 'split' in a: return 'SPLIT %s' % a['split']
    return str(a)


if __name__ == '__main__':
    gid, did, r0 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    r1 = int(sys.argv[4]) if len(sys.argv) > 4 else r0
    binary = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
    real, res, turns = run(gid, did, r0, r1, binary)
    for r in range(r0, r1 + 1):
        blk = res.get(r)
        print('=== R%d id%d real %s' % (r, did, fmt_act(real.get(r))))
        if blk:
            for line in blk.splitlines():
                if line.startswith('R') or 'cand' in line or '->' in line or 'POCKET' in line or 'RAM' in line.upper() or (len(sys.argv) > 6 and sys.argv[6] in line):
                    print('   ' + line.strip())
