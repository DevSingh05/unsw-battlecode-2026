"""Per-map winner-vs-loser metrics over notes/replays/permap (from permap_fetch.py).
Builds sim caches (*.sim.pkl) in parallel, then prints per-game rows and per-map medians.
Usage: python3 permap_analyze.py [--rows] > out.txt ; also writes permap_metrics.json next to the replays."""
import os, sys, glob, json, pickle, statistics as st
from collections import defaultdict, Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay_sim as S
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/permap')
CHK = [50, 100, 200, 300, 400, 450, 499]

def build(f):
    pk = f + '.sim.pkl'
    if not os.path.exists(pk):
        g = S.simulate(f)
        pickle.dump(g, open(pk, 'wb'))
    return pk

def portal_crossings(m, mv):
    p = mv['head']; n = 0
    for d in mv['act'].get('move', []):
        e = m.side_edge(p, d)
        k, _ = m.edges.get(e, (0, -1))
        q = m.step(p, d)
        if q is None: break
        if k == 2: n += 1
        p = q
    return n

def snap_at(g, r):
    best = None
    for rr, s in g['rounds']:
        if rr <= r: best = s
        else: break
    return best

def team_metrics(g, T):
    m = g['map']; O = 'B' if T == 'A' else 'A'
    res = g['result']; last = g['last_round']
    out = {}
    for r in CHK:
        s = snap_at(g, r) if r <= last else None
        out[f'n{r}'] = s[T]['n'] if s else None
        out[f'max{r}'] = s[T]['max'] if s else None
        out[f'second{r}'] = (s[T]['lens'][1] if s and len(s[T]['lens']) > 1 else 0) if s else None
    out['peak_n'] = max(s[T]['n'] for r, s in g['rounds'])
    out['final_n'] = res[T]['dragonCount']; out['final_max'] = res[T]['longest']
    sp = [x for x in g['splits'] if x['team'] == T]
    fwd = [x for x in sp if not (x['k'] == x['L'] - 2 and x['L'] >= 6)]  # exclude reverse splits (U-turns)
    out['splits'] = len(sp)
    out['split_buckets'] = [sum(1 for x in sp if b <= x['round'] < b + 50) for b in range(0, 500, 50)]
    out['split_sizes'] = Counter(f"{x['L']}>{x['L']-x['k']}+{x['k']}" for x in sp).most_common(4)
    out['share_4_2'] = round(sum(1 for x in sp if x['L'] == 4 and x['k'] == 2) / max(1, len(sp)), 2)
    s42 = [x['round'] for x in sp if x['L'] <= 5 and x['k'] == 2 and x['round'] > 5]
    out['last_small_split'] = max(s42) if s42 else None
    # "splitting stops": first round r such that fewer than 3 small splits happen in [r, end)
    stop = None
    for r in range(0, 500, 10):
        if sum(1 for x in s42 if x >= r) < 3: stop = r; break
    out['split_stop'] = stop
    out['rev_splits'] = sum(1 for x in sp if x['k'] == x['L'] - 2 and x['L'] >= 6)
    # king
    out['r_max10'] = next((r for r, s in g['rounds'] if r >= 20 and s[T]['max'] >= 10), None)
    out['r_max20'] = next((r for r, s in g['rounds'] if r >= 20 and s[T]['max'] >= 20), None)
    # single king: longest >= 2x second and >= 10
    out['r_single_king'] = next((r for r, s in g['rounds'] if s[T]['max'] >= 10 and (len(s[T]['lens']) < 2 or s[T]['max'] >= 2 * s[T]['lens'][1])), None)
    # deaths
    dt = [d for d in g['deaths'] if d['team'] == T]
    out['deaths'] = Counter(d['reason'] for d in dt)
    feed = [d for d in dt if d['reason'] in ('HitSelf', 'HitWall', 'NoValidAction', 'HitOtherBody') and d['len'] <= 4
            and d['round'] >= 200 and d.get('king') and d['king'][1] >= 8 and d['king'][2] <= 4]
    out['feeders'] = len(feed)
    out['feed_first'] = min((d['round'] for d in feed), default=None)
    out['feed_med'] = st.median([d['round'] for d in feed]) if feed else None
    out['feed_reason'] = Counter(d['reason'] for d in feed).most_common(2)
    out['feed_len'] = Counter(d['len'] for d in feed).most_common(3)
    # king corpse eats
    eats = [e for e in g['eats'] if e['team'] == T]
    out['king_own_corpse_eats'] = sum(1 for e in eats if e['corpse'] and e['corpse'][1] == T and (e['len'] or 0) >= 8 and e['round'] >= 250)
    # rams initiated (mover in H2H that killed an enemy)
    rams = [d for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d.get('killer_team') == T and d['team'] != T]
    out['rams'] = len(rams)
    out['ram_buckets'] = [sum(1 for d in rams if b <= d['round'] < b + 100) for b in range(0, 500, 100)]
    out['ram_killer_len'] = st.median([d['killer_len'] for d in rams]) if rams else None
    out['rams_on_big'] = sum(1 for d in rams if d['len'] >= 10)
    out['lost_big_h2h'] = sum(1 for d in dt if d['reason'] == 'HitHeadToHead' and d['len'] >= 10)
    xr = [d['round'] for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d.get('killer_team') and d['killer_team'] != d['team']]
    out['first_contact_ram'] = min(xr) if xr else None
    out['feed_dist'] = Counter(min(d['king'][2], 5) for d in feed)
    out['king_ratio450'] = round(out['max450'] / max(1, out['second450']), 2) if out['max450'] else None
    out['king_gain_400_499'] = (out['max499'] - out['max400']) if out['max499'] is not None and out['max400'] is not None else None
    out['own_h2h'] = sum(1 for d in dt if d['reason'] == 'HitHeadToHead' and d.get('killer_team') == T)
    # pearls
    spawn = [e for e in eats if not e['corpse']]
    hot = [e for e in spawn if e['gap'] == (1, 1)]
    out['eats'] = len(eats); out['spawn_eats'] = len(spawn); out['hot_eats'] = len(hot)
    out['hot_share'] = round(len(hot) / max(1, len(spawn)), 2)
    out['enemy_corpse_eats'] = sum(1 for e in eats if e['corpse'] and e['corpse'][1] != T)
    out['own_corpse_eats'] = sum(1 for e in eats if e['corpse'] and e['corpse'][1] == T)
    mv = [x for x in g['moves'] if x['team'] == T and 'move' in x['act']]
    out['portal_x'] = sum(portal_crossings(m, x) for x in mv)
    out['portal_per_move'] = round(out['portal_x'] / max(1, len(mv)), 3)
    out['sprints'] = sum(1 for x in mv if x['steps'] >= 2)
    return out

def start_dist(m):
    # shortest walk (kelp-aware, through portals) between any A start head and any B start head
    from collections import deque
    A = [pts[0] for t, pts in m.dragons if t == 0]; B = set(pts[0] for t, pts in m.dragons if t == 1)
    D = {a: 0 for a in A}; q = deque(A)
    while q:
        p = q.popleft()
        if p in B: return D[p]
        for d in 'NESW':
            n = m.step(p, d)
            if n is not None and n not in D: D[n] = D[p] + 1; q.append(n)
    return None

def med(v):
    v = [x for x in v if x is not None]
    return (st.median(v) if v else None)

def main():
    fs = sorted(glob.glob(os.path.join(RD, '*.replay')))
    with Pool(8) as p: p.map(build, fs)
    idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
    rows = []; seen = set()
    for f in fs:
        mid = int(os.path.basename(f).split('.')[0])
        if mid not in idx: continue
        g = pickle.load(open(f + '.sim.pkl', 'rb'))
        W = g['result']['winner']
        if W not in ('A', 'B'): continue
        L = 'B' if W == 'A' else 'A'
        sig = (idx[mid]['mapName'], idx[mid]['a']['id'], idx[mid]['b']['id'], g['last_round'], len(g['eats']), len(g['splits']))
        if sig in seen: continue  # deterministic re-runs of the same pairing
        seen.add(sig)
        names = {'A': idx[mid]['a']['name'], 'B': idx[mid]['b']['name']}
        rows.append({'id': mid, 'map': idx[mid]['mapName'], 'end': g['result']['endReason'], 'last': g['last_round'],
                     'W': names[W], 'L': names[L], 'w': team_metrics(g, W), 'l': team_metrics(g, L),
                     'size': (g['map'].w, g['map'].h), 'hot_tiles': sum(1 for v in g['map'].tiles.values() if v == (1, 1)),
                     'portals': sum(1 for v in g['map'].edges.values() if v[0] == 2) // 2, 'start_dist': start_dist(g['map'])})
    json.dump(rows, open(os.path.join(RD, 'permap_metrics.json'), 'w'), ensure_ascii=False, default=str, indent=0)
    bym = defaultdict(list)
    for r in rows: bym[r['map']].append(r)
    for mp, R in bym.items():
        el = [r for r in R if r['end'] == 'teamEliminated']
        print(f"\n=== {mp} {R[0]['size']} hot={R[0]['hot_tiles']} portals={R[0]['portals']} startdist={R[0]['start_dist']} | games {len(R)} | elim {len(el)} rounds {sorted(r['last']+1 for r in el)}")
        if '--rows' in sys.argv:
            for r in R:
                w, l = r['w'], r['l']
                print(f"  {r['id']} {r['W'][:12]:12s} beat {r['L'][:12]:12s} {r['end'][:4]}@{r['last']+1} | n W {[w[f'n{c}'] for c in CHK]} L {[l[f'n{c}'] for c in CHK]} | max W {[w[f'max{c}'] for c in CHK]} L {[l[f'max{c}'] for c in CHK]}")
                print(f"      splitstop W {w['split_stop']} L {l['split_stop']} | feed W {w['feeders']}@{w['feed_first']} L {l['feeders']}@{l['feed_first']} | rams W {w['ram_buckets']} L {l['ram_buckets']} | hot W {w['hot_eats']} L {l['hot_eats']} | portal W {w['portal_x']} L {l['portal_x']} | 1king W {w['r_single_king']} L {l['r_single_king']}")
        for side in 'wl':
            X = [r[side] for r in R]
            def M(k): return med([x[k] for x in X])
            print(f"  {'WIN ' if side=='w' else 'LOSE'} n@{CHK}: {[M(f'n{c}') for c in CHK]}  max: {[M(f'max{c}') for c in CHK]}  2nd: {[M(f'second{c}') for c in CHK]}")
            print(f"       peak_n {M('peak_n')} final_n {M('final_n')} final_max {M('final_max')} | split_stop {M('split_stop')} last_small {M('last_small_split')} share4>2+2 {M('share_4_2')} rev {M('rev_splits')}")
            bk = [med([x['split_buckets'][i] for x in X]) for i in range(10)]
            print(f"       splits/50r {bk} sizes {Counter(s for x in X for s,_ in x['split_sizes'][:2]).most_common(3)}")
            print(f"       max>=10 @{M('r_max10')} max>=20 @{M('r_max20')} single-king @{M('r_single_king')} | feeders {M('feeders')} first {M('feed_first')} med {M('feed_med')} reasons {Counter(k for x in X for k,_ in x['feed_reason']).most_common(2)} king_corpse_eats {M('king_own_corpse_eats')}")
            rb = [med([x['ram_buckets'][i] for x in X]) for i in range(5)]
            print(f"       rams {M('rams')} /100r {rb} killer_len {M('ram_killer_len')} rams_on_L>=10 {M('rams_on_big')} lost_L>=10_h2h {M('lost_big_h2h')} | hot {M('hot_eats')} share {M('hot_share')} | portal_x {M('portal_x')} ({M('portal_per_move')}/move) | own_corpse {M('own_corpse_eats')} enemy_corpse {M('enemy_corpse_eats')} sprints {M('sprints')}")
            fd = Counter(); [fd.update(x['feed_dist']) for x in X]
            print(f"       first cross-team ram {M('first_contact_ram')} | king ratio max/2nd @450 {M('king_ratio450')} | king gain 400->499 {M('king_gain_400_499')} | feeder dist to king {dict(sorted(fd.items()))}")
            dc = Counter(); [dc.update(x['deaths']) for x in X]
            print(f"       deaths total {dict(dc.most_common())}")
if __name__ == '__main__': main()
