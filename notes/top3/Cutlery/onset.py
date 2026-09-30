"""Consolidation onset per round-limit game: split-stop round (first 25-round window from r200 with splits < 35% of the
r150-275 window mean, staying below after), steepest 50-round unit drop start, king at onset and +75 rounds.
Usage: onset.py [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
maps = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
gm = {'cut': 'cut', 'cutvus': 'cut', 'us': 'us', 'usC': 'us', 'cutopp': 'opp', 'usopp': 'opp', 'us31': 'u31'}
res = collections.defaultdict(list)
bp = collections.defaultdict(list)
for x in collect.games():
    if x['grp'] in gm and (not maps or x['map'] in maps): bp[x['path']].append(x)
for p, its in bp.items():
    g = sim2.simulate(p)
    if g['result'].get('endReason') != 'roundLimit': continue
    R = dict(g['rounds'])
    for it in its:
        T = collect.side(it, g); k = (it['map'][:10], gm[it['grp']])
        sp = collections.Counter((s['round'] // 25) * 25 for s in g['splits'] if s['team'] == T)
        base = st.mean([sp[w] for w in range(150, 276, 25)]) or 1
        ss = None
        for w in range(200, 500, 25):
            if all(sp[v] < 0.35 * base for v in range(w, 500, 25) if v <= 475): ss = w; break
        drop = max(range(200, 450, 5), key=lambda r: R[r][T]['n'] - R[r + 50][T]['n'])
        res[k].append((ss, drop, R[drop][T]['max'], R[min(drop + 75, 499)][T]['max'], R[499][T]['max'], R[drop][T]['n'], R[min(drop + 50, 499)][T]['n']))
for k in sorted(res):
    v = res[k]
    print(f'{k[0]:<11}{k[1]:<4} n={len(v):2d} splitstop {st.mean([x[0] or 500 for x in v]):4.0f}  unitdrop@{st.mean([x[1] for x in v]):4.0f} '
          f'(units {st.mean([x[5] for x in v]):3.0f}->{st.mean([x[6] for x in v]):3.0f})  king at drop {st.mean([x[2] for x in v]):4.1f} +75r {st.mean([x[3] for x in v]):4.1f} end {st.mean([x[4] for x in v]):4.1f}')
