"""Mean per-window curves over a report.py group (default us-L-strong): units, total, pocket eats, rams, mouth heads.
    python3 avgwin.py [group] [W=20] [R=240]"""
import os, sys, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
grp = sys.argv[1] if len(sys.argv) > 1 else 'us-L-strong'; W = int(sys.argv[2]) if len(sys.argv) > 2 else 20; RR = int(sys.argv[3]) if len(sys.argv) > 3 else 240
sys.argv = ['x', 'none']; import report as RP
paths = {g['gid']: g['path'] for g in collect.games()}
acc = collections.defaultdict(float); n = len(RP.G[grp])
for r in RP.G[grp]:
    S = sim2.simulate(paths[r['gid']]); m = S['map']; PK = collect.pockets(m)
    near = {}
    def mouthd(t):
        if t not in near: near[t] = min(m.dist(t, u) for u in PK)
        return near[t]
    F = r['T']; snaps = dict(S['rounds'])
    for w0 in range(0, RR, W):
        s = snaps.get(min(w0 + W, S['last_round']))
        for T, tag in ((F, 'F'), ('B' if F == 'A' else 'A', 'O')):
            acc[(w0, tag, 'units')] += s[T]['n'] if s else 0
            acc[(w0, tag, 'total')] += s[T]['total'] if s else 0
        for e in S['eats']:
            if w0 <= e['round'] < w0 + W:
                tag = 'F' if e['team'] == F else 'O'
                acc[(w0, tag, 'pk' if e['tile'] in PK else ('corpse' if e['corpse'] else 'spawn'))] += 1
        for d in S['deaths']:
            if w0 <= d['round'] < w0 + W and d['reason'] == 'HitHeadToHead' and d['id'] != d['actor'] and d.get('killer_team') != d['team']:
                acc[(w0, 'F' if d['team'] == F else 'O', 'rammed')] += 1
        for rnd, s2 in S['rounds']:
            if w0 <= rnd < w0 + W:
                for v in s2['heads'].values():
                    if mouthd(v[0]) <= 3: acc[(w0, 'F' if v[2] == F else 'O', 'mouth')] += 1.0 / W
print(grp, 'n', n, '  cols: units F/O | total F/O | pocket eats F/O | open spawn F/O | corpse F/O | got rammed F/O | heads within 3 of a pocket F/O (mean per round)')
for w0 in range(0, RR, W):
    g = lambda t, k: acc[(w0, t, k)] / n
    print(f"r{w0:3d}-{w0 + W:3d}  {g('F', 'units'):4.1f}/{g('O', 'units'):4.1f} | {g('F', 'total'):5.1f}/{g('O', 'total'):5.1f} | {g('F', 'pk'):4.1f}/{g('O', 'pk'):4.1f} | {g('F', 'spawn'):4.1f}/{g('O', 'spawn'):4.1f} | {g('F', 'corpse'):4.1f}/{g('O', 'corpse'):4.1f} | {g('F', 'rammed'):4.1f}/{g('O', 'rammed'):4.1f} | {g('F', 'mouth'):4.1f}/{g('O', 'mouth'):4.1f}")
