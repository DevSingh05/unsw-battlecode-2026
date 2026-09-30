"""King formation on king maps: first round our longest >= 10 / 15, longest at r350/r400/end, vs theirs; per family.
python3 notes/top3/regression/kingform.py"""
import json, os, sys, statistics as st, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
from versions import version, FAMILY
import sim2
L = json.load(open(os.path.join(H, 'ledger_all.json')))
res = collections.defaultdict(list)
for r in sorted(L, key=lambda r: r['at']):
    f = FAMILY[version(r['at'])]
    if f not in ('v30', 'v31') or r['map'] not in ('Portals', 'Slithery Fight', 'Schooltime', 'Queen Of Spades'): continue
    p = os.path.join(ROOT, 'replays/regcheck/%d.replay' % r['game'])
    if not os.path.exists(p): continue
    S = sim2.simulate(p); us = r['side']; th = 'B' if us == 'A' else 'A'
    R = dict(S['rounds']); last = S['last_round']
    if last < 400: continue
    f10 = next((k for k, s in S['rounds'] if s[us]['max'] >= 10), 999)
    t10 = next((k for k, s in S['rounds'] if s[th]['max'] >= 10), 999)
    kd = sum(1 for d in S['deaths'] if d['team'] == us and d['len'] >= 10)
    res[(r['map'], f)].append(dict(g=r['game'], win=bool(r['win']), elo=r['oppElo'], f10=f10, t10=t10, m350=R[350][us]['max'], t350=R[350][th]['max'],
                                  m400=R[400][us]['max'], t400=R[400][th]['max'], kd=kd))
out = {}
for (m, f), X in sorted(res.items()):
    out['%s|%s' % (m, f)] = X
    print('%-16s %s n=%2d W=%2d  first>=10 us %5.0f them %5.0f | noKing@400(<=6) %d | max@350 %4.1f v %4.1f | max@400 %4.1f v %4.1f | our L>=10 deaths/g %.1f' % (
        m, f, len(X), sum(x['win'] for x in X), st.median(x['f10'] for x in X), st.median(x['t10'] for x in X), sum(x['m400'] <= 6 for x in X),
        st.mean(x['m350'] for x in X), st.mean(x['t350'] for x in X), st.mean(x['m400'] for x in X), st.mean(x['t400'] for x in X), st.mean(x['kd'] for x in X)))
json.dump(out, open(os.path.join(H, 'kingform.json'), 'w'), indent=1)
