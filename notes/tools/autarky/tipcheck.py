"""Re-run v28 and v28+PUMP_TIP_SPLIT on the real in-pocket L4 split decisions of our divers (Autarky).
    python3 tipcheck.py BIN_BASE BIN_FLAG [N=30]
Prints per case: tile, whether a pearl lies on the next pocket tile, base output, flag output."""
import os, sys, pickle, random, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import sim2, collect, botview as BV
b0, b1 = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 30
R = pickle.load(open(os.path.join(H, 'games.pkl'), 'rb')); paths = {g['gid']: g['path'] for g in collect.games()}
cases = []
for r in R:
    if r['grp'] != 'us': continue
    S = sim2.simulate(paths[r['gid']]); m = S['map']; PK = collect.pockets(m)
    heads = {}
    for x in S['moves']:
        if x.get('head_after'): heads[(x['id'], x['round'])] = x['head_after']
    for s in S['splits']:
        if s['team'] != r['T'] or s['L'] != 4 or s['round'] < 20: continue
        h = heads.get((s['parent'], s['round'] - 1))
        if h in PK: cases.append((r['gid'], s['parent'], s['round'], h))
random.seed(2); random.shuffle(cases)
c = collections.Counter()
for gid, i, rnd, h in cases[:N]:
    m, turns = BV.capture(paths[gid], i, rnd - 30, rnd)
    if not turns or turns[-1]['round'] != rnd: continue
    o0, _ = BV.run_bot(b0, i, turns); o1, _ = BV.run_bot(b1, i, turns)
    a0 = o0[-1] if o0 else None; a1 = o1[-1] if o1 else None
    c[(a0.split()[0] if a0 else None, a1.split()[0] if a1 else None)] += 1
    print(gid, i, rnd, h, 'base', a0, '| tip', a1, flush=True)
print(c)
