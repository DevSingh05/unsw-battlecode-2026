#!/usr/bin/env python3
"""Replay one of our dragons turn by turn through a compiled bot and compare every action with the replay.
   python3 notes/forensics/portals/compare.py BIN GAME ID R_FROM R_TO [--show]
--show prints the '->' decision and top candidates for every turn."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cap
import botview as BV

if __name__ == '__main__':
    b, gid, did, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    m, turns = cap.capture(gid, did, r0, r1)
    outs, dbg = BV.run_bot(b, did, turns)
    blocks = {int(x.group(1)): x.group(0) for x in re.finditer(r'R(\d+) id=[^\n]*\n(?:(?!R\d+ id=)[^\n]*\n?)*', dbg)}
    acts = [l for l in outs]
    same = 0
    for i, t in enumerate(turns):
        real = cap.fmt(t['act']); bot = acts[i] if i < len(acts) else None
        same += real == bot
        if '--show' in sys.argv or real != bot:
            bl = blocks.get(t['round'], '')
            arr = ' / '.join(re.findall(r'-> (.*)', bl))
            cs = ' '.join('%s:%s' % (c[0], c[1]) for c in re.findall(r'cand (\w) t=\S+ .*?score=([-\d.e+]+)', bl))
            ex = ' '.join(l.strip() for l in bl.split('\n') if l.strip().startswith(('POCKET', 'KING', 'FEED')))
            print('r%d L%d head=%s real=%-10s bot=%-10s %s | %s %s' % (t['round'], t['len'], t['head'], real, bot, '' if real == bot else '<<DIFF', cs, arr), ex[:150])
    print('match %d/%d' % (same, len(turns)))
