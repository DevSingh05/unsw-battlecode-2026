"""Rams on L>=10 dragons: rammer team/len/steps, rammer distance to victim head 1/3/5/10 rounds before, victim moves in the
previous 3 rounds (did it approach?), rammer id vs victim id (turn order), number of rammer-team heads within 5 of victim at r-1.
Usage: python3 bigrams.py U,SFu,US"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(',')
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want: bypath[r['path']].append(r)
for p, rs in sorted(bypath.items()):
    if not any(sum(r.get(f'rammedbig{i}', 0) for i in range(5)) for r in rs): continue
    g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
    mv = {(a['round'], a['id']): a for a in g['moves']}
    for r in rs:
        T = r['T']; E = 'B' if T == 'A' else 'A'
        for d in g['deaths']:
            if d['team'] != T or d['len'] < 10 or d['reason'] != 'HitHeadToHead' or d.get('killer_team') != E: continue
            k = d['killer']; a = mv.get((d['round'], k))
            hist = []
            for back in (1, 3, 5, 10):
                s = RS.get(d['round'] - back)
                if s and k in s['heads'] and d['id'] in s['heads']: hist.append(m.dist(s['heads'][k][0], s['heads'][d['id']][0]))
                else: hist.append(None)
            s = RS.get(d['round'] - 1)
            en5 = sum(1 for j, (h, L, t) in s['heads'].items() if t == E and m.dist(h, d['head']) <= 5) if s else -1
            own5 = sum(1 for j, (h, L, t) in s['heads'].items() if t == T and j != d['id'] and m.dist(h, d['head']) <= 5) if s else -1
            vm = [mv.get((d['round'] - b, d['id'])) for b in (0, 1, 2)]
            vmoves = ['' if x is None else ''.join(x['act'].get('move', ['split'] if 'split' in x['act'] else ['?'])) for x in vm]
            print(f"{r['grp']:4s} {r['gid']} {r['map'][:8]:8s} r{d['round']} victim L{d['len']} id{d['id']} | rammer L{d.get('killer_len')} id{k} steps{a['steps'] if a else '?'} {'LATER' if k > d['id'] else 'earlier'} | dist r-1,3,5,10 {hist} | enemy heads<=5 {en5} own {own5} | victim moves r0,-1,-2 {vmoves} free {sum(1 for v in d['nbrs'].values() if v in ('free','pearl'))}")
