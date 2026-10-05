"""Crowding per side (our games vs DEV), rounds 100-300 every 10 rounds: mean ally heads within Manhattan 3 of each head,
share of heads with 0 free neighbour tiles (end-of-round bodies), share of L2 heads within 3 of the own king.
usage: python3 crowd_dev5.py [maxgames] [map]"""
import sys, pickle, collections
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import replay_decode as R, sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb')); OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
MX = int(sys.argv[1]) if len(sys.argv) > 1 else 20; MP = sys.argv[2] if len(sys.argv) > 2 else None
C = {'us': collections.Counter(), 'DEV': collections.Counter()}; n = 0
for gid, o in sorted(D.items()):
    if not o or n >= MX: continue
    lab = o['meta']['lab']; Ts = [T for T in 'AB' if lab[T] in OURS]
    if not Ts or 'DEV' not in lab.values() or (MP and o['meta']['map'] != MP): continue
    n += 1; US = Ts[0]
    for r in range(100, 301, 20):
        if r > o['meta']['last']: break
        st = sim2.simulate(RD + f'{gid}.replay', stop=(r, 10 ** 9)) if False else None
    # cheaper: one full pass capturing bodies at chosen rounds
    o2 = R.load(RD + f'{gid}.replay'); m = sim2.Map(o2['map'])
    body = {i: list(p) for i, (t, p) in enumerate(m.dragons)}; team = {i: 'AB'[t] for i, (t, p) in enumerate(m.dragons)}; alive = set(body)
    def measure():
        occ = set()
        for j in alive: occ.update(body[j])
        heads = [(j, body[j][0]) for j in alive]
        for T in 'AB':
            who = 'us' if T == US else 'DEV'; c = C[who]
            hs = [(j, h) for j, h in heads if team[j] == T]
            if not hs: continue
            king = max((j for j, h in hs), key=lambda j: len(body[j]))
            for j, h in hs:
                c['heads'] += 1
                c['ally<=3'] += sum(1 for k, h2 in hs if k != j and m.dist(h, h2) <= 3)
                free = sum(1 for d in 'NESW' if (lambda t: t is not None and t not in occ)(m.step(h, d)))
                c['boxed'] += free == 0; c['free1'] += free == 1
                if len(body[j]) == 2: c['L2'] += 1; c['L2 near king'] += j != king and m.dist(h, body[king][0]) <= 3
    rnd = 0
    for e in o2['events']:
        t = e['t']
        if t == 'roundStart':
            if rnd in range(100, 301, 10): measure()
            rnd = e['round']
        elif t == 'dragonUpdate':
            b = body[e['id']]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']; alive.add(e['child'])
        elif t == 'dragonDeath': alive.discard(e['id'])
print(n, 'games', MP or 'all maps')
for who, c in C.items():
    h = c['heads']
    print(who, f"heads/snapshot {h / (n * 21):.0f}  ally heads within 3: {c['ally<=3'] / h:.2f}  boxed(0 free) {100 * c['boxed'] / h:.1f}%  1 free {100 * c['free1'] / h:.1f}%  L2 share {100 * c['L2'] / h:.0f}%  L2 within 3 of king {100 * c['L2 near king'] / max(1, c['L2']):.1f}%")
