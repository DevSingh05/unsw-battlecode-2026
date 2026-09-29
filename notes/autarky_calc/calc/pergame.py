from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
print('gid | dives calc/us | mass out-in per split-dive calc/us | pocket eats calc/us | head-on corpse pearls eaten (r<=350) calc/us | open-spawn eats calc/us | result')
for gm in GAMES:
    if gm['us'] is None: continue
    g = sim(gm['gid']); c = gm['calc']
    X = [e for e in E if e['gid'] == gm['gid']]
    dc = [e for e in X if e['calc']]; du = [e for e in X if not e['calc']]
    mc = st.mean(sum(a[2] for a in e['allsplits']) - e['L0'] for e in dc if e['end'] == 'split')
    mu = st.mean(sum(a[2] for a in e['allsplits']) - e['L0'] for e in du if e['end'] == 'split')
    pc = sum(1 for e in g['eats'] if e['team'] == c and pocket_of(e['tile']) is not None)
    pu = sum(1 for e in g['eats'] if e['team'] != c and pocket_of(e['tile']) is not None)
    h2h = {d['id'] for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d['round'] <= 350}
    cc = sum(1 for e in g['eats'] if e['corpse'] and e['corpse'][0] in h2h and e['team'] == c)
    cu = sum(1 for e in g['eats'] if e['corpse'] and e['corpse'][0] in h2h and e['team'] != c)
    oc = sum(1 for e in g['eats'] if not e['corpse'] and pocket_of(e['tile']) is None and e['team'] == c)
    ou = sum(1 for e in g['eats'] if not e['corpse'] and pocket_of(e['tile']) is None and e['team'] != c)
    res = g['result']
    print('%d | %d/%d | %+.2f/%+.2f | %d/%d | %d/%d | %d/%d | %s r%d, longest %d v %d' % (gm['gid'], len(dc), len(du), mc, mu, pc, pu, cc, cu, oc, ou, res['endReason'], g['last_round'], res[c]['longest'], res['B' if c == 'A' else 'A']['longest']))
