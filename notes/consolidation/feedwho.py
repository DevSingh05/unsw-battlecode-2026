"""For traced FEED events (CONS_TRACE), who ate the dropped pearls.  feedwho.py REPLAY TRACE_ALL"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tools/midgame'))
import sim2
S = sim2.simulate(sys.argv[1])
fe = {}
for l in open(sys.argv[2]):
    f = l.split()
    if len(f) > 2 and f[2] == 'FEED': fe[int(f[1])] = (int(f[0]), int(f[3][4:]), int(f[4][2:]))
eats = collections.defaultdict(list)
for e in S['eats']:
    if e['corpse']: eats[e['corpse'][0]].append(e)
dead = {d['id']: d for d in S['deaths']}
c = collections.Counter(); lag = []
for i, (r, h, hl) in fe.items():
    d = dead.get(i)
    if not d: c['nodeath'] += 1; continue
    drop = (d['len'] + 1) // 2; c['drop'] += drop; c['feeds'] += 1
    for e in eats[i]:
        who = 'host' if (e['id'] & 1023) == h else ('team_small' if (e['len'] or 0) <= 5 else 'team_big') if e['team'] == d['team'] else 'enemy'
        c[who] += 1
        if who == 'host': lag.append(e['round'] - d['round'])
    c['uneaten'] += drop - len(eats[i])
print(dict(c)); print('host eat lag', collections.Counter(lag).most_common(8))
