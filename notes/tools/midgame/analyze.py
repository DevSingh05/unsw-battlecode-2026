"""Mid-game (r60-350) behaviour metrics per (game, team). Usage: python3 analyze.py -> metrics.pkl
Groups: top (current top-10 team), topopp (their >=1850 opponent), us (Cache me outside v15), usopp."""
import json, os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(H, '../../..')
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import sim2
TOP10 = {306, 70, 801, 264, 20, 470, 249, 91, 46, 507}
ORD = {'Default', 'Autarky', 'Devil', 'Trophy', 'Prisoners Dilemma', 'Trauma'}
R0, R1 = 60, 350

def games():
    out = []
    for m in json.load(open(os.path.join(ROOT, 'notes/replays/midgame/index.json'))):
        p = os.path.join(ROOT, f"notes/replays/midgame/{m['id']}.replay")
        for s, T in (('a', 'A'), ('b', 'B')):
            grp = 'top' if m[s]['id'] in TOP10 else 'topopp'
            out.append((p, m['id'], m['mapName'], T, grp, m[s]['name'], m['winner'] == s))
    for x in json.load(open(os.path.join(ROOT, 'replays/v15/ledger.json'))):
        if x['map'] not in ORD - {'Trauma'}: continue
        p = os.path.join(ROOT, f"replays/v15/{x['game']}.replay")
        if not os.path.exists(p): continue
        o = 'B' if x['side'] == 'A' else 'A'
        out.append((p, x['game'], x['map'], x['side'], 'us', 'us', x['win']))
        out.append((p, x['game'], x['map'], o, 'usopp', x['opp'], not x['win']))
    ab = os.path.join(ROOT, 'replays/ab_base/summary.json')
    for x in json.load(open(ab)):
        p = os.path.join(ROOT, f"replays/ab_base/{x['id']}.replay")
        out.append((p, x['id'], x['map'], None, 'us', 'us', x['win'], x))
        out.append((p, x['id'], x['map'], None, 'usopp', x['opp'], not x['win'], x))
    return out

def med(a): return st.median(a) if a else None

def analyze(g, T):
    m = g['map']; E = 'B' if T == 'A' else 'A'
    rounds = dict(g['rounds'])
    deg = {}
    for x in range(m.w):
        for y in range(m.h):
            deg[(x, y)] = sum(1 for d in 'NESW' if m.step((x, y), d) is not None)
    # fast tiles from spawn appearances (non-corpse)
    cnt = collections.Counter(t for r, t, c in g['appears'] if not c)
    fast = {t for t, c in cnt.items() if c >= 8}
    nearfast = set()
    for t in fast:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 2: nearfast.add(m.wrap(t[0] + dx, t[1] + dy))
    open_frac_nearfast = len(nearfast) / (m.w * m.h)
    R = {}
    # A. composition
    for r in (100, 150, 200, 250, 300, 350):
        if r not in rounds: continue
        ls = rounds[r][T]['lens']
        R[f'n{r}'] = len(ls); R[f'tot{r}'] = sum(ls); R[f'max{r}'] = max(ls) if ls else 0
        R[f'le3_{r}'] = sum(1 for l in ls if l <= 3) / len(ls) if ls else None
        R[f'4to6_{r}'] = sum(1 for l in ls if 4 <= l <= 6) / len(ls) if ls else None
        R[f'ge7_{r}'] = sum(1 for l in ls if l >= 7) / len(ls) if ls else None
        R[f'med{r}'] = med(ls)
    # B. splits
    sp = [s for s in g['splits'] if s['team'] == T and R0 <= s['round'] <= R1]
    R['splits'] = len(sp)
    for a, b in ((60, 150), (150, 250), (250, 351)):
        ss = [s for s in sp if a <= s['round'] < b]
        R[f'splitL_{a}'] = [s['L'] for s in ss]; R[f'splitK_{a}'] = [s['k'] for s in ss]
        R[f'splitEn_{a}'] = [s['enemy_dist'] for s in ss]
    # C. spacing / D-I per-move
    own_nn = []; en_nn = []; own_le2 = 0; own_cnt = 0; loc_ratio = []
    for r in range(R0, R1 + 1, 5):
        if r not in rounds: continue
        hs = rounds[r]['heads']
        mine = [v[0] for k, v in hs.items() if v[2] == T]; th = [v[0] for k, v in hs.items() if v[2] == E]
        for i, h in enumerate(mine):
            o = [m.dist(h, x) for j, x in enumerate(mine) if j != i]
            if o: own_nn.append(min(o)); own_cnt += 1; own_le2 += min(o) <= 2
            if th: en_nn.append(min(m.dist(h, x) for x in th))
    R['own_nn_med'] = med(own_nn); R['own_nn_le2'] = own_le2 / own_cnt if own_cnt else None
    R['own_nn_le4'] = sum(1 for x in own_nn if x <= 4) / len(own_nn) if own_nn else None
    R['en_nn_med'] = med(en_nn)
    R['en_nn_le3'] = sum(1 for x in en_nn if x <= 3) / len(en_nn) if en_nn else None
    mv = [a for a in g['moves'] if a['team'] == T and R0 <= a['round'] <= R1]
    steps = sum(a['steps'] for a in mv if not a.get('suicide'))
    turns = len(mv) + len(sp)
    R['turns'] = turns; R['steps'] = steps
    ea = [e for e in g['eats'] if e['team'] == T and R0 <= e['round'] <= R1]
    R['eats'] = len(ea); R['eats_spawn'] = sum(1 for e in ea if not e['corpse'])
    R['eats_owncorpse'] = sum(1 for e in ea if e['corpse'] and e['corpse'][1] == T)
    R['eats_encorpse'] = sum(1 for e in ea if e['corpse'] and e['corpse'][1] == E)
    R['eats_per_turn'] = len(ea) / turns if turns else None
    R['steps_per_eat'] = steps / len(ea) if ea else None
    R['contested'] = sum(1 for e in ea if e['en'] <= 3) / len(ea) if ea else None
    R['contested_spawn'] = (sum(1 for e in ea if e['en'] <= 3 and not e['corpse']) / max(1, R['eats_spawn']))
    R['eat_len'] = collections.Counter(min(e['len'] or 0, 8) for e in ea)
    # opp eats in window for share
    eo = [e for e in g['eats'] if e['team'] == E and R0 <= e['round'] <= R1]
    R['eat_share'] = len(ea) / (len(ea) + len(eo)) if ea or eo else None
    # spawn share
    so = sum(1 for e in eo if not e['corpse'])
    R['spawn_share'] = R['eats_spawn'] / (R['eats_spawn'] + so) if R['eats_spawn'] + so else None
    # F. corpses dropped by T-dragons that died in window: who eats them, delay
    dT = [d for d in g['deaths'] if R0 <= d['round'] <= R1]
    ce = [e for e in g['eats'] if e['corpse'] and R0 <= e['corpse'][2] <= R1]
    # corpses of E eaten: by T vs by E, delay
    for who, lab in ((E, 'encorpse'), (T, 'owncorpse')):
        drops = sum((d['len'] + 1) // 2 for d in dT if d['team'] == who)
        eatenT = [e['round'] - e['corpse'][2] for e in ce if e['corpse'][1] == who and e['team'] == T]
        eatenE = [e['round'] - e['corpse'][2] for e in ce if e['corpse'][1] == who and e['team'] == E]
        R[f'{lab}_drops'] = drops; R[f'{lab}_byT'] = len(eatenT); R[f'{lab}_byE'] = len(eatenE)
        R[f'{lab}_delayT'] = eatenT
    # deaths
    myd = [d for d in dT if d['team'] == T]
    R['deaths'] = collections.Counter(d['reason'] for d in myd)
    R['death_len'] = [d['len'] for d in myd]
    R['h2h_lost'] = sum(1 for d in myd if d['reason'] == 'HitHeadToHead')
    R['kills'] = sum(1 for d in dT if d['team'] == E and d['reason'] == 'HitHeadToHead' and d.get('killer_team') == T)
    R['en_deaths'] = sum(1 for d in dT if d['team'] == E)
    # G. small dragon encounters
    dieat = {d['id']: d['round'] for d in g['deaths']}
    enc = collections.Counter()
    for a in mv:
        ne = a['near_enemy_head']
        if a.get('suicide') or not ne or ne[0] > 3 or a['len_before'] > 4: continue
        if a['enemy_after'] is None and a['died'] is None and not a['killed']:
            kind = 'enemy_gone'
        else:
            dd = (a['enemy_after'] if a['enemy_after'] is not None else 0) - ne[0]
            kind = 'app' if dd < 0 else ('flee' if dd > 0 else 'hold')
        if a['killed'] or a['died'] == 'HitHeadToHead': kind = 'ram'
        died5 = a['id'] in dieat and dieat[a['id']] <= a['round'] + 5
        enc[kind] += 1; enc[kind + '_died5'] += died5
        big = ne[2] >= a['len_before'] + 2
        enc[('vbig_' if big else 'vsm_') + kind] += 1
    R['enc'] = enc
    # H. sprints
    spr = [a for a in mv if a['steps'] >= 2 and not a.get('suicide')]
    R['sprint_frac'] = len(spr) / max(1, len([a for a in mv if not a.get('suicide')]))
    R['sprints'] = len(spr)
    R['sprint_ate'] = sum(1 for a in spr if a['ate'] > 0); R['sprint_kill'] = sum(1 for a in spr if a['killed'])
    R['sprint_died'] = sum(1 for a in spr if a['died'])
    R['sprint_flee'] = sum(1 for a in spr if a['near_enemy_head'] and a['near_enemy_head'][0] <= 4 and a['enemy_after'] and a['enemy_after'] > a['near_enemy_head'][0])
    R['sprint_len'] = [a['len_before'] for a in spr]; R['sprint_steps'] = [a['steps'] for a in spr]
    # I. terrain
    hd = [a['head'] for a in mv]
    R['deg1'] = sum(1 for h in hd if deg[h] <= 1) / max(1, len(hd))
    R['deg2'] = sum(1 for h in hd if deg[h] == 2) / max(1, len(hd))
    R['map_deg12'] = sum(1 for v in deg.values() if v <= 2) / len(deg)
    R['nearfast'] = sum(1 for h in hd if h in nearfast) / max(1, len(hd)); R['map_nearfast'] = open_frac_nearfast
    R['nfast'] = len(fast)
    # J. local outnumbered (E heads within 4 >= own heads within 4 (incl self) + 2)
    outn = collections.Counter()
    for r in range(R0, R1 + 1):
        if r not in rounds or r + 5 not in rounds: continue
        hs = rounds[r]['heads']; fut = rounds[r + 5]['heads']; fut1 = rounds.get(r + 1, {}).get('heads', {})
        mine = [(k, v) for k, v in hs.items() if v[2] == T]; th = [v[0] for v in hs.values() if v[2] == E]
        for k, v in mine:
            ne = sum(1 for x in th if m.dist(v[0], x) <= 4)
            na = sum(1 for k2, v2 in mine if m.dist(v[0], v2[0]) <= 4)
            if ne == 0: continue
            cat = 'out' if ne >= na + 1 else ('even' if ne == na else 'up')
            outn[cat] += 1; outn[cat + '_dead5'] += k not in fut
            if k in fut1 and th:
                d0 = min(m.dist(v[0], x) for x in th)
                th1 = [v2[0] for v2 in fut1.values() if v2[2] == E]
                if th1:
                    d1 = min(m.dist(fut1[k][0], x) for x in th1)
                    outn[cat + '_away'] += d1 > d0; outn[cat + '_closer'] += d1 < d0
    R['outn'] = outn
    # L. lifetime/roles: dragons alive in window: max len reached by r350
    mx = collections.defaultdict(int)
    for r in range(R0, R1 + 1, 5):
        if r in rounds:
            for k, v in rounds[r]['heads'].items():
                if v[2] == T: mx[k] = max(mx[k], v[1])
    R['maxlen_hist'] = collections.Counter(min(v, 10) for v in mx.values())
    return R

def main():
    res = []
    cache = {}
    for item in games():
        p, gid, mp, T, grp, name, win = item[:7]
        if p not in cache:
            try: cache.clear(); cache[p] = sim2.simulate(p)
            except Exception as ex: print('fail', p, ex); continue
        g = cache[p]
        if T is None:  # ab_base: infer side from summary
            x = item[7]; rs = g['result']
            us = None
            for S in 'AB':
                if rs[S]['dragonCount'] == x['us']['dragonCount'] and rs[S]['longest'] == x['us']['longest'] and rs[S]['total'] == x['us']['total']: us = S
            if us is None: print('side?', gid); continue
            T = us if grp == 'us' else ('B' if us == 'A' else 'A')
        R = analyze(g, T)
        R.update(gid=gid, map=mp, T=T, grp=grp, name=name, win=win, end=g['result'].get('endReason'), last=g['last_round'])
        res.append(R); print(gid, mp, grp, name, win, R['eats'], flush=True)
    pickle.dump(res, open(os.path.join(H, 'metrics.pkl'), 'wb'))

if __name__ == '__main__':
    main()
