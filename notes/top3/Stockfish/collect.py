"""Per (game, team) behaviour metrics for the Stockfish study.
Groups:  SF  = Stockfish vs strong (elo>=1940) others     SFo = those others
         SFu = Stockfish vs us                             U   = us vs Stockfish
         US  = us vs strong non-Stockfish (ledger, since 17:00 29 Sep)   USo = those opponents
Run from project root:  python3 notes/top3/Stockfish/collect.py   -> notes/top3/Stockfish/metrics.pkl
Sequential (no pool). Read-only over replays."""
import json, os, sys, glob, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2

SNAP = (10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 350, 400, 450, 480, 500)
PH = ((0, 60), (61, 150), (151, 300), (301, 400), (401, 500))


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 4


def games():
    out = []
    idx = json.load(open(os.path.join(H, 'index.json')))
    for m in idx:
        p = os.path.join(H, 'replays', f"{m['id']}.replay")
        if not os.path.exists(p): continue
        s = m['sf']; o = 'b' if s == 'a' else 'a'
        Ts, To = s.upper(), o.upper()
        if m['kind'] == 'vsus':
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=Ts, grp='SFu', opp='us', ranked=m['ranked']))
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=To, grp='U', opp='Stockfish', ranked=m['ranked']))
        else:
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=Ts, grp='SF', opp=m[o]['name'], ranked=m['ranked']))
            out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=To, grp='SFo', opp='Stockfish', ranked=m['ranked'], name=m[o]['name']))
    seen = {x['gid'] for x in out}
    L = json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))
    for x in L:
        p = os.path.join(ROOT, f"replays/auto/games/{x['game']}.replay")
        if not os.path.exists(p) or x['game'] in seen: continue
        o = 'B' if x['side'] == 'A' else 'A'
        if x['opp'] == 'Stockfish':
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='U', opp='Stockfish', ranked=x['ranked']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=o, grp='SFu', opp='us', ranked=x['ranked']))
        elif x['oppElo'] >= 1940 and x['at'] >= '2026-09-29T17:00':
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='US', opp=x['opp'], ranked=x['ranked']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=o, grp='USo', opp='us', ranked=x['ranked'], name=x['opp']))
        seen.add(x['game'])
    # A/B batches: side decided by matching the summary to the replay result
    import replay_decode as R
    for f in sorted(glob.glob(os.path.join(ROOT, 'replays/ab_*/summary.json'))):
        for x in json.load(open(f)):
            if x.get('opp') != 'Stockfish' or x['id'] in seen: continue
            p = os.path.join(os.path.dirname(f), f"{x['id']}.replay")
            if not os.path.exists(p): continue
            res = R.load(p)['result']
            side = None
            for T in 'AB':
                if res[T]['longest'] == x['us']['longest'] and res[T]['total'] == x['us']['total'] and res[T]['dragonCount'] == x['us']['dragonCount']:
                    side = T
            if side is None: print('side?', p); continue
            o = 'B' if side == 'A' else 'A'
            out.append(dict(path=p, gid=x['id'], map=x['map'], T=side, grp='U', opp='Stockfish', ranked=False, ab=os.path.basename(os.path.dirname(f))))
            out.append(dict(path=p, gid=x['id'], map=x['map'], T=o, grp='SFu', opp='us', ranked=False, ab=os.path.basename(os.path.dirname(f))))
            seen.add(x['id'])
    return out


def crossed_portal(m, head, mvs):
    pos = head
    for d in mvs:
        e = m.side_edge(pos, d)
        if m.edges.get(e, (0, -1))[0] == 2: return True
        nxt = m.step(pos, d)
        if nxt is None: return False
        pos = nxt
    return False


def death_cat(d, T):
    rs = d['reason']
    if rs == 'HitHeadToHead':
        ot = d.get('killer_team') or d.get('victim_team')
        return 'h2h_ally' if ot == T else ('h2h_enemy' if ot else 'h2h_unk')
    if rs == 'HitOtherBody':
        h = d.get('hit')
        return 'body_ally' if (h and h['team'] == T) else ('body_enemy' if h else 'body_unk')
    return {'HitSelf': 'self', 'HitWall': 'wall', 'NoValidAction': 'novalid'}.get(rs, rs)


def analyze(path, Ts):
    g = sim2.simulate(path); m = g['map']
    rounds = dict(g['rounds']); last = g['last_round']; res = g['result']
    fast = {t for t, (a, b) in m.tiles.items() if 0 < b <= 5}
    out = {}
    for T in Ts:
        E = 'B' if T == 'A' else 'A'
        R = {'last': last, 'end': res.get('endReason'), 'winner': res.get('winner'), 'W': m.w, 'H': m.h,
             'longest_end': res[T]['longest'], 'opp_longest_end': res[E]['longest'], 'total_end': res[T]['total'],
             'n_end': res[T]['dragonCount'], 'has_portals': any(k == 2 for k, _ in m.edges.values())}
        R['win'] = res.get('winner') == T
        for r in SNAP:
            s = rounds.get(min(r, last))
            if s is None or r > last:
                R[f'n{r}'] = 0 if r > last and R['end'] != 'roundLimit' and res[T]['dragonCount'] == 0 else (s[T]['n'] if s else 0)
                if r > last:
                    fin = rounds[last][T]
                    R[f'n{r}'] = fin['n']; R[f'tot{r}'] = fin['total']; R[f'max{r}'] = fin['max']; R[f'sec{r}'] = fin['lens'][1] if len(fin['lens']) > 1 else 0
                    continue
            ls = s[T]['lens']
            R[f'n{r}'] = len(ls); R[f'tot{r}'] = sum(ls); R[f'max{r}'] = ls[0] if ls else 0
            R[f'sec{r}'] = ls[1] if len(ls) > 1 else 0
            R[f'big{r}'] = sum(1 for x in ls if x >= 10)
            R[f'small{r}'] = sum(1 for x in ls if x <= 3)
            if r in (30, 60, 150):
                heads = [h for j, (h, L, t) in s['heads'].items() if t == T]
                nn = [min((m.dist(a, b) for k2, b in enumerate(heads) if k2 != k1), default=0) for k1, a in enumerate(heads)]
                R[f'nn{r}'] = st.mean(nn) if nn else 0
                R[f'cells{r}'] = len({(h[0] * 4 // m.w, h[1] * 4 // m.h) for h in heads})
        R['maxunits'] = max(s[T]['n'] for r, s in g['rounds'])
        R['r64'] = next((r for r, s in g['rounds'] if s[T]['n'] >= 64), None)
        for N in (8, 16, 32, 48):
            R[f'reach{N}'] = next((r for r, s in g['rounds'] if s[T]['n'] >= N), None)
        # king: final longest id; since when it has been the team's longest continuously
        kings = [(r, s[T]['king'], s[T]['max']) for r, s in g['rounds']]
        fk = kings[-1][1]
        since = None
        for r, k, mx in reversed(kings):
            if k != fk: break
            since = r
        R['king_since'] = since if fk is not None else None
        R['king_changes_300'] = sum(1 for i in range(1, len(kings)) if kings[i][0] >= 300 and kings[i][1] != kings[i - 1][1])
        # round when longest first >= 10, 20, 30
        for N in (10, 20, 30, 40):
            R[f'max{N}_at'] = next((r for r, k, mx in kings if mx >= N), None)
        D = collections.Counter()
        # deaths
        for d in g['deaths']:
            if d['team'] != T: continue
            p = ph(d['round']); c = death_cat(d, T)
            D[f'd{p}'] += 1; D[f'd{p}_{c}'] += 1; D[f'dL{p}'] += d['len']
            free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
            if free == 0 and c not in ('h2h_enemy', 'h2h_ally'): D[f'd{p}_trapped'] += 1
            k = d.get('king')
            if d['round'] >= 250 and k and k[1] >= 8 and k[3] <= 2 and d['len'] <= 5 and c not in ('h2h_enemy',):
                D['feeddeath'] += 1; D[f'feeddeath{p}'] += 1; D['feedL'] += d['len']
            if d['len'] >= 10: D[f'bigdeath{p}'] += 1; D[f'bigdeath{p}_{c}'] += 1
            if c == 'h2h_enemy': D[f'h2hlen{p}'] += d['len']
            if c == 'body_enemy': D[f'dbodyen{p}'] += 1
        for d in g['deaths']:
            if d['team'] == T: continue
            h = d.get('hit')
            if d['reason'] == 'HitOtherBody' and h and h['team'] == T:
                D[f'blockkill{ph(d["round"])}'] += 1; D[f'blockkillL{ph(d["round"])}'] += d['len']
        # moves
        lastcross = {}
        prevheads = {}
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'):
                if a['team'] == T: D['suicide'] += 1
                continue
            p = ph(a['round']); mv = a['act'].get('move', [])
            D[f'mv{p}'] += 1
            if len(mv) >= 2:
                D[f'spr{p}'] += 1; D[f'sprsteps{p}'] += len(mv)
                if a['ate']: D[f'spr_eat{p}'] += 1
                if a['killed']: D[f'spr_kill{p}'] += 1
                if a['died']: D[f'spr_die{p}'] += 1
                ne = a['near_enemy_head']
                if ne and ne[0] <= 3 and not a['killed'] and not a['died']: D[f'spr_evade{p}'] += 1
            if mv and crossed_portal(m, a['head'], mv):
                D[f'x{p}'] += 1
                if a['died']: D[f'xd{p}'] += 1
            for kid, kt, kl in a['killed']:
                if kt != T:
                    D[f'ram{p}'] += 1; D[f'ramL{p}'] += kl; D[f'ramown{p}'] += a['len_before']
                    if kl >= 10: D[f'ramking{p}'] += 1
                    if len(mv) >= 2: D[f'ramspr{p}'] += 1
                    # local numbers at start of round (previous snapshot)
                    s = rounds.get(a['round'] - 1)
                    if s:
                        own = sum(1 for j, (hh, L, t) in s['heads'].items() if t == T and m.dist(hh, a['head']) <= 5)
                        en = sum(1 for j, (hh, L, t) in s['heads'].items() if t == E and m.dist(hh, a['head']) <= 5)
                        D[f'ramlocal_own{p}'] += own; D[f'ramlocal_en{p}'] += en
                        if own > en: D[f'ram_ahead{p}'] += 1
                        elif own < en: D[f'ram_behind{p}'] += 1
        # being rammed: enemy h2h kills of us, from the enemy mover's perspective
        for d in g['deaths']:
            if d['team'] == T and d['reason'] == 'HitHeadToHead' and d.get('killer') is not None and d.get('killer_team') == E:
                D[f'rammed{ph(d["round"])}'] += 1
                if d['len'] >= 8: D[f'rammedbig{ph(d["round"])}'] += 1
        # eats
        kid_final = fk
        king_at = {r: s[T]['king'] for r, s in g['rounds']}
        for e in g['eats']:
            if e['team'] != T: continue
            p = ph(e['round']); D[f'e{p}'] += 1
            if e['corpse']:
                if e['corpse'][1] == T: D[f'eco{p}'] += 1
                else: D[f'ece{p}'] += 1
            else:
                if e['tile'] in fast: D[f'efast{p}'] += 1
            if e['id'] == king_at.get(e['round'] - 1) or e['id'] == king_at.get(e['round']):
                D[f'ek{p}'] += 1
                if e['corpse'] and e['corpse'][1] == T: D[f'ekown{p}'] += 1
                elif e['corpse']: D[f'eken{p}'] += 1
            if e['id'] == kid_final:
                D[f'efk{p}'] += 1
                if e['corpse'] and e['corpse'][1] == T: D[f'efkown{p}'] += 1
        # splits
        sp = [s for s in g['splits'] if s['team'] == T]
        R['first_split'] = min((s['round'] for s in sp), default=None)
        R['split_r'] = [s['round'] for s in sp[:6]]
        for s in sp:
            p = ph(s['round']); D[f's{p}'] += 1; D[f'sk{p}'] += s['k']; D[f'sL{p}'] += s['L']
            if s['exits'] <= 1: D[f'srev{p}'] += 1
            if s['k'] == 2: D[f'sk2_{p}'] += 1
            if s['L'] - s['k'] == 2: D[f'sp2_{p}'] += 1
            if s['L'] >= 10: D[f'sbig{p}'] += 1
            D[f'sL_{min(s["L"],12)}'] += 1
        # sonar
        so = [x for x in g['sonars'] if x['team'] == T]
        D['sonar'] = len(so)
        R.update(D)
        out[T] = R
    return out


if __name__ == '__main__':
    G = games()
    by = collections.defaultdict(set)
    for x in G: by[x['path']].add(x['T'])
    cache = {}
    for i, (p, Ts) in enumerate(sorted(by.items())):
        try:
            cache[p] = analyze(p, tuple(sorted(Ts)))
        except Exception as ex:
            import traceback; traceback.print_exc(); print('ERR', p, ex)
        if i % 20 == 0: print(i, len(by), flush=True)
    rows = []
    for x in G:
        r = cache.get(x['path'])
        if not r: continue
        R = dict(x); R.update(r[x['T']]); rows.append(R)
    pickle.dump(rows, open(os.path.join(H, 'metrics.pkl'), 'wb'))
    print(len(rows), collections.Counter(r['grp'] for r in rows))
