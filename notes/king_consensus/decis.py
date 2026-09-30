import sys, os, re
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'
sys.path.insert(0, ROOT+'/notes/forensics/slithery_fight')
import fx
from sim2 import simulate
import botview as BV
bins = sys.argv[1].split(',')
for spec in sys.argv[2:]:
    g, i, *rs = map(int, spec.split(':'))
    S = simulate(fx.path_of(g)); born = S['born'].get(i, 0)
    m, turns = BV.capture(fx.path_of(g), i, born, max(rs))
    for bn in bins:
        outs, dbg = BV.run_bot(bn, i, turns)
        blocks = {int(re.match(r'R(\d+)', b).group(1)): b for b in re.split(r'\n(?=R\d+ id=)', dbg) if re.match(r'R\d+ id=', b)}
        for r in rs:
            b = blocks.get(r, '')
            fd = [l.strip() for l in b.splitlines() if 'FEEDDBG' in l]
            dec = [l.strip() for l in b.splitlines() if '->' in l]
            print('%d/%d r%d %s born%d\n   %s\n   %s' % (g, i, r, os.path.basename(bn), born, fd[0][:230] if fd else '-', dec[-1][:120] if dec else '-'))
