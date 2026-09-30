"""Own-corpse pipeline into big dragons (round-limit games, r200+).
For every own death with L<=6 at r>=200: reason, distance (Manhattan) from its head to the nearest own L>=10 head,
free neighbours at death, and how many of its pearls were eaten by an own L>=10 dragon (and within how many rounds).
Also: for each own-corpse pearl eaten by a big, the dead dragon's distance to that eater at death.
Usage: python3 feedpipe.py SFu,U [maps]"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',') if len(sys.argv) > 1 else ['SFu', 'U']
MAPS = sys.argv[2].split(',') if len(sys.argv) > 2 else None
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and r['end'] == 'roundLimit' and (MAPS is None or r['map'] in MAPS): bypath[r['path']].append(r)
A = collections.defaultdict(collections.Counter); ng = collections.Counter(); lagl = collections.defaultdict(list)
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    for r in rs:
        T = r['T']; ng[r['grp']] += 1; C = A[r['grp']]
        # pearl -> death record
        drops = {}
        for d in g['deaths']:
            if d['team'] != T or d['round'] < 200 or d['len'] > 6: continue
            s = RS.get(d['round'] - 1)
            bigs = [(m.dist(d['head'], h), j) for j, (h, L, t) in s['heads'].items() if t == T and L >= 10 and j != d['id']] if s else []
            dist = min(bigs)[0] if bigs else 99
            b = 'd<=2' if dist <= 2 else ('d3-6' if dist <= 6 else ('d7-15' if dist <= 15 else 'd>15'))
            rs_ = d['reason']
            C[('death', b)] += 1
            C[('deathreason', b, rs_)] += 1
            C[('deathlen', b, d['len'])] += 1
            for sgm in d['body'][::2]: drops[sgm] = (d['round'], b, d['id'])
        for e in g['eats']:
            if e['team'] != T or not e['corpse'] or e['corpse'][1] != T: continue
            if e['tile'] in drops and drops[e['tile']][2] == e['corpse'][0]:
                rd, b, _ = drops.pop(e['tile'])
                big = e['len'] is not None and e['len'] >= 10
                C[('pearl_eaten', b, 'big' if big else 'small')] += 1
                if big: lagl[(r['grp'], b)].append(e['round'] - rd)
        for t_, (rd, b, _) in drops.items(): C[('pearl_uneaten', b)] += 1
for gname in want:
    print('==', gname, ng[gname], 'team-games (per game)')
    C = A[gname]
    for b in ('d<=2', 'd3-6', 'd7-15', 'd>15'):
        n = C[('death', b)]
        rsn = {k[2]: round(v / ng[gname], 1) for k, v in C.items() if k[0] == 'deathreason' and k[1] == b}
        lns = {k[2]: round(v / ng[gname], 1) for k, v in C.items() if k[0] == 'deathlen' and k[1] == b}
        lg = lagl.get((gname, b), [])
        print(f'  {b:6s} deaths {n/ng[gname]:5.1f}  pearls->big {C[("pearl_eaten", b, "big")]/ng[gname]:5.1f}  ->small {C[("pearl_eaten", b, "small")]/ng[gname]:5.1f}  uneaten {C[("pearl_uneaten", b)]/ng[gname]:5.1f}  lag med {st.median(lg) if lg else 0}')
        print('        reasons', rsn, ' lens', dict(sorted(lns.items())))
