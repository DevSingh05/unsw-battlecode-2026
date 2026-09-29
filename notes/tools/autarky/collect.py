"""Autarky: per (game, team) metrics for our v28 games and fresh top-10 games.
Writes notes/tools/autarky/games.pkl (list of dicts). Read-only over replays.
Groups:  us (our side), opp (their side) for replays/auto + replays/v28 ledgers (Autarky only);
         top / topopp for notes/replays/autarky (fresh top-10 fetch) and notes/replays/{top10b,midgame} (28 Sep).
"""
import os, sys, json, pickle, collections
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, os.path.join(H, '..'))
import sim2

TOP10 = {306, 20, 70, 801, 264, 213, 314, 46, 91, 104}
TOPNAMES = {'Cutlery', 'calc', 'cheji bt', '中国必须人能飞😡', 'forgot to mention', 'Sponge(Albert and Bob)', '3.14159265',
            'Sabotage-d', 'SSS', 'Peanut Butter', 'Team SKKU'}
PH = [(0, 59), (60, 199), (200, 349), (350, 500)]
PID = {}
TL = [25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]


def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = {}; q = [t for t, d in deg.items() if d <= 1]; k = 1
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem[t] = k
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq; k += 1
    return rem


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 3


def games():
    out = []
    for d in ('replays/auto/games', 'replays/v28'):
        for g in json.load(open(os.path.join(ROOT, d, 'ledger.json'))):
            p = os.path.join(ROOT, d, '%d.replay' % g['game'])
            if g['map'] != 'Autarky' or not os.path.exists(p): continue
            us = g['side']; them = 'B' if us == 'A' else 'A'
            out.append(dict(path=p, gid=g['game'], src=d.split('/')[1], sides={us: ('us', 'Cache me outside', 1958), them: ('opp', g['opp'], g['oppElo'])}))
    for d in ('notes/replays/autarky', 'notes/replays/top10b', 'notes/replays/midgame'):
        idx = json.load(open(os.path.join(ROOT, d, 'index.json')))
        for m in idx:
            if m.get('mapName') != 'Autarky': continue
            p = os.path.join(ROOT, d, '%d.replay' % m['id'])
            if not os.path.exists(p): continue
            if any(x['id'] == 952 for x in (m['a'], m['b'])): continue
            sides = {}
            for s in 'ab':
                t = m[s]; top = t['id'] in TOP10 or t['name'] in TOPNAMES
                sides[s.upper()] = ('top' if top else 'topopp', t['name'], t['elo'])
            if all(v[0] == 'top' for v in sides.values()):
                pass  # top vs top: both 'top'
            out.append(dict(path=p, gid=m['id'], src=d.split('/')[-1], sides=sides))
    seen = set(); res = []
    for g in out:
        if g['gid'] in seen: continue
        seen.add(g['gid']); res.append(g)
    return res


def analyse(g, PK):
    m = g['map']; rounds = dict(g['rounds']); last = g['last_round']; winner = g['result'].get('winner')
    team = g['team']; born = g['born']
    out = {}
    for T in 'AB':
        E = 'B' if T == 'A' else 'A'
        o = {'T': T, 'win': winner == T, 'last': last, 'end': g['result'].get('endReason'), 'final': g['result'].get(T)}
        # timeline
        tl = {}
        for r in TL:
            s = rounds.get(min(r, last))
            row = s[T] if s else {'n': 0, 'total': 0, 'max': 0}
            tl[r] = (row['n'], row['total'], row['max'])
        o['tl'] = tl
        # eats
        eats = collections.Counter()
        for e in g['eats']:
            if e['team'] != T: continue
            p = ph(e['round']); src = 'spawn' if not e['corpse'] else ('own' if e['corpse'][1] == T else 'enemy')
            loc = 'pk' if e['tile'] in PK else 'open'
            eats[(p, loc, src)] += 1
        o['eats'] = eats
        # splits
        sp = collections.Counter()
        for s in g['splits']:
            if s['team'] != T: continue
            p = ph(s['round'])
            kind = 'rev' if (s['k'] == s['L'] - 2 and s['L'] >= 5) else ('2' if s['k'] == 2 else 'other')
            sp[(p, kind, 'pk' if (s['exits'] <= 1) else 'open')] += 1
            sp[(p, 'L', s['L'])] += 1
        o['splits'] = sp
        # deaths
        dc = collections.Counter(); dl = collections.Counter()
        for d in g['deaths']:
            if d['team'] != T: continue
            p = ph(d['round']); rs = d['reason']
            if rs == 'HitHeadToHead':
                if d['id'] != d['actor']:
                    c = 'rammed_by_enemy' if d.get('killer_team') != T else 'h2h_ally'
                else:
                    c = 'rammed_enemy' if d.get('victim_team', E) != T else 'h2h_ally'
            elif rs == 'HitOtherBody':
                h = d.get('hit'); c = 'body_enemy' if (h and h['team'] != T) else ('body_ally' if h else 'body_?')
            elif rs == 'HitSelf': c = 'self'
            elif rs == 'HitWall': c = 'wall'
            else: c = 'nva'
            trapped = all(v not in ('free', 'pearl') for v in d['nbrs'].values())
            inpk = d['head'] in PK
            dc[(p, c)] += 1; dl[(p, c)] += d['len']
            dc[(p, 'trapped' if trapped else 'free')] += 1
            if inpk: dc[(p, 'inpk')] += 1; dl[(p, 'inpk')] += d['len']
            dc[(p, 'L', min(d['len'], 12))] += 1
        o['deaths'] = dc; o['dlen'] = dl
        # sprints
        o['sprints'] = collections.Counter((ph(a['round']), 'kill' if a['killed'] else ('eat' if a['ate'] else 'other')) for a in g['moves'] if a['team'] == T and a.get('steps', 0) >= 2)
        out[T] = o
    # pump episodes: head enters a pocket tile; closed by exit move, split (as parent) or death, in time order
    ep = {'A': [], 'B': []}
    tl_ = collections.defaultdict(list)
    for a in g['moves']:
        if not a.get('suicide'): tl_[a['id']].append((a['round'], 0, 'move', a))
    for s in g['splits']: tl_[s['parent']].append((s['round'], 1, 'split', s))
    for d in g['deaths']: tl_[d['id']].append((d['round'], 2, 'death', d))
    deaths = {d['id']: d for d in g['deaths']}
    for i, evs in tl_.items():
        evs.sort(key=lambda x: (x[0], x[1]))
        cur = None
        for r, _, kind, x in evs:
            if cur is None:
                if kind == 'move' and x['head'] not in PK and x.get('head_after') in PK:
                    T = x['team']; h1 = x['head_after']
                    hs = rounds.get(r - 1, {}).get('heads', {})
                    en = min((m.dist(h1, v[0]) for v in hs.values() if v[2] != T), default=99)
                    own_in = sum(1 for k, v in hs.items() if v[2] == T and k != i and v[0] in PK and m.dist(v[0], h1) <= 5)
                    en_in = sum(1 for k, v in hs.items() if v[2] != T and v[0] in PK and m.dist(v[0], h1) <= 5)
                    cur = {'team': T, 'id': i, 'r0': r, 'L0': x['len_before'], 'en': en, 'own_in': own_in, 'en_in': en_in,
                           'maxL': x.get('len_after') or 0, 'pocket': PID.get(h1), 'eats': x['ate']}
                continue
            if kind == 'move':
                cur['maxL'] = max(cur['maxL'], x.get('len_after') or 0); cur['eats'] += x['ate']
                if x.get('head_after') is not None and x['head_after'] not in PK:
                    cur.update(out='exit', L1=x['len_after'], r1=r); ep[cur['team']].append(cur); cur = None
            elif kind == 'split':
                d = deaths.get(i)
                cur.update(out='pump', r1=r, splitL=x['L'], k=x['k'], exits=x['exits'],
                           parent_death=(d['round'] - r, d['reason'], d['len']) if d else None)
                ep[cur['team']].append(cur); cur = None
            else:
                cur.update(out='died', r1=r, dreason=x['reason'], dL=x['len'], hit=x.get('hit'))
                ep[cur['team']].append(cur); cur = None
    # per-pocket eats by phase
    for T in 'AB':
        c = collections.Counter()
        for e in g['eats']:
            if e['team'] == T and e['tile'] in PK: c[(ph(e['round']), PID[e['tile']])] += 1
        out[T]['pk_by_pocket'] = c
        # pocket head-occupancy: rounds with >=1 own head in pocket, per pocket
        occ = collections.Counter()
        for r, s in g['rounds']:
            seen = set(PID[v[0]] for v in s['heads'].values() if v[2] == T and v[0] in PK)
            for p_ in seen: occ[(ph(r), p_)] += 1
        out[T]['pk_occ'] = occ
    # head location by zone (pocket / mouth = within 3 of a pocket tile / centre x19-34 / side), per phase, dragon-rounds
    def zone(t):
        if t in PK: return 'pocket'
        if min(m.dist(t, u) for u in PK) <= 3: return 'mouth'
        return 'centre' if 19 <= t[0] <= 34 else 'side'
    ZC = {}
    for T in 'AB':
        z = collections.Counter(); ze = collections.Counter()
        for r, s in g['rounds']:
            for k, v in s['heads'].items():
                if v[2] != T: continue
                t = v[0]
                if t not in ZC: ZC[t] = zone(t)
                z[(ph(r), ZC[t])] += 1
        for e in g['eats']:
            if e['team'] != T: continue
            t = e['tile']
            if t not in ZC: ZC[t] = zone(t)
            ze[(ph(e['round']), ZC[t], 'c' if e['corpse'] else 's')] += 1
        out[T]['zone'] = z; out[T]['zone_eats'] = ze
    # rams with context: location vs pockets, local odds from previous round's heads (Chebyshev 3 of the death tile)
    for T in 'AB':
        rl = []
        for d in g['deaths']:
            if d['reason'] != 'HitHeadToHead' or d['team'] != T or d['id'] == d['actor']: continue
            kt = d.get('killer_team')
            hs = rounds.get(d['round'] - 1, {}).get('heads', {})
            own = sum(1 for k, v in hs.items() if v[2] == T and m.cheb(v[0], d['head']) <= 3)
            en = sum(1 for k, v in hs.items() if v[2] != T and m.cheb(v[0], d['head']) <= 3)
            dpk = min((m.dist(d['head'], t) for t in PK), default=99)
            rl.append({'round': d['round'], 'len': d['len'], 'killer_len': d.get('killer_len'), 'ally_kill': kt == T, 'own': own, 'en': en, 'dpk': dpk,
                       'age': d['age']})
        out[T]['rammed'] = rl
    for T in 'AB': out[T]['episodes'] = ep[T]
    for tt, pts in m.dragons:
        if len(pts) >= 10:
            T = 'AB'[tt]; xs = {pts[0][0]}
            out[T]['home'] = sorted({p for t, p in PID.items() if abs(t[0] - pts[0][0]) <= 1})
    # pocket eats per pocket id (4 pockets) & control
    return out


def pocket_ids(PK, m):
    # connected components of pocket tiles
    comp = {}; cid = 0
    for t in PK:
        if t in comp: continue
        st = [t]; comp[t] = cid
        while st:
            u = st.pop()
            for d in 'NESW':
                v = m.step(u, d)
                if v in PK and v not in comp: comp[v] = cid; st.append(v)
        cid += 1
    return comp


if __name__ == '__main__':
    res = []
    for gm in games():
        try:
            g = sim2.simulate(gm['path'])
        except Exception as ex:
            print('fail', gm['gid'], ex); continue
        PK = pockets(g['map'])
        PID.clear(); PID.update(pocket_ids(PK, g['map']))
        a = analyse(g, PK)
        for T, (grp, name, elo) in gm['sides'].items():
            oth = 'B' if T == 'A' else 'A'
            r = dict(a[T], gid=gm['gid'], src=gm['src'], grp=grp, name=name, elo=elo, oppname=gm['sides'][oth][1], oppelo=gm['sides'][oth][2], oppgrp=gm['sides'][oth][0])
            res.append(r)
        # opponent episodes are in a[oth]; also attach the raw sim for ours? too big: skip
    pickle.dump(res, open(os.path.join(H, 'games.pkl'), 'wb'))
    print(len(res), collections.Counter((r['grp'], r['src']) for r in res))
