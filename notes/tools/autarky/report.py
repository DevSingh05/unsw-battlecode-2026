"""Aggregate games.pkl into the notes/22 tables.  python3 report.py [section...]
sections: list tl eats splits deaths pump sprint"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, 'games.pkl'), 'rb'))
PHN = ['r0-59', 'r60-199', 'r200-349', 'r350-500']


def cls(r):
    if r['grp'] == 'us':
        if r['oppelo'] >= 1940: return 'us-L-strong' if not r['win'] else 'us-W-strong'
        return 'us-W-weak' if r['win'] else 'us-L-weak'
    if r['grp'] == 'opp':
        if r['elo'] >= 1940: return 'strong-W-vs-us' if r['win'] else 'strong-L-vs-us'
        return 'weak-vs-us'
    if r['grp'] == 'top':
        return 'top-W' if r['win'] else 'top-L'
    return 'topopp-W' if r['win'] else 'topopp-L'


GROUPS = ['us-L-strong', 'strong-W-vs-us', 'us-W-strong', 'us-W-weak', 'us-L-weak', 'top-W', 'top-L', 'topopp-L']
G = collections.defaultdict(list)
for r in R: G[cls(r)].append(r)
sec = sys.argv[1:] or ['list', 'tl', 'eats', 'splits', 'deaths', 'pump', 'sprint']


def mean(xs): return sum(xs) / len(xs) if xs else float('nan')


if 'list' in sec:
    for g in GROUPS:
        print(g, len(G[g]), ' '.join(f"{r['gid']}:{r['oppname'][:10]}{'W' if r['win'] else 'L'}{r['last']}" for r in G[g][:40]))
if 'tl' in sec:
    print('\n== timeline units / total / longest (mean) ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        cells = []
        for t in (50, 100, 200, 300, 400, 500):
            cells.append('%4.1f/%5.1f/%4.1f' % tuple(mean([r['tl'][t][i] for r in rs]) for i in range(3)))
        print(f"{g:16s} n={len(rs):2d} " + ' | '.join(cells), ' elim%%=%.0f last=%.0f' % (100 * mean([r['end'] == 'teamEliminated' for r in rs]), mean([r['last'] for r in rs])))
if 'eats' in sec:
    print('\n== eats per game by phase: pocket(spawn+corpse) / open spawn / own corpse / enemy corpse ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        cells = []
        for p in range(4):
            def s(f): return mean([sum(v for k, v in r['eats'].items() if k[0] == p and f(k)) for r in rs])
            cells.append('pk%5.1f op%5.1f own%4.1f en%4.1f' % (s(lambda k: k[1] == 'pk'), s(lambda k: k[1] == 'open' and k[2] == 'spawn'),
                                                               s(lambda k: k[1] == 'open' and k[2] == 'own'), s(lambda k: k[1] == 'open' and k[2] == 'enemy')))
        tot = mean([sum(r['eats'].values()) for r in rs]); pk = mean([sum(v for k, v in r['eats'].items() if k[1] == 'pk') for r in rs])
        print(f"{g:16s} tot {tot:5.0f} pk {pk:5.0f} | " + ' | '.join(cells))
if 'splits' in sec:
    print('\n== splits per game by phase: 2-child open / 2-child low-exit / reverse(L-2) / other ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        cells = []
        for p in range(4):
            def s(f): return mean([sum(v for k, v in r['splits'].items() if k[0] == p and f(k)) for r in rs])
            cells.append('2o%5.1f 2p%5.1f rev%5.1f oth%4.1f' % (s(lambda k: k[1] == '2' and k[2] == 'open'), s(lambda k: k[1] == '2' and k[2] == 'pk'),
                                                               s(lambda k: k[1] == 'rev'), s(lambda k: k[1] == 'other')))
        print(f"{g:16s} " + ' | '.join(cells))
    print('split parent length histogram (all phases), share')
    for g in GROUPS:
        c = collections.Counter()
        for r in G[g]:
            for k, v in r['splits'].items():
                if k[1] == 'L': c[min(k[2], 10)] += v
        n = sum(c.values()) or 1
        print(f"{g:16s} n/g={n / max(1, len(G[g])):5.1f} " + ' '.join(f"L{k}:{100 * v / n:.0f}%" for k, v in sorted(c.items())))
if 'deaths' in sec:
    print('\n== deaths per game by phase and cause ==')
    CA = ['rammed_enemy', 'rammed_by_enemy', 'h2h_ally', 'body_enemy', 'body_ally', 'self', 'wall', 'nva', 'trapped', 'inpk']
    for p in range(4):
        print(' ', PHN[p], '  '.join(CA))
        for g in GROUPS:
            rs = G[g]
            if not rs: continue
            print(f"  {g:16s} " + ' '.join('%6.1f' % mean([r['deaths'].get((p, c), 0) for r in rs]) for c in CA),
                  ' lenlost %5.1f' % mean([sum(v for k, v in r['dlen'].items() if k[0] == p and k[1] != 'inpk') for r in rs]))
    print('death length histogram r60-349 (share)')
    for g in GROUPS:
        c = collections.Counter()
        for r in G[g]:
            for k, v in r['deaths'].items():
                if k[0] in (1, 2) and k[1] == 'L': c[k[2]] += v
        n = sum(c.values()) or 1
        print(f"{g:16s} n/g={n / max(1, len(G[g])):5.1f} " + ' '.join(f"L{k}:{100 * v / n:.0f}%" for k, v in sorted(c.items())))
if 'pump' in sec:
    print('\n== pocket episodes (head enters pocket), r0-500, per game ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        eps = [e for r in rs for e in r['episodes']]
        n = len(rs)
        oc = collections.Counter(e['out'] for e in eps)
        pumps = [e for e in eps if e['out'] == 'pump']
        died = [e for e in eps if e['out'] == 'died']
        exits = [e for e in eps if e['out'] == 'exit']
        # net: pump -> child k - L0 ; died -> -L0 ; exit -> L1 - L0
        net = [e['k'] - e['L0'] for e in pumps] + [-e['L0'] for e in died] + [e['L1'] - e['L0'] for e in exits]
        pdL = collections.Counter(e['parent_death'][2] if e.get('parent_death') else 'alive' for e in pumps)
        rev = sum(1 for e in pumps if e['k'] == e['splitL'] - 2)
        print(f"{g:16s} eps/g {len(eps) / n:5.1f}  pump {oc['pump'] / n:5.1f} died {oc['died'] / n:5.1f} exit {oc['exit'] / n:5.1f} | entryL {mean([e['L0'] for e in eps]):.2f}"
              f" splitL {mean([e['splitL'] for e in pumps]):.2f} child {mean([e['k'] for e in pumps]):.2f} rev% {100 * rev / max(1, len(pumps)):.0f}"
              f" | net/ep {mean(net):+.2f} net/g {sum(net) / n:+5.1f} | rounds/ep {mean([e['r1'] - e['r0'] for e in eps if 'r1' in e]):.1f}")
        print(f"{'':16s}   pump parent death len {dict(pdL.most_common(6))}  died reasons {collections.Counter(e['dreason'] for e in died).most_common(5)}  diedL {mean([e['dL'] for e in died]):.2f}")
        print(f"{'':16s}   entry: enemy head dist<=3 {100 * mean([e['en'] <= 3 for e in eps]):.0f}%  own inside {mean([e['own_in'] for e in eps]):.2f}  enemy inside {mean([e['en_in'] for e in eps]):.2f}")
        # by phase
        cells = []
        for p, (a, b) in enumerate([(0, 59), (60, 199), (200, 349), (350, 500)]):
            ee = [e for e in eps if a <= e['r0'] <= b]
            nn = [x for e, x in zip(pumps + died + exits, net) if a <= e['r0'] <= b]
            cells.append(f"{PHN[p]} eps {len(ee) / n:4.1f} net {sum(nn) / n:+5.1f}")
        print(f"{'':16s}   " + ' | '.join(cells))
if 'sprint' in sec:
    print('\n== sprints per game (kill / eat / other) by phase ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        print(f"{g:16s} " + ' | '.join('%4.1f/%4.1f/%4.1f' % tuple(mean([r['sprints'].get((p, k), 0) for r in rs]) for k in ('kill', 'eat', 'other')) for p in range(4)))
if 'pockets' in sec:
    print('\n== per pocket: eats per game (home pockets = 2 at own L14 start column / away) and head-occupancy rounds ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        cells = []
        for p in range(4):
            he = mean([sum(v for k, v in r['pk_by_pocket'].items() if k[0] == p and k[1] in r.get('home', [])) for r in rs])
            ae = mean([sum(v for k, v in r['pk_by_pocket'].items() if k[0] == p and k[1] not in r.get('home', [])) for r in rs])
            ho = mean([sum(v for k, v in r['pk_occ'].items() if k[0] == p and k[1] in r.get('home', [])) for r in rs])
            ao = mean([sum(v for k, v in r['pk_occ'].items() if k[0] == p and k[1] not in r.get('home', [])) for r in rs])
            cells.append(f"home {he:5.1f}e/{ho:5.1f}r away {ae:5.1f}e/{ao:5.1f}r")
        print(f"{g:16s} " + ' | '.join(cells))
if 'rams' in sec:
    print('\n== rammed by enemy (our dragon killed head-on, enemy moved): per game; local odds from previous round heads within Cheb 3 ==')
    for g in GROUPS:
        rs = G[g]
        if not rs: continue
        rl = [x for r in rs for x in r['rammed'] if not x['ally_kill']]
        n = len(rs)
        def pr(f): return 100 * mean([f(x) for x in rl]) if rl else float('nan')
        print(f"{g:16s} n/g {len(rl) / n:5.1f} victimL {mean([x['len'] for x in rl]):.2f} killerL {mean([x['killer_len'] or 0 for x in rl]):.2f}"
              f" | near pocket(d<=3) {pr(lambda x: x['dpk'] <= 3):3.0f}%  outnumbered(own<en) {pr(lambda x: x['own'] < x['en']):3.0f}% even {pr(lambda x: x['own'] == x['en']):3.0f}%"
              f" | age<=3 {pr(lambda x: x['age'] <= 3):3.0f}%")
if 'zone' in sec:
    print('\n== head-rounds per game by zone (pocket / mouth<=3 / centre x19-34 / side) and eats there (spawn+corpse) ==')
    Z = ['pocket', 'mouth', 'centre', 'side']
    for p in range(4):
        print(' ', PHN[p])
        for g in GROUPS:
            rs = G[g]
            if not rs: continue
            tot = [sum(v for k, v in r['zone'].items() if k[0] == p) for r in rs]
            cells = []
            for z in Z:
                hr = mean([r['zone'].get((p, z), 0) for r in rs]); sh = 100 * sum(r['zone'].get((p, z), 0) for r in rs) / max(1, sum(tot))
                es = mean([r['zone_eats'].get((p, z, 's'), 0) for r in rs]); ec = mean([r['zone_eats'].get((p, z, 'c'), 0) for r in rs])
                cells.append(f"{z[:4]} {sh:3.0f}% e{es:5.1f}+{ec:4.1f}")
            print(f"  {g:16s} " + ' | '.join(cells))
if 'pergame' in sec:
    print('\n== per game (us vs opp): r100/r200 units, r60-199 pocket eats us/them, rams r0-199 (we rammed / they rammed us), pump eps us/them, net pump us/them ==')
    by = collections.defaultdict(dict)
    for r in R:
        if r['grp'] in ('us', 'opp'): by[r['gid']][r['grp']] = r
    for gid, d in sorted(by.items(), key=lambda kv: (kv[1]['us']['win'], -kv[1]['opp']['elo'])):
        u, o = d['us'], d['opp']
        def pk(r, a, b): return sum(v for k, v in r['eats'].items() if k[1] == 'pk' and a <= k[0] <= b)
        def rams(r): return sum(r['deaths'].get((p, 'rammed_enemy'), 0) for p in (0, 1))
        def eps(r): return len([e for e in r['episodes'] if e['r0'] < 200])
        def net(r): return sum((e['k'] - e['L0']) if e['out'] == 'pump' else (-e['L0'] if e['out'] == 'died' else e['L1'] - e['L0']) for e in r['episodes'] if e['r0'] < 200)
        print(f"{gid} {o['name'][:14]:14s} {o['elo']} {'W' if u['win'] else 'L'} r{u['last']:3d} {u['end'][:5]} | u r100 {u['tl'][100][0]:2d}/{o['tl'][100][0]:2d} r200 {u['tl'][200][0]:2d}/{o['tl'][200][0]:2d} tot200 {u['tl'][200][1]:3d}/{o['tl'][200][1]:3d}"
              f" | pk0-59 {pk(u,0,0):3d}/{pk(o,0,0):3d} pk60-199 {pk(u,1,1):3d}/{pk(o,1,1):3d} | rams {rams(u):2d}/{rams(o):2d} | eps {eps(u):3d}/{eps(o):3d} net {net(u):+4d}/{net(o):+4d} | final max {u['tl'][500][2]}/{o['tl'][500][2]}")
if 'ledger' in sec:
    print('\n== length ledger per game, r60-199 and r200-349: + pocket eats, + open spawn, + own corpse, + enemy corpse, - in-pocket deaths, - ram deaths (both kinds), - other deaths = net ==')
    for p in (1, 2):
        print(' ', PHN[p])
        for g in GROUPS:
            rs = G[g]
            if not rs: continue
            def e(f): return mean([sum(v for k, v in r['eats'].items() if k[0] == p and f(k)) for r in rs])
            pk = e(lambda k: k[1] == 'pk'); sp = e(lambda k: k[1] == 'open' and k[2] == 'spawn'); oc = e(lambda k: k[1] == 'open' and k[2] == 'own'); ec = e(lambda k: k[1] == 'open' and k[2] == 'enemy')
            lp = mean([r['dlen'].get((p, 'inpk'), 0) for r in rs])
            lr = mean([r['dlen'].get((p, 'rammed_enemy'), 0) + r['dlen'].get((p, 'rammed_by_enemy'), 0) for r in rs])
            la = mean([sum(v for k, v in r['dlen'].items() if k[0] == p and k[1] != 'inpk') for r in rs])
            # ram deaths inside pockets are rare; other = all - rams - inpk (approx)
            lo = la - lr - lp
            print(f"  {g:16s} +pk {pk:5.1f} +sp {sp:5.1f} +own {oc:5.1f} +en {ec:5.1f} | -pk {lp:5.1f} -ram {lr:5.1f} -oth {lo:5.1f} | net {pk + sp + oc + ec - la:+6.1f}")
