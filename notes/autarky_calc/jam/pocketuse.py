"""Pocket utilisation, us vs calc, r0-249. For each pocket-round, 'owner' = team with a head inside, else the team with more heads
within BFS<=3 of the mouth (ties/none = nobody). Count: rounds owned, rounds owned-but-idle (no head inside, >=2 pearls waiting),
eats in the pocket by owner, queue size (owner heads within 3 while idle)."""
import collections
from common import *
from jtl import mouths, bfsd
for g in GAMES:
    S = sim(g); m = S['map']; PK = S['PK']; us = GAMES[g]; th = 'B' if us == 'A' else 'A'
    MO = mouths(m, PK); MD = [bfsd(m, x, 3) for x in MO]
    pocket_of = {u: min(range(4), key=lambda i: m.dist(u, MO[i])) for u in PK}
    R = dict(S['rounds'])
    pe = collections.Counter((e['round'], pocket_of[e['tile']], e['team']) for e in S['eats'] if e['tile'] in PK)
    st = {T: collections.Counter() for T in (us, th)}
    for r in sorted(R):
        if r > 249: break
        for i in range(4):
            ins = collections.Counter(T for j, (t, L, T) in R[r]['heads'].items() if pocket_of.get(t) == i)
            nearc = collections.Counter(T for j, (t, L, T) in R[r]['heads'].items() if t in MD[i] and t not in PK)
            if ins: own = max(ins, key=lambda T: ins[T])
            elif nearc and nearc[us] != nearc[th]: own = us if nearc[us] > nearc[th] else th
            else: continue
            pp = sum(1 for p in R[r]['pearls'] if pocket_of.get(p) == i)
            st[own]['own'] += 1
            if not ins and pp >= 2: st[own]['idle'] += 1; st[own]['queue'] += nearc[own]
            st[own]['eats'] += pe[(r + 1, i, own)]
            st[own]['inside'] += bool(ins)
    for T, nm in ((us, 'us'), (th, 'calc')):
        s = st[T]
        print(g, '%-4s owned %4d rounds, head inside %4d, idle-with>=2-pearls %4d (%.0f%%, mean queue %.1f), eats %4d (%.2f/owned round)' % (
            nm, s['own'], s['inside'], s['idle'], 100.0 * s['idle'] / max(1, s['own']), s['queue'] / max(1, s['idle']), s['eats'], s['eats'] / max(1, s['own'])))
