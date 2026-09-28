"""Same metrics as permap_analyze.py, for OUR games in replays/ch1 (challenges vs ranks 16-20).
Usage: python3 permap_ours.py"""
import os, sys, json, pickle
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay_sim as S
from permap_analyze import team_metrics, med
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../replays/ch1')
summ = json.load(open(os.path.join(D, 'summary.json')))
bym = defaultdict(list)
for s in summ:
    f = os.path.join(D, f"{s['id']}.replay")
    if not os.path.exists(f): continue
    pk = f + '.sim.pkl'
    if os.path.exists(pk): g = pickle.load(open(pk, 'rb'))
    else: g = S.simulate(f); pickle.dump(g, open(pk, 'wb'))
    us = s['side']; them = 'B' if us == 'A' else 'A'
    bym[s['map']].append((s, team_metrics(g, us), team_metrics(g, them), g['last_round'] + 1))
for mp, G in sorted(bym.items()):
    rec = ''.join('W' if s['win'] else 'L' for s, *_ in G)
    print(f"\n== {mp}: {rec} vs {[s['opp'][:10] for s,*_ in G]} ends {[e for *_, e in G]}")
    for lab, i in (('US  ', 1), ('THEM', 2)):
        X = [t[i] for t in G]
        M = lambda k: med([x[k] for x in X])
        print(f"  {lab} n@300/400/499 {[M(f'n{c}') for c in (300,400,499)]} max@300/400/450/499 {[M(f'max{c}') for c in (300,400,450,499)]} max>=10@{M('r_max10')} >=20@{M('r_max20')} splitstop {M('split_stop')} feeders {M('feeders')} first {M('feed_first')} rams {M('rams')} hot {M('hot_eats')} ratio450 {M('king_ratio450')} lostbigH2H {M('lost_big_h2h')} own_h2h {M('own_h2h')}")
