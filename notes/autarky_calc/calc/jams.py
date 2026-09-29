from common import *
import sys
gid = int(sys.argv[1]); side = sys.argv[2]  # 'C' or 'O'
gm = [x for x in GAMES if x['gid'] == gid][0]; g = sim(gid)
T = gm['calc'] if side == 'C' else ('B' if gm['calc'] == 'A' else 'A')
K = int(sys.argv[3]) if len(sys.argv) > 3 else 4
runs = {}
for r, S in g['rounds']:
    for p in range(4):
        ins = [j for j, bd in S['bodies'].items() if any(pocket_of(s) == p for s in bd)]
        near = [j for j, (h, L, t) in S['heads'].items() if t == T and pocket_of(h) is None and mdist(h, MOUTH[p]) <= 3]
        pe = sum(1 for t in S['pearls'] if pocket_of(t) == p)
        mine_in = [j for j in ins if S['heads'][j][2] == T]
        en_in = [j for j in ins if S['heads'][j][2] != T]
        if len(near) >= K and not mine_in:
            print('r%d pocket%d near=%d pearls=%d enemy_in=%s' % (r, p, len(near), pe, en_in))
