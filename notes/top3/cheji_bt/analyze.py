"""Per (game, team) behaviour metrics for the cheji bt study.
Groups:
  cheji   : cheji bt in its games vs strong peers (elo>=1900, not us)       notes/top3/cheji_bt/replays
  cpeer   : those peers
  cvsus   : cheji bt in games vs us (ledger + ab_* + listing)
  usvc    : us in those games
  uspeer  : us vs the SAME peer teams (ledger, since 29 Sep 15:00 UTC)
  uspeerop: those peers vs us
Usage: python3 analyze.py [jobs] -> metrics.pkl"""
import json, os, sys, pickle, collections, glob, statistics as st
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
PEERS = {'forgot to mention', 'Sabotage-d', 'Sponge(Albert and Bob)', 'SSS', '中国必须人能飞😡', 'ddabap', 'free trip to sydney pls'}
PH = ((1, 60), (61, 200), (201, 350), (351, 500))
SNAP = (20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 350, 400, 450, 480, 500)


def games():
    out = []; seen = set()
    for m in json.load(open(os.path.join(H, 'index.json'))):
        p = os.path.join(H, 'replays', f"{m['id']}.replay")
        if not os.path.exists(p): continue
        C = m['side'].upper(); O = 'B' if C == 'A' else 'A'
        if m['kind'] == 'peer':
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=C, grp='cheji', opp=m['opp']))
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=O, grp='cpeer', opp='cheji bt'))
        else:
            seen.add(m['id'])
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=C, grp='cvsus', opp='us'))
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=O, grp='usvc', opp='cheji bt'))
    led = json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))
    for x in led:
        p = os.path.join(ROOT, f"replays/auto/games/{x['game']}.replay")
        if not os.path.exists(p): continue
        O = 'B' if x['side'] == 'A' else 'A'
        if x['opp'] == 'cheji bt' and x['game'] not in seen:
            seen.add(x['game'])
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='usvc', opp='cheji bt', at=x['at']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=O, grp='cvsus', opp='us', at=x['at']))
        elif x['opp'] in PEERS and x['at'] >= '2026-09-29T15':
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='uspeer', opp=x['opp'], at=x['at']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=O, grp='uspeerop', opp='us', at=x['at']))
    for d in sorted(glob.glob(os.path.join(ROOT, 'replays/ab_*'))):
        try: S = json.load(open(os.path.join(d, 'summary.json')))
        except Exception: continue
        for x in S:
            if x['opp'] != 'cheji bt' or x['id'] in seen: continue
            p = os.path.join(d, f"{x['id']}.replay")
            if not os.path.exists(p): continue
            seen.add(x['id'])
            out.append(dict(path=p, gid=x['id'], map=x['map'], T='?us', grp='usvc', opp='cheji bt', ab=os.path.basename(d), abus=x['us']))
            out.append(dict(path=p, gid=x['id'], map=x['map'], T='?them', grp='cvsus', opp='us', ab=os.path.basename(d), abus=x['us']))
    return out


def phase(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 3


def deadend_tiles(m):
    """static leaf pruning: tiles in dead-end pockets / 1-wide dead-end tubes"""
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            p = (x, y); s = set()
            for d in 'NESW':
                q = m.step(p, d)
                if q is not None and q != p: s.add(q)
            nb[p] = s
    deg = {p: len(s) for p, s in nb.items()}
    dead = set(); stack = [p for p, k in deg.items() if k <= 1]
    while stack:
        p = stack.pop()
        if p in dead: continue
        dead.add(p)
        for q in nb[p]:
            if q in dead: continue
            deg[q] -= 1
            if deg[q] <= 1: stack.append(q)
    return dead, nb


def crossed_portal(m, head, mvs):
    pos = head
    for d in mvs:
        e = m.side_edge(pos, d)
        if m.edges.get(e, (0, -1))[0] == 2: return True
        nxt = m.step(pos, d)
        if nxt is None: return False
        pos = nxt
    return False


def analyze_game(path, Ts):
    g = sim2.simulate(path); m = g['map']
    rounds = dict(g['rounds']); last = g['last_round']; res = g['result']
    dead, nb = deadend_tiles(m)
    # natural-spawn counts per tile (for "hot tile" classification, per game)
    spawn = collections.Counter(t for r, t, c in g['appears'] if not c)
    hot = {t for t, c in spawn.items() if c >= max(8, last / 25)}
    out = {}
    for T in Ts:
        E = 'B' if T == 'A' else 'A'
        R = {'last': last, 'end': res.get('endReason'), 'winner': res.get('winner'), 'area': m.w * m.h,
             'has_portals': any(k == 2 for k, _ in m.edges.values()),
             'longest_end': res.get(T, {}).get('longest'), 'opp_longest_end': res.get(E, {}).get('longest'),
             'total_end': res.get(T, {}).get('total'), 'opp_total_end': res.get(E, {}).get('total')}
        for r in SNAP:
            s = rounds.get(min(r, last))
            if s is None: continue
            ls = s[T]['lens']
            R[f'n{r}'] = len(ls); R[f'tot{r}'] = sum(ls); R[f'max{r}'] = ls[0] if ls else 0
            R[f'sec{r}'] = ls[1] if len(ls) > 1 else 0
            R[f'big{r}'] = sum(1 for L in ls if L >= 10)
            R[f'small{r}'] = sum(1 for L in ls if L <= 3)
            R[f'en_n{r}'] = s[E]['n']; R[f'en_tot{r}'] = s[E]['total']; R[f'en_max{r}'] = s[E]['max']
            if r in (30, 60, 100):
                heads = [h for j, (h, L, t) in s['heads'].items() if t == T]
                nn = [min((m.dist(a, b) for b in heads if b is not a), default=0) for a in heads]
                R[f'nn{r}'] = st.mean(nn) if nn else 0
                R[f'cells{r}'] = len({(h[0] * 4 // m.w, h[1] * 4 // m.h) for h in heads})
        R['max_units'] = max(s[T]['n'] for r, s in g['rounds'])
        for N in (8, 16, 32, 48):
            R[f'reach{N}'] = next((r for r, s in g['rounds'] if s[T]['n'] >= N), None)
        D = collections.Counter()
        # head-rounds per phase
        for r, s in g['rounds']:
            D[f'hr{phase(r)}'] += s[T]['n']
        # ---- deaths
        for d in g['deaths']:
            if d['team'] != T: continue
            ph = phase(d['round']); rs = d['reason']
            if rs == 'HitHeadToHead':
                ot = d.get('killer_team') or d.get('victim_team')
                cat = 'h2h_ally' if ot == T else 'h2h_enemy'
                if ot != T:
                    # who initiated: actor
                    cat = 'rammed' if d['actor'] != d['id'] else 'ram_trade'
            elif rs == 'HitOtherBody':
                h = d.get('hit'); cat = 'body_ally' if (h and h['team'] == T) else 'body_enemy'
            elif rs == 'HitSelf': cat = 'self'
            elif rs == 'HitWall': cat = 'wall'
            elif rs == 'NoValidAction': cat = 'novalid'
            else: cat = str(rs)
            free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
            D[f'd{ph}'] += 1; D[f'd{ph}_{cat}'] += 1; D[f'dL{ph}'] += d['len']
            if cat in ('self', 'wall', 'novalid', 'body_ally'):
                D[f'd{ph}_{"trap" if free == 0 else "chosen"}'] += 1
            if d['head'] in dead: D[f'd{ph}_dead'] += 1
            k = d.get('king')
            if d['round'] >= 300 and k and k[1] >= 10 and k[2] <= 3 and cat in ('self', 'wall', 'novalid', 'body_ally', 'Suicide'):
                D['feed_deaths'] += 1; D['feed_len'] += d['len']
            if d['len'] >= 10: D[f'bigdeath{ph}'] += 1; D[f'bigdeath_{cat}'] += 1
        # ---- moves
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'): continue
            ph = phase(a['round']); mvs = a['act'].get('move', [])
            D[f'mv{ph}'] += 1
            if len(mvs) >= 2:
                D[f'sprint{ph}'] += 1; D[f'sprintsteps{ph}'] += len(mvs)
                if a['killed']: D[f'sprintkill{ph}'] += 1
                if a['ate']: D[f'sprinteat{ph}'] += 1
            if mvs and m.edges and crossed_portal(m, a['head'], mvs):
                D[f'x{ph}'] += 1
                if a['died']: D[f'xd{ph}'] += 1
        # ---- rams we initiate (actor of a head-to-head that kills an enemy)
        rams = []
        MV = {(a['round'], a['id']): a for a in g['moves']}
        for d in g['deaths']:
            if d['reason'] != 'HitHeadToHead' or d['id'] == d['actor']: continue
            if d.get('killer_team') != T or d['team'] == T: continue
            r = d['round']; s = rounds.get(r - 1) or rounds.get(r) or g['rounds'][0][1]
            ah = None; kl = d.get('killer_len')
            # attacker head before move: from moves list
            mv = MV.get((r, d['actor']))
            ah = mv['head'] if mv else d['head']
            steps = mv['steps'] if mv else 1
            own = sum(1 for j, (h, L, t) in s['heads'].items() if t == T and j != d['actor'] and m.dist(h, ah) <= 4)
            en = sum(1 for j, (h, L, t) in s['heads'].items() if t != T and m.dist(h, ah) <= 4)
            rams.append((r, kl, d['len'], steps, own, en))
            ph = phase(r)
            D[f'ram{ph}'] += 1; D[f'ramvL{ph}'] += d['len']; D[f'ramaL{ph}'] += (kl or 0)
            if steps >= 2: D[f'ramsprint{ph}'] += 1
            if own + 1 > en: D[f'ramahead{ph}'] += 1
            if d['len'] >= 10: D['ram_big'] += 1
            if kl and kl <= 3 and d['len'] >= 6: D['ram_smallbig'] += 1
        R['rams'] = rams
        for d in g['deaths']:
            if d['team'] == T: continue
            h = d.get('hit')
            if d['reason'] == 'HitOtherBody' and h and h['team'] == T: D[f'blockkill{phase(d["round"])}'] += 1
        # ---- eats
        king_ids = {r: s[T]['king'] for r, s in g['rounds']}
        final_king = rounds[last][T]['king'] if rounds[last][T]['n'] else None
        for e in g['eats']:
            if e['team'] != T: continue
            ph = phase(e['round']); D[f'eat{ph}'] += 1
            if e['corpse']:
                D[f'eatc{ph}'] += 1
                if e['corpse'][1] == T: D[f'eatco{ph}'] += 1
                else: D[f'eatce{ph}'] += 1
            else:
                if e['tile'] in dead: D[f'eatdead{ph}'] += 1
                if e['tile'] in hot: D[f'eathot{ph}'] += 1
            if e['round'] > 350 and e['id'] == final_king:
                D['fk_eat'] += 1
                if e['corpse']: D['fk_eat_c' + ('o' if e['corpse'][1] == T else 'e')] += 1
        # ---- splits
        sp = [s for s in g['splits'] if s['team'] == T]
        R['first_split'] = min((s['round'] for s in sp if s['round'] > 0), default=None)
        R['split_r0'] = sum(1 for s in sp if s['round'] == 0)
        for s in sp:
            ph = phase(s['round']); D[f'split{ph}'] += 1
            D[f'splitk{ph}_{min(s["k"], 5)}'] += 1; D[f'splitL{ph}_{min(s["L"], 9)}'] += 1
            if s['exits'] <= 1: D[f'splitrev{ph}'] += 1
            if s['L'] >= 10: D[f'splitbig{ph}'] += 1
        # ---- king
        if final_king is not None:
            since = last
            for r, s in reversed(g['rounds']):
                if s[T]['king'] == final_king: since = r
                else: break
            R['fk_since'] = since
            R['fk_born'] = g['born'].get(final_king)
            R['fk_len'] = rounds[last][T]['max']
        kings = [s[T]['king'] for r, s in g['rounds'] if r >= 300 and s[T]['n']]
        R['king_changes300'] = sum(1 for a, b in zip(kings, kings[1:]) if a != b)
        # king safety: min dist of team's longest head to nearest enemy head, r400+
        ds = []
        for r, s in g['rounds']:
            if r < 400 or not s[T]['n']: continue
            k = s[T]['king']; kh = s['heads'].get(k)
            if not kh: continue
            en = [m.dist(kh[0], h) for j, (h, L, t) in s['heads'].items() if t != T]
            if en: ds.append(min(en))
        R['king_en_dist400'] = st.mean(ds) if ds else None
        R['king_en_close400'] = sum(1 for x in ds if x <= 3) / len(ds) if ds else None
        R.update(D)
        out[T] = R
    return out


def work(args):
    path, Ts = args
    try:
        return path, analyze_game(path, Ts)
    except Exception as ex:
        import traceback; traceback.print_exc()
        return path, {'err': repr(ex)}


if __name__ == '__main__':
    G = games()
    by = collections.defaultdict(set)
    for x in G:
        by[x['path']].update(['A', 'B'])
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    with Pool(jobs) as P:
        res = dict(P.map(work, sorted((p, tuple(sorted(t))) for p, t in by.items()), chunksize=2))
    rows = []
    for x in G:
        r = res.get(x['path'], {})
        if 'err' in r: print('ERR', x['path'], r['err']); continue
        T = x['T']
        if T.startswith('?'):
            # ab games: find our side from summary longest/total
            us = x['abus']; A = r['A']; ourT = 'A' if (A['longest_end'], A['total_end']) == (us['longest'], us['total']) else 'B'
            T = ourT if T == '?us' else ('B' if ourT == 'A' else 'A')
        R = dict(x); R['T'] = T; R.update(r[T]); R['win'] = (R['winner'] == T); rows.append(R)
    pickle.dump(rows, open(os.path.join(H, 'metrics.pkl'), 'wb'))
    print(len(rows), collections.Counter(r['grp'] for r in rows))
    print('wins', {g: sum(r['win'] for r in rows if r['grp'] == g) for g in ('cheji', 'cvsus', 'usvc', 'uspeer')})
