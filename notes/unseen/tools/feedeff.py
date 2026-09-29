#!/usr/bin/env python3
"""Endgame feeding efficiency (notes/unseen/endgame-king.md).

For every round-limit team-game in our replays (v19plus + ab_v2*) and the top-10 sample
(notes/replays/top10b, 'top' group), look at every own-team death from r250 on
(except deaths of the final-king lineage) and follow its corpse pearls:
who ate each pearl (final king / other ally / enemy / nobody within 25 rounds) and how fast.
Also records the feeder's length, how it died, where it died relative to the king head and
facing (the team's longest dragon at the time), and the king-growth curve.

usage: python3 feedeff.py [jobs]   -> feedeff.pkl next to this file, then prints tables
"""
import collections, glob, json, os, pickle, sys
from multiprocessing import Pool

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/top10b'))
from sim2 import simulate  # noqa
import replay_decode as RD  # noqa
TOP10 = {306, 70, 264, 801, 20, 46, 91, 213, 249, 470}
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def games():
    out = []
    led = os.path.join(ROOT, 'replays/v19plus/ledger.json')
    seen = set()
    if os.path.exists(led):
        for x in json.load(open(led)):
            p = os.path.join(ROOT, f"replays/v19plus/{x['game']}.replay")
            if os.path.exists(p):
                out.append((p, x['side'], 'us', x['map'])); seen.add(x['game'])
    for d in sorted(glob.glob(os.path.join(ROOT, 'replays/ab_v2*/summary.json'))):
        for g in json.load(open(d)):
            if g['id'] in seen: continue
            p = os.path.join(os.path.dirname(d), '%d.replay' % g['id'])
            if not os.path.exists(p): continue
            res = RD.load(p)['result']
            out.append((p, 'A' if res['A'] == g['us'] else 'B', 'us', g['map'])); seen.add(g['id'])
    for m in json.load(open(os.path.join(ROOT, 'notes/replays/top10b/index.json'))):
        p = os.path.join(ROOT, f"notes/replays/top10b/{m['id']}.replay")
        if not os.path.exists(p): continue
        for s, T in (('a', 'A'), ('b', 'B')):
            if m[s]['id'] in TOP10:
                out.append((p, T, 'top', m['mapName']))
    return out


def rel(m, king_head, king_neck, tile):
    """(forward, right) of tile relative to king head, facing = head - neck (wrapped)."""
    def d(a, b, n):
        v = (b - a) % n
        return v - n if v > n // 2 else v
    fx, fy = d(king_neck[0], king_head[0], m.w), d(king_neck[1], king_head[1], m.h)
    if abs(fx) + abs(fy) != 1:
        return None  # portal between head and neck
    dx, dy = d(king_head[0], tile[0], m.w), d(king_head[1], tile[1], m.h)
    fwd = dx * fx + dy * fy
    right = dx * (-fy) + dy * fx  # facing N (0,-1): right = +x
    return fwd, right


def work(job):
    path, T, grp, mp = job
    try:
        g = simulate(path)
    except Exception as ex:  # noqa
        return None
    if g['result'].get('endReason') != 'roundLimit':
        return None
    m = g['map']; rounds = dict(g['rounds']); last = g['last_round']
    fin = rounds[last][T]
    if not fin['ids']:
        return None
    k = max(fin['ids'], key=lambda j: (fin['ids'][j], -j))
    lineage = {k}; cur = k
    while cur in g['parent_of']:
        p = g['parent_of'][cur]
        sp = [s for s in g['splits'] if s['child'] == cur]
        if sp and sp[0]['k'] > sp[0]['L'] - sp[0]['k']:
            lineage.add(p); cur = p
        else:
            break
    E = 'B' if T == 'A' else 'A'
    curve = {}
    for r in (200, 250, 300, 350, 400, 450, 500):
        s = rounds.get(min(r, last))
        curve[r] = (max((s[T]['ids'].get(j, 0) for j in lineage), default=0), s[T]['max'], s[E]['max'], s[T]['n'], s[T]['total'])
    # eaters of each corpse pearl
    eat_by = collections.defaultdict(list)  # corpse id -> [(round, eater group)]
    for e in g['eats']:
        if e['corpse'] and e['corpse'][1] == T:
            who = 'king' if e['id'] in lineage else ('ally' if e['team'] == T else 'enemy')
            eat_by[e['corpse'][0]].append((e['round'], who))
    king_eats = collections.Counter()
    for e in g['eats']:
        if e['id'] in lineage and e['round'] >= 300:
            src = 'spawn' if not e['corpse'] else ('own' if e['corpse'][1] == T else 'enemy')
            king_eats[(e['round'] // 50 * 50, src)] += 1
    feeders = []
    for d in g['deaths']:
        if d['team'] != T or d['round'] < 250 or d['id'] in lineage:
            continue
        L = d['len']; drop = (L + 1) // 2
        eats = eat_by.get(d['id'], [])
        c = collections.Counter(w for r, w in eats if r - d['round'] <= 25)
        lag = sorted(r - d['round'] for r, w in eats if w == 'king')
        deliberate = d['actor'] == d['id'] and d['reason'] in ('HitSelf', 'NoValidAction', 'HitWall', 'HitOtherBody') and \
            any(v in ('free', 'pearl') for v in d.get('nbrs', {}).values())
        pos = None
        kinfo = d.get('king')
        if kinfo and kinfo[0] in lineage and len(d.get('king_head2', [])) == 2:
            pos = rel(m, d['king_head2'][0], d['king_head2'][1], d['head'])
        # alignment: how many of this corpse's pearl tiles lie within Manhattan 3 of the king head
        near3 = None
        if kinfo and kinfo[0] in lineage and d.get('king_head2'):
            kh = d['king_head2'][0]
            near3 = sum(1 for s in d['body'][::2] if m.dist(s, kh) <= 3)
        orient = None
        if kinfo and kinfo[0] in lineage and d.get('king_head2') and len(d['body']) >= 2:
            def dd(a, b, n):
                v = (b - a) % n
                return v - n if v > n // 2 else v
            kh, kn = d['king_head2']
            kf = (dd(kn[0], kh[0], m.w), dd(kn[1], kh[1], m.h))
            b0, b1 = d['body'][0], d['body'][1]
            ff = (dd(b1[0], b0[0], m.w), dd(b1[1], b0[1], m.h))
            if abs(kf[0]) + abs(kf[1]) == 1 and abs(ff[0]) + abs(ff[1]) == 1:
                dot = kf[0] * ff[0] + kf[1] * ff[1]
                orient = 'headon' if dot == -1 else 'same' if dot == 1 else 'perp'
        feeders.append(dict(orient=orient, round=d['round'], L=L, drop=drop, reason=d['reason'], deliberate=deliberate,
                            king_is_lineage=bool(kinfo and kinfo[0] in lineage), kdist=kinfo[2] if kinfo else None,
                            klen=kinfo[1] if kinfo else None, pos=pos, near3=near3,
                            king=c['king'], ally=c['ally'], enemy=c['enemy'], lag=lag,
                            enemy_dist=d.get('enemy_near', (0, 0, 99))[2]))
    return dict(path=path, T=T, grp=grp, map=mp, curve=curve, feeders=feeders, king_eats=dict(king_eats),
                win=(g['result'].get('winner') == T) if 'winner' in g['result'] else None)


def main():
    H = os.path.dirname(os.path.abspath(__file__))
    pk = os.path.join(H, 'feedeff.pkl')
    if not os.path.exists(pk) or '--redo' in sys.argv:
        jobs = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 4
        G = games()
        with Pool(jobs) as P:
            res = [r for r in P.map(work, G, chunksize=2) if r]
        pickle.dump(res, open(pk, 'wb'))
    res = pickle.load(open(pk, 'rb'))
    report(res)


def report(res):
    for grp in ('top', 'us'):
        R = [r for r in res if r['grp'] == grp]
        print(f'==== {grp}: {len(R)} round-limit team-games')
        # king curve (lineage length) medians
        import statistics as st
        for r in (300, 350, 400, 450, 500):
            ks = [x['curve'][r][0] for x in R]; em = [x['curve'][r][2] for x in R]
            n = [x['curve'][r][3] for x in R]
            print(f'  r{r}: king median {st.median(ks):.1f} mean {st.mean(ks):.1f} | enemy longest mean {st.mean(em):.1f} | units mean {st.mean(n):.1f}')
        F = [f for x in R for f in x['feeders']]
        print(f'  own deaths r250+ (non-king): {len(F)} = {len(F)/len(R):.1f}/game')
        # by length bucket: yield to king
        def b(L): return 'L2' if L == 2 else 'L3' if L == 3 else 'L4-6' if L <= 6 else 'L7-10' if L <= 10 else 'L11+'
        tab = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0])
        for f in F:
            t = tab[b(f['L'])]
            t[0] += 1; t[1] += f['drop']; t[2] += f['king']; t[3] += f['ally']; t[4] += f['enemy']; t[5] += f['L']
        print('  len   deaths/g  drop  ->king  ->ally  ->enemy  king/drop  king/length')
        for key in ('L2', 'L3', 'L4-6', 'L7-10', 'L11+'):
            t = tab[key]
            if not t[0]: continue
            print(f'  {key:5s} {t[0]/len(R):7.2f} {t[1]:5d} {t[2]:6d} {t[3]:6d} {t[4]:6d}   {t[2]/t[1]:.2f}      {t[2]/t[5]:.2f}')
        # feeders = deaths with >=1 pearl to king
        FE = [f for f in F if f['king'] > 0]
        print(f'  feeders (>=1 pearl to king): {len(FE)/len(R):.1f}/game; king own-corpse pearls {sum(f["king"] for f in F)/len(R):.1f}/game')
        # position relative to king for feeders
        pc = collections.Counter(); pk_ = collections.Counter()
        for f in F:
            if f['pos'] is None or not f['king_is_lineage'] or f['kdist'] is None or f['kdist'] > 6: continue
            fw, rt = f['pos']
            cell = 'ahead' if fw > 0 and abs(rt) <= fw else 'behind' if fw < 0 and abs(rt) <= -fw else 'side'
            pc[cell] += f['drop']; pk_[cell] += f['king']
        print('  deaths within 6 of king, yield by cell:', {c: f'{pk_[c]}/{pc[c]}={pk_[c]/max(1,pc[c]):.2f}' for c in pc})
        dc = collections.Counter(); dk = collections.Counter()
        for f in F:
            if f['kdist'] is None or not f['king_is_lineage']: continue
            kd = min(f['kdist'], 9)
            dc[kd] += f['drop']; dk[kd] += f['king']
        print('  yield by king distance:', ' '.join(f'd{k}:{dk[k]}/{dc[k]}' for k in sorted(dc)))
        lags = [l for f in F for l in f['lag']]
        if lags:
            print(f'  king eat lag: median {st.median(lags)} p75 {sorted(lags)[3*len(lags)//4]}')
        # timing: own-corpse king eats per 50 rounds
        ke = collections.Counter()
        for x in R:
            for (r, s), v in x['king_eats'].items():
                ke[(r, s)] += v
        print('  king eats per game by 50r (spawn/own/enemy):', ' '.join(f"r{r}:{ke[(r,'spawn')]/len(R):.1f}/{ke[(r,'own')]/len(R):.1f}/{ke[(r,'enemy')]/len(R):.1f}" for r in range(300, 500, 50)))
        # enemy near at feeding
        en = [f for f in F if f['king'] > 0]
        if en:
            print(f'  feeders: enemy head dist median {st.median([f["enemy_dist"] for f in en])}, deliberate share {sum(f["deliberate"] for f in en)/len(en):.2f}')
        rs = collections.Counter(f['round'] // 50 * 50 for f in FE)
        print('  feeder deaths by 50r per game:', ' '.join(f'r{r}:{rs[r]/len(R):.1f}' for r in sorted(rs)))
        # deliberate deaths with 0 pearls to king (wasted suicides)
        W = [f for f in F if f['deliberate'] and f['king'] == 0]
        print(f'  deliberate deaths with 0 king pearls: {len(W)/len(R):.1f}/game (mean L {st.mean([f["L"] for f in W]) if W else 0:.1f})')
        oc = collections.defaultdict(lambda: [0, 0, 0, 0])
        for f in F:
            if f.get('orient') is None or f['kdist'] is None or f['kdist'] > 3 or not f['deliberate']: continue
            o = oc[(f['orient'], 'L2' if f['L'] == 2 else 'L3' if f['L'] == 3 else 'L4+')]
            o[0] += 1; o[1] += f['drop']; o[2] += f['king']; o[3] += f['ally']
        print('  deliberate deaths within 3 of king by feeder orientation (n, drop, ->king, ->ally):')
        for k_ in sorted(oc): print('    ', k_, oc[k_], f"yield {oc[k_][2]/max(1,oc[k_][1]):.2f}")
        # near3 alignment vs yield
        a = collections.defaultdict(lambda: [0, 0])
        for f in F:
            if f['near3'] is None: continue
            frac = f['near3'] / f['drop']
            key = 'all<=3' if frac == 1 else 'some' if f['near3'] else 'none'
            a[key][0] += f['drop']; a[key][1] += f['king']
        print('  corpse pearls within 3 of king head at death -> yield:', {k: f'{v[1]}/{v[0]}={v[1]/max(1,v[0]):.2f}' for k, v in a.items()})


if __name__ == '__main__':
    main()
