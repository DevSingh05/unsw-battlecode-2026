"""King growth / pearl sources / movement / feeders / sonar for top-10 winners on growth maps.
Input: notes/replays/kings/*.replay + index.json (from kings_fetch.py). Caches *.sim.pkl.
    python3 notes/tools/kings_analyze.py            # per-game + per-map summary
Writes notes/replays/kings/kings_metrics.json"""
import os, sys, json, glob, pickle, collections, statistics as S
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replay_sim import simulate
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/kings')
MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maps')
MAPF = {'Schooltime': 'Schooltime__id9', 'Portals': 'Portals__id20', 'Slithery Fight': 'Slithery_Fight__id21',
        'Queen Of Spades': 'Queen_Of_Spades__id7'}
CK = [100, 150, 200, 250, 300, 350, 400, 450, 499]
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def gaps(name):
    g = {}
    for l in open(os.path.join(MD, MAPF[name] + '.map')):
        f = l.split()
        if f and f[0] == 'TILE' and len(f) == 5: g[(int(f[1]), int(f[2]))] = (int(f[3]), int(f[4]))
    return g


def load(mid):
    pk = os.path.join(RD, f'{mid}.replay.sim.pkl')
    if os.path.exists(pk): return pickle.load(open(pk, 'rb'))
    g = simulate(os.path.join(RD, f'{mid}.replay'))
    g.pop('moves_raw', None)
    pickle.dump(g, open(pk, 'wb'))
    return g


def med(x): return round(S.median(x), 1) if x else None


def wrapd(m, a, b):
    dx = (b[0] - a[0]) % m.w; dy = (b[1] - a[1]) % m.h
    if dx > m.w // 2: dx -= m.w
    if dy > m.h // 2: dy -= m.h
    return dx, dy


def lineage(g, K):
    """list of (id, start_round) from oldest to newest body holders of the final king."""
    splits_by_child = {s['child']: s for s in g['splits']}
    out = [K]; cur = K
    while cur in splits_by_child:
        s = splits_by_child[cur]
        if s['k'] > s['L'] - s['k']: cur = s['parent']; out.insert(0, cur)
        else: break
    return [(i, g['born'].get(i, 0)) for i in out]


def analyze(mid, meta):
    g = load(mid); m = g['map']; gp = gaps(meta['mapName'])
    W = g['result']['winner']; Lt = 'B' if W == 'A' else 'A'
    snap = dict(g['rounds']); last = g['last_round']
    at = lambda r: snap.get(r, snap[max(k for k in snap if k <= r)] if any(k <= r for k in snap) else snap[min(snap)])
    R = {'id': mid, 'map': meta['mapName'], 'end': g['result']['endReason'], 'last': last,
         'W': meta['a' if W == 'A' else 'b']['name'], 'L': meta['b' if W == 'A' else 'a']['name']}
    R['curveW'] = [at(r)[W]['max'] for r in CK]; R['curveL'] = [at(r)[Lt]['max'] for r in CK]
    R['unitsW'] = [at(r)[W]['n'] for r in CK]; R['unitsL'] = [at(r)[Lt]['n'] for r in CK]
    R['secondW'] = [(at(r)[W]['lens'] + [0, 0])[1] for r in CK]
    R['totalW'] = [at(r)[W]['total'] for r in CK]; R['totalL'] = [at(r)[Lt]['total'] for r in CK]
    fin = snap[max(snap)]
    K = fin[W]['king']
    lin = lineage(g, K); R['lineage'] = lin
    ids = [i for i, _ in lin]
    owner = {}  # round -> lineage id holding the king body
    for n, (i, b) in enumerate(lin):
        end = lin[n + 1][1] if n + 1 < len(lin) else last + 1
        for r in range(b, end): owner[r] = i
    # when did the final lineage become the team's longest for good
    lead = None
    for r in sorted(snap):
        s = snap[r][W]
        if s['king'] not in ids and s['max'] > s['ids'].get(owner.get(r, -1), 0): lead = None
        elif lead is None: lead = r
    R['king_lead_from'] = lead
    R['king_len_at'] = [at(r)[W]['ids'].get(owner.get(r, -1), 0) for r in CK]
    # splits by lineage when big
    R['king_splits'] = [(s['round'], s['L'], s['k'], 'rev' if s['k'] > s['L'] - s['k'] else 'shed') for s in g['splits']
                        if s['parent'] in ids and s['L'] >= 8 and (owner.get(s['round'] - 1) == s['parent'] or owner.get(s['round']) == s['parent'])]
    # ---- king eats by source
    kid_of = lambda e: owner.get(e['round']) == e['id']
    hot = {t for t, (a, b) in gp.items() if b and b <= 10}
    rich = {t for t, (a, b) in gp.items() if b and b <= 50}
    src = collections.Counter(); byph = collections.defaultdict(collections.Counter); feeders = {}
    for e in g['eats']:
        if e['team'] != W or not kid_of(e): continue
        c = e['corpse']; ph = min(e['round'] // 100, 4)
        if not c:
            a, b = gp.get(tuple(e['tile']), (0, 0)); k = f'spawn[{a}-{b}]'
        elif c[1] == W: k = 'own_2-4' if c[3] <= 4 else ('own_5-9' if c[3] <= 9 else 'own_10+')
        else: k = 'enemy'
        src[k] += 1; byph[ph][k] += 1
        if c and c[1] == W: feeders.setdefault(c[0], []).append(e['round'])
    R['king_src'] = dict(src); R['king_src_phase'] = {p: dict(v) for p, v in sorted(byph.items())}
    # ---- king movement
    heads = {}; near = {}
    for mv in g['moves']:
        if owner.get(mv['round']) == mv['id'] and mv['team'] == W:
            heads[mv['round']] = mv['head']
            if mv['near_enemy_head']: near[mv['round']] = mv['near_enemy_head']
    mvst = {}
    for a, b in ((200, 300), (300, 400), (400, 500)):
        hs = [heads[r] for r in range(a, b) if r in heads]
        if len(hs) < 10: continue
        uniq = len(set(hs))
        xs = [h[0] for h in hs]; ys = [h[1] for h in hs]
        d_hot = [min((m.dist(h, t) for t in hot), default=None) for h in hs] if hot else []
        d_rich = [min((m.dist(h, t) for t in rich), default=None) for h in hs]
        en = [near[r][0] for r in range(a, b) if r in near]
        disp = m.dist(hs[0], hs[-1])
        mvst[a] = {'n': len(hs), 'uniq': uniq, 'revisit': round(1 - uniq / len(hs), 2), 'bbox': (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1),
                   'disp100': disp, 'd_hot_med': med(d_hot), 'd_rich_med': med(d_rich),
                   'en_min': min(en) if en else None, 'en_p10': sorted(en)[len(en) // 10] if en else None, 'en_med': med(en),
                   'en_le3_frac': round(sum(1 for x in en if x <= 3) / len(en), 2) if en else None}
    R['king_move'] = mvst
    # ---- big deaths (both sides)
    R['big_deaths'] = [(d['round'], d['team'] == W and 'W' or 'L', d['len'], d['reason'], d.get('killer_len') or d.get('victim_len') or (d['hit'] or {}).get('len'),
                        (d.get('killer_team') or d.get('victim_team') or (d['hit'] or {}).get('team')) == d['team'] and 'ally' or 'enemy')
                       for d in g['deaths'] if d['len'] >= 10]
    # ---- feeders: own deaths whose corpse pearls the king ate
    death_by_id = {d['id']: d for d in g['deaths']}
    head_track = collections.defaultdict(dict)
    for mv in g['moves']: head_track[mv['id']][mv['round']] = mv['head']
    sonar_by = collections.defaultdict(list)
    for s in g['sonars']: sonar_by[s['id']].append(s)
    F = []
    for fid, rs in feeders.items():
        d = death_by_id.get(fid)
        if not d: continue
        r = d['round']; kh = heads.get(r) or heads.get(r - 1) or heads.get(r + 1)
        kid = owner.get(r)
        rec = {'round': r, 'len': d['len'], 'reason': d['reason'], 'eaten_by_king': len(rs), 'drop': (d['len'] + 1) // 2,
               'lag': min(rs) - r, 'age': d['age'], 'move': d.get('move')}
        if kh and d['head']:
            rec['dist'] = m.dist(kh, d['head'])
            k2 = d.get('king_head2')
            if d.get('king') and d['king'][0] == kid and k2 and len(k2) == 2:
                fx, fy = wrapd(m, k2[1], k2[0])
                if abs(fx) + abs(fy) == 1:
                    dx, dy = wrapd(m, k2[0], d['head'])
                    rec['rel'] = (dx * fx + dy * fy, dx * (-fy) + dy * fx)  # (forward, right)
        # approach: distance to king head N rounds before death
        tr = head_track[fid]
        for k in (5, 10, 20, 40):
            h = tr.get(r - k); kk = heads.get(r - k)
            rec[f'd-{k}'] = m.dist(h, kk) if h and kk else None
        # rounds continuously within 6 of king before death
        w = 0
        for k in range(1, 200):
            h = tr.get(r - k); kk = heads.get(r - k)
            if not h or not kk or m.dist(h, kk) > 6: break
            w += 1
        rec['near_rounds'] = w
        ss = [s for s in sonar_by[fid] if r - 10 <= s['round'] <= r]
        rec['sonar10'] = len(ss); rec['sonar_dirs'] = ''.join(s['dir'] for s in ss[-8:])
        F.append(rec)
    R['feeders'] = F
    # all feeding own corpses reaching king - also count own deaths near king (<=4) that king did not eat
    # ---- sonar
    son = collections.Counter(); sv = collections.Counter(); kson = 0; perr = collections.Counter()
    for s in g['sonars']:
        if s['team'] != W: continue
        son[min(s['round'] // 100, 4)] += 1; sv[s['value']] += 1; perr[(s['round'], s['id'])] += 1
        if owner.get(s['round']) == s['id']: kson += 1
    R['sonar'] = {'by_phase': dict(sorted(son.items())), 'distinct': len(sv), 'total': sum(sv.values()), 'king_pings': kson,
                  'pings_per_sender_turn': dict(collections.Counter(perr.values()))}
    # sonar sender profile
    sl = collections.Counter(); samev = 0; turns = collections.defaultdict(set)
    for s in g['sonars']:
        if s['team'] != W: continue
        sl['king' if owner.get(s['round']) == s['id'] else ('L2-4' if (s['len'] or 0) <= 4 else ('L5-9' if s['len'] <= 9 else 'L10+'))] += 1
        turns[(s['round'], s['id'])].add(s['value'])
    R['sonar']['senders'] = dict(sl); R['sonar']['same_value_all_dirs'] = round(sum(1 for v in turns.values() if len(v) == 1) / max(1, len(turns)), 2)
    # loser king fate
    pk = max((r for r in snap), key=lambda r: snap[r][Lt]['max'])
    R['L_peak'] = (snap[pk][Lt]['max'], pk)
    R['L_bigdeaths'] = [(d['round'], d['len'], d['reason'], d.get('killer_len'), d.get('killer_team') == W and 'enemy' or ('ally' if d.get('killer_team') else '-'),
                         d.get('enemy_near', (0, 0, None))[2]) for d in g['deaths'] if d['team'] == Lt and d['len'] >= 12]
    R['W_bigdeaths_enemy'] = [(d['round'], d['len'], d.get('killer_len')) for d in g['deaths'] if d['team'] == W and d['len'] >= 10 and d['reason'] == 'HitHeadToHead' and d.get('killer_team') == Lt]
    R['final_units'] = (fin[W]['n'], fin[Lt]['n']); R['final_lens_W'] = fin[W]['lens'][:8]
    return R


if __name__ == '__main__':
    idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
    out = []
    for mid in sorted(idx):
        try: out.append(analyze(mid, idx[mid]))
        except Exception as ex: print('ERR', mid, ex); raise
    json.dump(out, open(os.path.join(RD, 'kings_metrics.json'), 'w'), ensure_ascii=False, default=str)
    print('ok', len(out))
