"""Per (game, team) behaviour metrics for the Cutlery study.
Groups:
  cut      Cutlery's side in its recent games (notes/top3/Cutlery/replays, index.json)
  cutopp   the opponent side in those games
  usC      our side in our games vs Cutlery (replays/auto/games, ledger opp == Cutlery)
  cutvus   Cutlery's side in those games
  us       our side in recent games vs elo>=1950 (ledger, since 29 Sep 15:00, <=8 most recent per map, not Cutlery)
  usopp    their side
  us31     our side in v30/v31 server A/B games vs top-10 (replays/ab_kc31, ab_pf31, ab_v30kc, ab_v30sch; side from summary)
Usage (project root): python3 notes/top3/Cutlery/collect.py [jobs=3] -> notes/top3/Cutlery/metrics.pkl"""
import json, os, sys, pickle, collections, statistics as st
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2

SN = (10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500)
PH = ((0, 60), (61, 200), (201, 350), (351, 500))


def ph(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b: return i
    return 3


def games():
    out = []
    for m in json.load(open(os.path.join(H, 'index.json'))):
        p = os.path.join(H, 'replays', f"{m['id']}.replay")
        if not os.path.exists(p): continue
        cs = 'a' if m['a']['id'] == 306 else 'b'; os_ = 'b' if cs == 'a' else 'a'
        out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=cs.upper(), grp='cut', opp=m[os_]['name'], oppelo=m[os_]['elo'], kind=m['kind']))
        out.append(dict(path=p, gid=m['id'], map=m['mapName'], T=os_.upper(), grp='cutopp', opp='Cutlery', oppelo=m[cs]['elo'], kind=m['kind'], name=m[os_]['name']))
    L = json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))
    per = collections.Counter()
    for x in sorted(L, key=lambda x: x['at'], reverse=True):
        p = os.path.join(ROOT, f"replays/auto/games/{x['game']}.replay")
        if not os.path.exists(p): continue
        o = 'B' if x['side'] == 'A' else 'A'
        if 'utlery' in x['opp']:
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='usC', opp=x['opp'], oppelo=x['oppElo']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=o, grp='cutvus', opp='us', oppelo=2000))
        elif x['oppElo'] >= 1950 and x['at'] >= '2026-09-29T15' and per[x['map']] < 8:
            per[x['map']] += 1
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=x['side'], grp='us', opp=x['opp'], oppelo=x['oppElo']))
            out.append(dict(path=p, gid=x['game'], map=x['map'], T=o, grp='usopp', opp='us', oppelo=2000, name=x['opp']))
    for d in ('ab_kc31', 'ab_pf31', 'ab_v30kc', 'ab_v30sch'):
        f = os.path.join(ROOT, 'replays', d, 'summary.json')
        if not os.path.exists(f): continue
        for x in json.load(open(f)):
            p = os.path.join(ROOT, 'replays', d, f"{x['id']}.replay")
            if not os.path.exists(p): continue
            out.append(dict(path=p, gid=x['id'], map=x['map'], T=None, grp='us31', opp=x['opp'], oppelo=0, abus=x['us'], abthem=x['them'], abdir=d))
    return out


def pockets(m):
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); nb[t] = {m.step(t, d) for d in 'NESW'} - {None}
    deg = {t: len(v) for t, v in nb.items()}; rem = set(); q = [t for t, d in deg.items() if d <= 1]
    while q:
        nq = []
        for t in q:
            if t in rem: continue
            rem.add(t)
            for u in nb[t]:
                if u in rem: continue
                deg[u] -= 1
                if deg[u] <= 1: nq.append(u)
        q = nq
    return rem


def crossed_portal(m, head, mvs):
    pos = head
    for d in mvs:
        e = m.side_edge(pos, d)
        if m.edges.get(e, (0, -1))[0] == 2: return True
        nxt = m.step(pos, d)
        if nxt is None: return False
        pos = nxt
    return False


def analyse(g, T, PK):
    m = g['map']; E = 'B' if T == 'A' else 'A'
    rounds = dict(g['rounds']); last = g['last_round']; res = g['result']
    R = {'last': last, 'end': res.get('endReason'), 'win': res.get('winner') == T, 'draw': res.get('winner') not in ('A', 'B'),
         'res_long': res.get(T, {}).get('longest'), 'res_tot': res.get(T, {}).get('total'), 'res_n': res.get(T, {}).get('dragonCount'),
         'opp_long': res.get(E, {}).get('longest'), 'opp_tot': res.get(E, {}).get('total'),
         'area': m.w * m.h, 'portals': any(k == 2 for k, _ in m.edges.values()), 'npocket': len(PK)}
    # snapshots (eliminated -> 0)
    for r in SN:
        if r <= last: ls = rounds[r][T]['lens'] if r in rounds else []
        elif R['end'] == 'roundLimit' or R['win']: ls = rounds[last][T]['lens']
        else: ls = []
        R[f'n{r}'] = len(ls); R[f'tot{r}'] = sum(ls); R[f'max{r}'] = ls[0] if ls else 0; R[f'sec{r}'] = ls[1] if len(ls) > 1 else 0
        R[f'small{r}'] = sum(1 for x in ls if x <= 3)
    # opening spread
    for r in (30, 60):
        s = rounds.get(min(r, last))
        heads = [h for j, (h, L, t) in s['heads'].items() if t == T]
        nn = [min((m.dist(a, b) for b in heads if b is not a), default=0) for a in heads]
        R[f'nn{r}'] = st.mean(nn) if nn else 0
        cells = {(h[0] * 6 // m.w, h[1] * 6 // m.h) for h in heads}
        R[f'cells{r}'] = len(cells)
    visited = set()
    for mv in g['moves']:
        if mv['team'] == T and mv['round'] <= 60 and mv.get('head_after'): visited.add(mv['head_after'])
    R['visit60'] = len(visited) / (m.w * m.h)
    # head-rounds per phase
    hr = [0] * 4
    for r, s in g['rounds']: hr[ph(r)] += s[T]['n']
    R['hr'] = hr
    # eats
    ek = collections.defaultdict(lambda: [0] * 4)
    kingid = {r: s[T]['king'] for r, s in g['rounds']}
    for e in g['eats']:
        if e['team'] != T: continue
        p = ph(e['round']); c = e['corpse']
        if c is None:
            ek['spawn'][p] += 1
            if e['tile'] in PK: ek['pocket'][p] += 1
            gp = e['gap']
            if gp and gp[1] and gp[1] <= 5: ek['fast'][p] += 1
        elif c[1] == T: ek['own'][p] += 1
        else: ek['enemy'][p] += 1
        if e['tile'] in PK and c is not None: ek['pocketcorpse'][p] += 1
        k = kingid.get(e['round'] - 1)
        if k == e['id'] and e['len'] and e['len'] >= 8:
            ek['king'][p] += 1
            if c is not None and c[1] == T: ek['kingown'][p] += 1
            if c is not None and c[1] != T: ek['kingenemy'][p] += 1
    R['eats'] = dict(ek)
    # splits
    sp = collections.defaultdict(lambda: [0] * 4); ks = collections.Counter(); first = None; Ls = []
    for s in g['splits']:
        if s['team'] != T: continue
        p = ph(s['round']); sp['all'][p] += 1
        if s['k'] == 2: sp['k2'][p] += 1
        if s['exits'] <= 1: sp['tight'][p] += 1
        if s['L'] - s['k'] == 2 and s['k'] > 2: sp['tip'][p] += 1
        if s['L'] >= 10: sp['big'][p] += 1
        if s['round'] <= 60: ks[s['k']] += 1; Ls.append(s['L'])
        if first is None and s['round'] > 0: first = s['round']
    R['splits'] = dict(sp); R['ks60'] = dict(ks); R['first_split'] = first; R['splitL60'] = st.mean(Ls) if Ls else 0
    R['split_r0'] = sum(1 for s in g['splits'] if s['team'] == T and s['round'] == 0)
    # moves: sprints, portal crossings, suicides
    mv = collections.defaultdict(lambda: [0] * 4)
    for a in g['moves']:
        if a['team'] != T: continue
        p = ph(a['round'])
        if a.get('suicide'): mv['suicide'][p] += 1; continue
        mv['moves'][p] += 1
        if a['steps'] >= 2:
            mv['sprint'][p] += 1; mv['sprint_steps'][p] += a['steps']
            if a['ate']: mv['sprint_ate'][p] += 1
            if a['killed']: mv['sprint_kill'][p] += 1
            if a['len_before'] >= 8: mv['sprint_big'][p] += 1
        if m.edges and crossed_portal(m, a['head'], a['act']['move']):
            mv['portal'][p] += 1
            if a['died']: mv['portal_die'][p] += 1
    R['mv'] = dict(mv)
    # deaths
    dd = collections.defaultdict(lambda: [0] * 4); dl = collections.defaultdict(lambda: [0] * 4)
    rams = []; kills = collections.defaultdict(lambda: [0] * 4)
    for d in g['deaths']:
        p = ph(d['round'])
        if d['team'] == T:
            rs = d['reason']
            if rs == 'HitOtherBody' and d.get('hit'): rs = 'BodyAlly' if d['hit']['team'] == T else 'BodyEnemy'
            dd[rs][p] += 1; dl[rs][p] += d['len']; dd['all'][p] += 1; dl['all'][p] += d['len']
            if d['len'] >= 10: dd['big'][p] += 1
            if rs == 'NoValidAction' and d.get('king') and d['king'][2] <= 3 and d['len'] <= 5: dd['feedNVA'][p] += 1
        else:
            if d['reason'] == 'HitOtherBody' and d.get('hit') and d['hit']['team'] == T: kills['block'][p] += 1; kills['block_len'][p] += d['len']
        # rams: mover (actor) and victim both die, record once from the mover's death record
        if d['reason'] == 'HitHeadToHead' and d['id'] == d['actor'] and d.get('victim') is not None:
            if d['team'] == T or d.get('victim_team') == T:
                prev = rounds.get(d['round'] - 1) or rounds.get(d['round']) or g['rounds'][0][1]
                site = d['head']
                own = sum(1 for j, (h, L, t) in prev['heads'].items() if t == T and m.dist(h, site) <= 6)
                en = sum(1 for j, (h, L, t) in prev['heads'].items() if t == E and m.dist(h, site) <= 6)
                ownL = sum(L for j, (h, L, t) in prev['heads'].items() if t == T and m.dist(h, site) <= 6)
                enL = sum(L for j, (h, L, t) in prev['heads'].items() if t == E and m.dist(h, site) <= 6)
                rams.append({'round': d['round'], 'by': 'T' if d['team'] == T else 'E', 'mover_len': d['len'], 'victim_len': d.get('victim_len'),
                             'same': d.get('victim_team') == d['team'], 'steps': d.get('steps'), 'own': own, 'en': en, 'ownL': ownL, 'enL': enL})
    R['deaths'] = dict(dd); R['dlen'] = dict(dl); R['kills'] = dict(kills); R['rams'] = rams
    # corpse harvest: of pearls dropped by E deaths, fraction eaten by T (within 20 rounds) and vice versa
    drop = {'T': 0, 'E': 0}
    for d in g['deaths']: drop['T' if d['team'] == T else 'E'] += (d['len'] + 1) // 2
    R['drop'] = drop
    # king
    mx = [(r, s[T]['max'], s[T]['king']) for r, s in g['rounds']]
    R['king10'] = next((r for r, L, k in mx if L >= 10), None); R['king20'] = next((r for r, L, k in mx if L >= 20), None)
    R['king30'] = next((r for r, L, k in mx if L >= 30), None)
    sw = 0; prevk = None; kd = 0
    alive_ids = None
    for r, L, k in mx:
        if prevk is not None and k != prevk and L >= 8: sw += 1
        prevk = k
    for d in g['deaths']:
        if d['team'] == T and d['len'] >= 8:
            s = rounds.get(d['round'] - 1)
            if s and s[T]['king'] == d['id']: kd += 1; R.setdefault('kingdeath', []).append((d['round'], d['len'], d['reason']))
    R['king_switch'] = sw; R['king_deaths'] = kd
    # endgame: enemy heads within 6 of king, mean over r400-499
    near = []; kdist = []
    for r, s in g['rounds']:
        if r < 400: continue
        k = s[T]['king']
        if k is None or k not in s['heads']: continue
        kh = s['heads'][k][0]
        near.append(sum(1 for j, (h, L, t) in s['heads'].items() if t == E and m.dist(h, kh) <= 6))
        oh = [m.dist(h, kh) for j, (h, L, t) in s['heads'].items() if t == T and j != k]
        kdist.append(sum(1 for x in oh if x <= 6))
    R['end_en_near'] = st.mean(near) if near else None; R['end_own_near'] = st.mean(kdist) if kdist else None
    return R


PKC = {}


def work(items):
    try:
        g = sim2.simulate(items[0]['path'])
    except Exception as ex:
        return [dict(it, err=str(ex)) for it in items]
    PK = pockets(g['map']); out = []
    for item in items:
        T = item['T']
        if T is None:  # ab: infer side from longest/total
            res = g['result']
            T = 'A' if (res['A']['longest'], res['A']['total']) == (item['abus']['longest'], item['abus']['total']) else 'B'
            item = dict(item, T=T)
        try:
            out.append(dict(item, **analyse(g, T, PK)))
        except Exception as ex:
            import traceback; out.append(dict(item, err=traceback.format_exc()))
    return out


if __name__ == '__main__':
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    G = games()
    # group items by path so each replay is simulated once per process call
    print(len(G), collections.Counter(x['grp'] for x in G), flush=True)
    out = []
    with Pool(jobs) as P:
        bp = collections.defaultdict(list)
        for x in G: bp[x['path']].append(x)
        for i, r in enumerate(P.imap_unordered(work, list(bp.values()))):
            out.extend(r)
            if i % 25 == 0: print(i, flush=True)
    pickle.dump(out, open(os.path.join(H, 'metrics.pkl'), 'wb'))
    print('errors', [x for x in out if 'err' in x][:3])


def side(item, g):
    """Our side letter for an item (infers it for ab games from the summary's longest/total)."""
    if item.get('T'): return item['T']
    res = g['result']
    return 'A' if (res['A']['longest'], res['A']['total']) == (item['abus']['longest'], item['abus']['total']) else 'B'
