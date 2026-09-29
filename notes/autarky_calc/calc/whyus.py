"""Re-run live v29 on our dragons at pocket mouths (reconstructed 7x7 input) to see why they did not enter."""
import sys, os
from common import *
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV
BIN = sys.argv[1]
CASES = [(625768, 105, 109), (625768, 111, 107), (625768, 79, 108), (625768, 171, 161), (625768, 171, 162), (625768, 186, 169),
         (612737, 35, 22), (612737, 35, 23), (617872, 249, 238), (617872, 249, 244), (608221, 35, 37), (625768, 69, 52)]
for gid, did, R0 in CASES:
    gm = [x for x in GAMES if x['gid'] == gid][0]
    g = sim(gid)
    r_from = max(g['born'].get(did, 0), R0 - 40)
    m, turns = BV.capture(gm['path'], did, r_from, R0)
    if not turns or turns[-1]['round'] != R0:
        print('skip', gid, did, R0); continue
    outs, dbg = BV.run_bot(BIN, did, turns)
    pr = BV.parse_last(dbg, R0)
    print('=== %d id%d r%d real=%s bot=%s' % (gid, did, R0, turns[-1].get('act'), outs[-1] if outs else None))
    if pr:
        for k, v in pr['cands'].items(): print('   cand %s t=%s pearls=%.2f area=%d depth=%d threat=%d score=%.2f' % (k, v['t'], v['pearls'], v['area'], v['depth'], v['threat'], v['score']))
        for l in pr['raw'].splitlines():
            if 'POCKET' in l or 'pump' in l.lower() or 'hold' in l.lower(): print('   ', l[:200])
        print('   ->', pr['arrow'][:3])
