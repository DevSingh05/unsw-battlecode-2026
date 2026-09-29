"""Risk of diving with an enemy head near the mouth: for every pocket entry (all teams, all games), the fate of the
diver + its split child within 8 rounds, by the nearest enemy head distance at entry.  python3 entryrisk.py"""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
sys.argv = ['x', 'none']; import report as RP
paths = {g['gid']: g['path'] for g in collect.games()}
C = collections.defaultdict(collections.Counter)
done = set()
for grp in ['us-L-strong', 'strong-W-vs-us', 'us-W-weak', 'top-W', 'top-L', 'topopp-L']:
    for r in RP.G[grp]:
        S = sim2.simulate(paths[r['gid']]); m = S['map']; PK = collect.pockets(m)
        deaths = {d['id']: d for d in S['deaths']}
        kids = collections.defaultdict(list)
        for s in S['splits']: kids[s['parent']].append(s)
        for e in r['episodes']:
            if e['out'] != 'pump' or e['r0'] < 40: continue
            b = 'en<=2' if e['en'] <= 2 else ('en3-4' if e['en'] <= 4 else 'en5+')
            ch = [s for s in kids[e['id']] if s['round'] == e['r1']]
            cd = deaths.get(ch[0]['child']) if ch else None
            cat = 'ok'
            if cd and cd['round'] - e['r1'] <= 8:
                cat = 'child_rammed' if cd['reason'] == 'HitHeadToHead' else ('child_body' if cd['reason'] == 'HitOtherBody' else 'child_other')
            C[(grp, b)][cat] += 1; C[(grp, b)]['n'] += 1
            C[(grp, b)]['gain'] += e['k'] - e['L0'] - (e['k'] if cat != 'ok' else 0)
for k in sorted(C):
    c = C[k]; n = c['n']
    print(f"{k[0]:15s} {k[1]:6s} n={n:4d}  child dies<=8r: rammed {100 * c['child_rammed'] / n:4.1f}% body {100 * c['child_body'] / n:4.1f}% other {100 * c['child_other'] / n:4.1f}%  mean net {c['gain'] / n:+.2f}")
