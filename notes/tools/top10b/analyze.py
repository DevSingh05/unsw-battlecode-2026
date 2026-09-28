"""Whole-game behaviour metrics per (game, team) for top-10 vs us (v16).
Groups: top (current top-10 team, notes/replays/top10b), peer (its 1780-1940 opponent),
        us (Cache me outside v16, replays/v16), usopp (our opponent).
Usage: python3 analyze.py [jobs=4] -> metrics.pkl (list of dicts)."""
import json, os, sys, pickle, collections, statistics as st
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, os.path.join(H, '..'))
import sim2
TOP10 = {306, 70, 264, 801, 20, 46, 91, 213, 249, 470}
PH = ((1, 60), (61, 350), (351, 500))
SNAP = (10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500)


def games():
    out = []
    for m in json.load(open(os.path.join(ROOT, 'notes/replays/top10b/index.json'))):
        p = os.path.join(ROOT, f"notes/replays/top10b/{m['id']}.replay")
        if not os.path.exists(p): continue
        for s, T in (('a', 'A'), ('b', 'B')):
            grp = 'top' if m[s]['id'] in TOP10 else 'peer'
            o = 'b' if s == 'a' else 'a'
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=T, grp=grp, name=m[s]['name'], elo=m[s]['elo'],
                            opp=m[o]['name'], oppelo=m[o]['elo'], ranked=m.get('ranked')))
    for x in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
        p = os.path.join(ROOT, f"replays/v16/{x['game']}.replay")
        if not os.path.exists(p): continue
        o = 'B' if x['side'] == 'A' else 'A'
        out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='us', name='us', elo=1850, opp=x['opp'], oppelo=x['oppElo'], ranked=x['ranked']))
        out.append(dict(path=p, gid=x['game'], map=x['map'], T=o, grp='usopp', name=x['opp'], elo=x['oppElo'], opp='us', oppelo=1850, ranked=x['ranked']))
    return out


def phase(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 2


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
    rounds = dict(g['rounds']); last = g['last_round']
    res = g['result']
    out = {}
    for T in Ts:
        E = 'B' if T == 'A' else 'A'
        R = {'last': last, 'end': res.get('endReason'), 'winner': res.get('winner'),
             'longest_end': res.get(T, {}).get('longest'), 'opp_longest_end': res.get(E, {}).get('longest'),
             'has_portals': any(k == 2 for k, _ in m.edges.values()), 'area': m.w * m.h}
        # snapshots
        for r in SNAP:
            rr = min(r, last)
            s = rounds.get(rr)
            if s is None: continue
            ls = s[T]['lens']
            R[f'n{r}'] = len(ls); R[f'tot{r}'] = sum(ls); R[f'max{r}'] = ls[0] if ls else 0
            R[f'mean{r}'] = sum(ls) / len(ls) if ls else 0
            R[f'second{r}'] = ls[1] if len(ls) > 1 else 0
            R[f'en_max{r}'] = s[E]['max']
            if r == 60 or r == 30:
                heads = [h for j, (h, L, t) in s['heads'].items() if t == T]
                nn = [min((m.dist(a, b) for b in heads if b is not a), default=0) for a in heads]
                R[f'nn{r}'] = st.mean(nn) if nn else 0
                cells = {(h[0] * 4 // m.w, h[1] * 4 // m.h) for h in heads}
                R[f'cells{r}'] = len(cells)  # of 16 map quadrants-of-quadrants
        # deaths
        king_ids = {}
        for r, s in g['rounds']:
            king_ids[r] = s[T]['king']
        D = collections.Counter()
        bigdeaths = []
        for d in g['deaths']:
            if d['team'] != T: continue
            ph = phase(d['round']); rs = d['reason']
            if rs == 'HitHeadToHead':
                ot = d.get('killer_team') or d.get('victim_team')
                cat = 'h2h_ally' if ot == T else ('h2h_enemy' if ot else 'h2h_unk')
            elif rs == 'HitOtherBody':
                h = d.get('hit')
                cat = 'body_ally' if (h and h['team'] == T) else ('body_enemy' if h else 'body_unk')
            elif rs == 'HitSelf': cat = 'self'
            elif rs == 'HitWall': cat = 'wall'
            elif rs == 'NoValidAction': cat = 'novalid'
            else: cat = rs
            free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
            k = d.get('king')
            feed = d['round'] >= 300 and d['len'] <= 4 and k and k[1] >= 8 and k[2] <= 3 and cat in ('self', 'wall', 'novalid', 'body_ally', 'Suicide', 'suicide')
            D[f'd{ph}'] += 1; D[f'd{ph}_{cat}'] += 1
            if free == 0 and cat in ('self', 'wall', 'novalid', 'body_ally', 'body_enemy', 'body_unk'): D[f'd{ph}_trapped'] += 1
            if feed: D[f'd{ph}_feed'] += 1
            if d['len'] >= 8: D[f'd{ph}_big'] += 1; bigdeaths.append((d['round'], d['len'], cat))
            if d['len'] >= 10 and d['round'] >= 300: D['king_death'] += 1
        # moves: portal crossings, fatal crossings, ping-pong, sprints
        lastcross = {}
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'): continue
            ph = phase(a['round'])
            mvs = a['act'].get('move', [])
            D[f'mv{ph}'] += 1
            if len(mvs) >= 2: D[f'sprint{ph}'] += 1
            if mvs and crossed_portal(m, a['head'], mvs):
                D[f'x{ph}'] += 1
                if a['died']: D[f'xd{ph}'] += 1; D[f'xd{ph}_{a["died"]}'] += 1
                if a['id'] in lastcross and a['round'] - lastcross[a['id']] <= 4: D[f'xpp{ph}'] += 1
                lastcross[a['id']] = a['round']
            for kid, kt, kl in a['killed']:
                if kt != T: D[f'kill{ph}'] += 1; D[f'killL{ph}'] += kl
                if kt != T and kl >= 10 and a['round'] >= 300: D['kill_king'] += 1
        # enemy deaths caused by running into our bodies
        for d in g['deaths']:
            if d['team'] == T: continue
            h = d.get('hit')
            if d['reason'] == 'HitOtherBody' and h and h['team'] == T: D[f'blockkill{phase(d["round"])}'] += 1
        # eats
        for e in g['eats']:
            if e['team'] != T: continue
            ph = phase(e['round']); D[f'eat{ph}'] += 1
            if e['corpse']:
                D[f'eatc{ph}'] += 1
                if e['corpse'][1] == T: D[f'eatco{ph}'] += 1
            if e['round'] >= 350 and e['len'] is not None:
                ki = king_ids.get(e['round'])
                if e['id'] == ki: D['king_eat_late'] += 1
        # splits
        sp = [s for s in g['splits'] if s['team'] == T]
        R['first_split'] = min((s['round'] for s in sp), default=None)
        for s in sp:
            ph = phase(s['round']); D[f'split{ph}'] += 1
            if s['exits'] <= 1: D[f'splitrev{ph}'] += 1
            if s['L'] >= 8 and s['round'] >= 300: D['bigsplit_late'] += 1
        # when first reach N units
        for N in (4, 8, 16, 24, 32):
            R[f'reach{N}'] = next((r for r, s in g['rounds'] if s[T]['n'] >= N), None)
        R.update(D); R['bigdeaths'] = bigdeaths
        out[T] = R
    return out


def work(args):
    path, Ts = args
    try:
        return path, analyze_game(path, Ts)
    except Exception as ex:
        return path, {'err': repr(ex)}


if __name__ == '__main__':
    G = games()
    by = collections.defaultdict(set)
    for x in G: by[x['path']].add(x['T'])
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(jobs) as P:
        res = dict(P.map(work, sorted((p, tuple(sorted(t))) for p, t in by.items()), chunksize=2))
    rows = []
    for x in G:
        r = res.get(x['path'], {})
        if 'err' in r: print('ERR', x['path'], r['err']); continue
        R = dict(x); R.update(r[x['T']]); R['win'] = (R['winner'] == x['T']); rows.append(R)
    pickle.dump(rows, open(os.path.join(H, 'metrics.pkl'), 'wb'))
    print(len(rows), collections.Counter(r['grp'] for r in rows))
