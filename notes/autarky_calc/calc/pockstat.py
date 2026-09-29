from common import *
import collections
W = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 400), (400, 500)]
PKT = pockets()
def run(gm):
    g = sim(gm['gid']); c = gm['calc']; o = 'B' if c == 'A' else 'A'
    out = {}
    for (a, b) in W:
        acc = collections.defaultdict(float); n = 0
        for r, S in g['rounds']:
            if not (a <= r < b): continue
            n += 1
            heads = S['heads']
            for T, tag in ((c, 'C'), (o, 'O')):
                for p in range(4):
                    ins = sum(1 for j, (h, L, t) in heads.items() if t == T and pocket_of(h) == p)
                    near = sum(1 for j, (h, L, t) in heads.items() if t == T and pocket_of(h) is None and mdist(h, MOUTH[p]) <= 3)
                    acc[tag + 'in'] += ins; acc[tag + 'near'] += near
                    if ins == 0 and near >= 3: acc[tag + 'jam3'] += 1
                    # segs in pocket
                    acc[tag + 'segin'] += sum(1 for j, bd in S['bodies'].items() if S['heads'][j][2] == T for s in bd if pocket_of(s) == p)
            for p in range(4):
                acc['pearls'] += sum(1 for t in S['pearls'] if pocket_of(t) == p)
                acc['idle'] += all(pocket_of(S['heads'][j][0]) != p and not any(pocket_of(s) == p for s in S['bodies'][j]) for j in S['heads'])
        # eats in pockets
        for e in g['eats']:
            if a <= e['round'] < b and pocket_of(e['tile']) is not None:
                acc[('C' if e['team'] == c else 'O') + 'peat'] += 1
        out[(a, b)] = {k: (v / n if k not in ('Cpeat', 'Opeat') else v) for k, v in acc.items()} if n else {}
    return out
print('per window: heads in pockets (sum 4 pockets), heads within 3 of mouths, rounds*pockets with >=3 near & 0 in, pearls waiting in pockets, pocket eats; calc | opp')
for gm in GAMES:
    o = run(gm)
    print(gm['gid'], gm['opp'])
    for k, v in o.items():
        if not v: continue
        print('  r%3d-%3d  in %.1f|%.1f  near %.1f|%.1f  jam %.2f|%.2f  segin %.1f|%.1f  pearlsWaiting %.1f idle %.2f  eats %d|%d' % (k[0], k[1], v.get('Cin',0), v.get('Oin',0), v.get('Cnear',0), v.get('Onear',0), v.get('Cjam3',0), v.get('Ojam3',0), v.get('Csegin',0), v.get('Osegin',0), v.get('pearls',0), v.get('idle',0), v.get('Cpeat', 0), v.get('Opeat', 0)))
