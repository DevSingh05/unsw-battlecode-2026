"""Early war on a map: units (us-them) at r20/40/60/80/100, H2H kills by r100 for/against, per game.
python3 notes/top3/regression/early.py MAP MINELO"""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
from versions import version, FAMILY
import sim2
m_, me = sys.argv[1], int(sys.argv[2])
L = json.load(open(os.path.join(H, 'ledger_all.json')))
agg = collections.defaultdict(list)
for r in sorted(L, key=lambda r: r['at']):
    if r['map'] != m_ or r['oppElo'] < me: continue
    p = os.path.join(ROOT, 'replays/regcheck/%d.replay' % r['game'])
    if not os.path.exists(p): continue
    S = sim2.simulate(p); us = r['side']; th = 'B' if us == 'A' else 'A'; R = dict(S['rounds'])
    def u(k):
        s = R.get(k) or S['rounds'][-1][1]; return '%2d-%2d' % (s[us]['n'], s[th]['n'])
    # head-to-head: who survives (killer = mover). count our H2H deaths where we were the mover vs they
    ours_mover = sum(1 for d in S['deaths'] if d['team'] == us and d['reason'] == 'HitHeadToHead' and d['round'] <= 100 and d['actor'] == d['id'])
    ours_rammed = sum(1 for d in S['deaths'] if d['team'] == us and d['reason'] == 'HitHeadToHead' and d['round'] <= 100 and d['actor'] != d['id'])
    th_mover = sum(1 for d in S['deaths'] if d['team'] == th and d['reason'] == 'HitHeadToHead' and d['round'] <= 100 and d['actor'] == d['id'])
    th_rammed = sum(1 for d in S['deaths'] if d['team'] == th and d['reason'] == 'HitHeadToHead' and d['round'] <= 100 and d['actor'] != d['id'])
    eu = sum(1 for e in S['eats'] if e['team'] == us and e['round'] <= 60); et = sum(1 for e in S['eats'] if e['team'] == th and e['round'] <= 60)
    print('%d %-4s %s %s %-18s units r20 %s r40 %s r60 %s r80 %s r100 %s | eats<=60 %3d-%3d | H2H<=100 our deaths mover %2d rammed %2d, their mover %2d rammed %2d' % (
        r['game'], FAMILY[version(r['at'])], r['side'], 'W' if r['win'] else 'L', r['opp'][:18], u(20), u(40), u(60), u(80), u(100), eu, et, ours_mover, ours_rammed, th_mover, th_rammed))
