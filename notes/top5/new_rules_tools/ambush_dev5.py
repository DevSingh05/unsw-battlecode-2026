"""Kill anatomy both ways (our games vs DEV): killer born this round (split ambush: child acts the same round it is born,
from the parent's old tail), reach beyond the plain free+paid reach thanks to pearls eaten on the path, victim queen.
usage: python3 ambush_dev5.py [maxgames]"""
import sys, pickle, collections, math
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb')); OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
MX = int(sys.argv[1]) if len(sys.argv) > 1 else 120
C = {'DEV': collections.Counter(), 'us': collections.Counter()}; n = 0
for gid, o in sorted(D.items()):
    if not o or n >= MX: continue
    lab = o['meta']['lab']; Ts = [T for T in 'AB' if lab[T] in OURS]
    if not Ts or 'DEV' not in lab.values(): continue
    n += 1; US = Ts[0]
    g = sim2.simulate(RD + f'{gid}.replay'); born = g['born']
    for a in g['moves']:
        ks = [k for k in a['killed'] if k[1] != a['team']]
        if not ks: continue
        who = 'us' if a['team'] == US else 'DEV'; c = C[who]
        L = a['len_before']; plain = math.ceil(L / 4) + max(0, L - 2)
        for vid, vt, vl in ks:
            tag = 'Q' if vid <= 1 else ('big' if vl >= 8 else 'small')
            c[tag] += 1
            if born.get(a['id']) == a['round'] and a['id'] > 1: c[tag + ' newborn-killer'] += 1
            if a['steps'] > plain - 0: c[tag + ' beyond-plain-reach(pearls)'] += a['steps'] > plain
            if a['steps'] >= 3: c[tag + ' steps>=3'] += 1
print(n, 'games; per game')
for who, c in C.items():
    print(who, {k: round(v / n, 2) for k, v in sorted(c.items())})
