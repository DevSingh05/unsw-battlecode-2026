"""Feeding volume on king maps: pearls our longest-5 dragons (len>=10) ate from OUR OWN corpses after r300 (feeding),
per game, v30 vs v31 families; plus final longest us/them.  python3 notes/top3/regression/feedstat.py MAP[,MAP]"""
import json, os, sys, statistics as st, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
from versions import version, FAMILY
import sim2
maps = sys.argv[1].split(',')
L = json.load(open(os.path.join(H, 'ledger_all.json')))
agg = collections.defaultdict(list)
for r in sorted(L, key=lambda r: r['at']):
    f = FAMILY[version(r['at'])]
    if r['map'] not in maps or f not in ('v30', 'v31'): continue
    p = os.path.join(ROOT, 'replays/regcheck/%d.replay' % r['game'])
    if not os.path.exists(p): continue
    S = sim2.simulate(p); us = r['side']; th = 'B' if us == 'A' else 'A'
    if S['last_round'] < 450: continue
    own = sum(1 for e in S['eats'] if e['team'] == us and e['round'] > 300 and (e['len'] or 0) >= 10 and e['corpse'] and e['corpse'][1] == us)
    theirs = sum(1 for e in S['eats'] if e['team'] == th and e['round'] > 300 and (e['len'] or 0) >= 10 and e['corpse'] and e['corpse'][1] == th)
    fin = S['rounds'][-1][1]
    agg[(r['map'], f)].append((own, theirs, fin[us]['max'], fin[th]['max'], bool(r['win']), r['oppElo']))
MINELO = int(os.environ.get("MINELO", "0"))
for (m, f), X in sorted(agg.items()):
    X = [x for x in X if x[5] >= MINELO]
    if not X: continue
    print('%-16s %s n=%2d W=%2d  own-corpse eats by L>=10 after r300: us %.1f them %.1f | final longest %.1f v %.1f' % (
        m, f, len(X), sum(x[4] for x in X), st.mean(x[0] for x in X), st.mean(x[1] for x in X), st.mean(x[2] for x in X), st.mean(x[3] for x in X)))
