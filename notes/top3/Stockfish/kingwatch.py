"""Event log of a team's king in a window: king eats (src), own deaths within 4 of king (reason,len,dist), king splits, king moves (steps).
Usage: python3 kingwatch.py REPLAY TEAM R0 R1"""
import os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
p, T, r0, r1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
g = sim2.simulate(p); m = g['map']; RS = dict(g['rounds'])
ev = collections.defaultdict(list)
for e in g['eats']:
    if e['team'] == T and r0 <= e['round'] <= r1:
        s = RS.get(e['round'] - 1); k = s[T]['king'] if s else None
        if e['id'] == k or (e['len'] or 0) >= 10:
            src = 'own' if e['corpse'] and e['corpse'][1] == T else ('EN' if e['corpse'] else 'sp')
            ev[e['round']].append(f"eat[{e['id']} L{e['len']}]{src}{'(d' + str(e['round'] - e['corpse'][2]) + ')' if e['corpse'] else ''}")
for d in g['deaths']:
    if d['team'] == T and r0 <= d['round'] <= r1:
        k = d.get('king')
        if k and k[2] <= 4:
            ev[d['round']].append(f"die[{d['id']} L{d['len']} {d['reason'][:8]} dK{k[2]} free{sum(1 for v in d['nbrs'].values() if v in ('free','pearl'))}]")
    if d['team'] != T and r0 <= d['round'] <= r1 and d['len'] >= 5:
        ev[d['round']].append(f"ENdie[L{d['len']} {d['reason'][:8]}]")
for s in g['splits']:
    if s['team'] == T and r0 <= s['round'] <= r1 and s['L'] >= 6:
        ev[s['round']].append(f"split[{s['parent']} L{s['L']} k{s['k']} ex{s['exits']} en{s['enemy_dist']}]")
for a in g['moves']:
    if a['team'] == T and r0 <= a['round'] <= r1 and a['len_before'] >= 10 and a['steps'] >= 2:
        ev[a['round']].append(f"SPRINT[{a['id']} L{a['len_before']} {''.join(a['act']['move'])} en{a['near_enemy_head'][0] if a['near_enemy_head'] else '-'}]")
for r in range(r0, r1 + 1):
    s = RS.get(r)
    if not s: continue
    k = s[T]['king']
    hd = s['heads'].get(k)
    E = 'B' if T == 'A' else 'A'
    near = sum(1 for j, (h, L, t) in s['heads'].items() if t == T and j != k and hd and m.dist(h, hd[0]) <= 4)
    enear = min((m.dist(h, hd[0]) for j, (h, L, t) in s['heads'].items() if t == E and hd), default=99)
    if ev.get(r) or r % 10 == 0:
        print(f"r{r} n{s[T]['n']} K{k} L{s[T]['max']} @{hd[0] if hd else None} lens{s[T]['lens'][:4]} allies<=4:{near} enemy:{enear} | " + ' '.join(ev.get(r, [])))
