#!/usr/bin/env python3
"""Big-board study (notes/23). Read-only over replays.

    python3 notes/tools/bigboard/collect.py [--jobs 4]     # -> notes/tools/bigboard/games.pkl

Game set: replays/auto/games + replays/v28 ledgers (deduped). Every game is kept; `top` marks
opponents that were top-15 when auto_challenge launched a series against them (launched.jsonl rank<=15).

Per game and team (us/them):
  tl        per-round (units, total, max)
  eats      Counter[(phase100, zone, src)]   zone = home/mid/far from BFS distance to each team's starts
  terr      {round: (tile_share, income_share, cover3)} every 25 rounds (head Voronoi over the portal graph)
  zonefrac  {round: (home, mid, far)} fraction of our heads in each zone
  deaths    list of (round, len, cls, zone)
  splits    Counter[phase100]
Zones: rel = (dOpp - dOwn) / (dOpp + dOwn) over BFS distance from the starting heads; home rel>0.2, far rel<-0.2.
Income weights = spawns actually seen on each tile in this game (non-corpse pearl appearances).
"""
import collections, json, os, pickle, sys
from multiprocessing import Pool
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate

TERR_EVERY = 25


def top_teams():
    top = {}
    for l in open(os.path.join(ROOT, 'replays/auto/launched.jsonl')):
        d = json.loads(l)
        if d.get('rank', 99) <= 15:
            top.setdefault(d['team'], d['rank'])
    return top


def games():
    G = {}
    # BB_DIRS=replays/ab_x,... to measure an A/B batch (each dir needs ledger.json with game/side/opp/map/win)
    dirs = os.environ.get('BB_DIRS', 'replays/auto/games,replays/v28').split(',')
    for p in dirs:
        for g in json.load(open(os.path.join(ROOT, p, 'ledger.json'))):
            path = os.path.join(ROOT, p, '%d.replay' % g['game'])
            if os.path.exists(path):
                G[g['game']] = dict(g, path=path)
    top = top_teams()
    for g in G.values():
        g['top'] = g['opp'] in top or os.environ.get('BB_ALL_TOP') == '1'
    return sorted(G.values(), key=lambda g: g['game'])


def bfs(m, srcs):
    """multi-source BFS over the portal graph; srcs = list of (tile, label). returns dist, label-set per tile"""
    dist = {}; lab = {}
    q = collections.deque()
    for t, l in srcs:
        if t in dist:
            if dist[t] == 0: lab[t].add(l)
            continue
        dist[t] = 0; lab[t] = {l}; q.append(t)
    while q:
        t = q.popleft()
        for d in 'NESW':
            n = m.step(t, d)
            if n is None: continue
            if n not in dist:
                dist[n] = dist[t] + 1; lab[n] = set(lab[t]); q.append(n)
            elif dist[n] == dist[t] + 1:
                lab[n] |= lab[t]
    return dist, lab


def classify(m, d):
    if d['actor'] != d['id']:
        if d['reason'] == 'HitHeadToHead':
            return 'rammed_' + ('ally' if d.get('killer_team') == d['team'] else 'enemy')
        return 'killed_other'
    mv = d.get('move') or ''
    k = d.get('step_failed', 1) - 1
    crossed = bool(mv) and k < len(mv) and m.edges.get(m.side_edge(d['head'], mv[k]), (0, -1))[0] == 2
    r = d['reason']
    if r == 'HitHeadToHead':
        return ('portal_' if crossed else '') + 'ram_' + ('ally' if d.get('victim_team') == d['team'] else 'enemy')
    if r == 'NoValidAction': return 'nva'
    if r == 'HitWall': return 'wall'
    hit = d.get('hit')
    what = 'self' if r == 'HitSelf' else ('ally' if hit and hit['team'] == d['team'] else ('enemy' if hit else 'other'))
    if crossed: return 'portal_' + what
    free = [x for x, v in (d.get('nbrs') or {}).items() if v in ('free', 'pearl')]
    if not free: return 'trapped_' + what
    kg = d.get('king')
    if kg and kg[1] > d['len'] and kg[2] <= 4: return 'feed_' + what
    return 'chose_' + what


def analyse(g):
    G = simulate(g['path'])
    m = G['map']
    us = g['side']; them = 'B' if us == 'A' else 'A'
    tiles = []
    # all tiles reachable from any start
    starts = {'A': [], 'B': []}
    for i, (t, pts) in enumerate(m.dragons):
        starts['AB'[t]].append(pts[0])
    dA, _ = bfs(m, [(p, 'A') for p in starts['A']])
    dB, _ = bfs(m, [(p, 'B') for p in starts['B']])
    reach = [t for t in dA if t in dB] or list(dA)
    dOwn = {'A': dA, 'B': dB}
    Dmax = {T: max(dOwn[T].values()) for T in 'AB'}
    zone = {}
    for t in set(dA) | set(dB):
        a = dA.get(t, 999); b = dB.get(t, 999)
        rel = (b - a) / max(1, a + b)          # >0: nearer A
        zone[t] = {'A': 'home' if rel > 0.2 else ('far' if rel < -0.2 else 'mid'),
                   'B': 'home' if rel < -0.2 else ('far' if rel > 0.2 else 'mid')}
    # empirical spawn income
    spawns = collections.Counter(t for (r, t, c) in G['appears'] if not c)
    tot_sp = sum(spawns.values()) or 1
    # income per zone (from A's frame)
    inc_zone = collections.Counter()
    for t, c in spawns.items():
        inc_zone[zone.get(t, {'A': 'mid'})['A']] += c
    rs = dict(G['rounds'])
    last = G['last_round']
    out = {'game': g['game'], 'map': g['map'], 'w': m.w, 'h': m.h, 'win': g['win'], 'opp': g['opp'], 'oppElo': g.get('oppElo'),
           'ranked': g['ranked'], 'top': g['top'], 'side': us, 'at': g['at'], 'end': G['result'].get('endReason'), 'last': last,
           'result': G['result'], 'ntiles': len(reach), 'spawns': tot_sp,
           'inc_zone_A': dict(inc_zone),
           'Dmax': Dmax, 'start_dist': min((dA.get(p, 999) for p in starts['B']), default=999),
           'start_len': {T: sum(len(pts) for (t, pts) in m.dragons if 'AB'[t] == T) for T in 'AB'}}
    # territory samples
    terr = {}; zonefrac = {}
    for r in range(TERR_EVERY, last + 1, TERR_EVERY):
        s = rs.get(r)
        if not s: continue
        heads = s['heads']
        srcs = [(h[0], h[2]) for j, h in heads.items()]
        if not srcs: continue
        dist, lab = bfs(m, srcs)
        share = {'A': 0.0, 'B': 0.0}; ish = {'A': 0.0, 'B': 0.0}
        for t, L in lab.items():
            w = 1.0 / len(L)
            for T in L:
                share[T] += w; ish[T] += w * spawns.get(t, 0)
        n = sum(share.values()) or 1
        # cover: tiles within Chebyshev 3 of a head of team T
        cov = {}
        for T in 'AB':
            c = set()
            for j, h in heads.items():
                if h[2] != T: continue
                x, y = h[0]
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        c.add(((x + dx) % m.w, (y + dy) % m.h))
            cov[T] = len(c) / (m.w * m.h)
        terr[r] = {T: (share[T] / n, ish[T] / tot_sp, cov[T]) for T in 'AB'}
        zf = {}
        for T in 'AB':
            hz = collections.Counter(zone.get(h[0], {T: 'mid'})[T] for j, h in heads.items() if h[2] == T)
            nn = sum(hz.values()) or 1
            zf[T] = (hz['home'] / nn, hz['mid'] / nn, hz['far'] / nn, sum(hz.values()))
        zonefrac[r] = zf
        # mean head distance from own starts / Dmax (expansion) and mean nearest-own-head distance (spread)
        for T in 'AB':
            hs = [h[0] for j, h in heads.items() if h[2] == T]
            if hs:
                ex = sum(dOwn[T].get(p, 0) for p in hs) / len(hs) / max(1, Dmax[T])
                nn = [min(m.dist(p, q) for q in hs if q != p) for p in hs] if len(hs) > 1 else [0]
                zf[T] = zf[T] + (ex, sum(nn) / len(nn))
            else:
                zf[T] = zf[T] + (0, 0)
    # mean distance of heads to own nearest start (expansion) at samples
    for tag, T in (('us', us), ('them', them)):
        tl = []
        for r in range(1, last + 1):
            s = rs.get(r)
            tl.append((s[T]['n'], s[T]['total'], s[T]['max']) if s else (0, 0, 0))
        eats = collections.Counter()
        for e in G['eats']:
            if e['team'] != T: continue
            z = zone.get(e['tile'], {T: 'mid'})[T]
            if e['corpse']:
                src = 'own' if e['corpse'][1] == T else 'enemy'
            else:
                src = 'spawn'
            near = dOwn[T].get(e['tile'], 999) <= 0.25 * Dmax[T]
            eats[(min(4, e['round'] // 100), z, src, near)] += 1
        deaths = []
        for d in G['deaths']:
            if d['team'] != T: continue
            deaths.append((d['round'], d['len'], classify(m, d), zone.get(d['head'], {T: 'mid'})[T], d['age'],
                           dOwn[T].get(d['head'], 999) <= 0.25 * Dmax[T]))
        splits = collections.Counter()
        for s in G['splits']:
            if s['team'] == T:
                splits[(min(4, s['round'] // 100), 'norm' if s['k'] <= 3 and s['L'] <= 6 else 'big')] += 1
        out[tag] = {'T': T, 'tl': tl, 'eats': eats, 'deaths': deaths, 'splits': splits,
                    'terr': {r: v[T] for r, v in terr.items()}, 'zonefrac': {r: v[T] for r, v in zonefrac.items()},
                    'final': G['result'].get(T)}
    return out


def safe(g):
    try:
        return analyse(g)
    except Exception as ex:
        print('ERR', g['game'], ex, file=sys.stderr)
        return None


if __name__ == '__main__':
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 4
    gs = games()
    with Pool(jobs) as p:
        res = [r for r in p.imap(safe, gs, chunksize=4) if r]
    pickle.dump(res, open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'wb'))
    print(len(res), 'games')
