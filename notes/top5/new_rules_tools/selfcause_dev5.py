"""Self-inflicted (non head-on, non-queen) deaths per side in our games vs DEV, by cause:
stillborn (age<=1) / king-feed (own king within 3) / boxed-by-ally (no free tile, >=1 ally body adjacent) /
boxed-own (no free tile, only own body/kelp) / chose-death (a free tile existed). Neighbours from sim2 death record.
usage: python3 selfcause_dev5.py [maxgames]"""
import sys, pickle, collections
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb')); OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
MX = int(sys.argv[1]) if len(sys.argv) > 1 else 120
C = {'us': collections.Counter(), 'DEV': collections.Counter()}; n = 0
for gid, o in sorted(D.items()):
    if not o or n >= MX: continue
    lab = o['meta']['lab']; Ts = [T for T in 'AB' if lab[T] in OURS]
    if not Ts or 'DEV' not in lab.values(): continue
    n += 1; US = Ts[0]
    g = sim2.simulate(RD + f'{gid}.replay')
    for x in g['deaths']:
        if x['id'] <= 1 or x['reason'] == 'HitHeadToHead': continue
        who = 'us' if x['team'] == US else 'DEV'; c = C[who]
        nb = x.get('nbrs', {})
        free = [d for d, v in nb.items() if v in ('free', 'pearl')]
        ally = [d for d, v in nb.items() if isinstance(v, tuple) and v[0] == 'ally']
        enemy = [d for d, v in nb.items() if isinstance(v, tuple) and v[0] == 'enemy']
        kingd = x['king'][2] if x.get('king') else 99
        if x['age'] <= 1: cause = 'stillborn'
        elif kingd <= 3: cause = 'king-feed'
        elif not free and ally: cause = 'boxed-by-ally'
        elif not free and enemy: cause = 'boxed-by-enemy'
        elif not free: cause = 'boxed-own/kelp'
        else: cause = 'had-free-tile'
        c[cause] += 1; c[cause + ' len'] += x['len']; c['all'] += 1; c['all len'] += x['len']
print(n, 'games; deaths per game (length lost per game)')
for who, c in C.items():
    print(who, ' | '.join(f"{k} {c[k] / n:.1f} ({c[k + ' len'] / n:.0f})" for k in ('all', 'stillborn', 'king-feed', 'boxed-by-ally', 'boxed-by-enemy', 'boxed-own/kelp', 'had-free-tile')))
