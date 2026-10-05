"""Feeding-death anatomy (replays/devtest): for each side's non-H2H non-queen deaths: action (steps, ate), length,
age (stillborn), units alive (cap pressure), hit target team for body deaths, pearls dropped, and who eats them within 10 rounds.
usage: python3 feed_dev5.py SIDE OPP [maxgames]"""
import sys, json, pickle, collections, math
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
SIDE, OPP = sys.argv[1], sys.argv[2]; MX = int(sys.argv[3]) if len(sys.argv) > 3 else 40
m_ = lambda lab, w: (lab in OURS) if w == 'US' else lab == w
C = {'side': collections.Counter(), 'opp': collections.Counter()}; n = 0
for gid, o in sorted(D.items()):
    if not o or n >= MX: continue
    lab = o['meta']['lab']
    Ts = [T for T in 'AB' if m_(lab[T], SIDE) and m_(lab['B' if T == 'A' else 'A'], OPP)]
    if not Ts: continue
    n += 1; T0 = Ts[0]
    g = sim2.simulate(RD + f'{gid}.replay'); rd = dict(g['rounds'])
    acts = {(a['round'], a['id']): a for a in g['moves']}
    born = g['born']
    # pearls dropped per death tile -> eaten by
    eat_by_src = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse']: eat_by_src[(e['corpse'][0], e['corpse'][2])].append(e)
    for x in g['deaths']:
        if x['reason'] == 'HitHeadToHead' or x['id'] <= 1: continue
        who = 'side' if x['team'] == T0 else 'opp'; c = C[who]
        a = acts.get((x['round'], x['id']))
        key = x['reason'][:8]
        c[key] += 1
        s = rd.get(x['round'] - 1)
        units = s[x['team']]['n'] if s else 0
        c[key + ' units>=60'] += units >= 60
        c[key + ' units>=48'] += units >= 48
        c[key + ' age<=1'] += x['age'] <= 1
        c[key + f" L{min(x['len'], 5)}"] += 1
        if a:
            c[key + f" steps{min(a['steps'], 3)}"] += 1
            c[key + ' ate>0'] += a['ate'] > 0
            if a.get('suicide'): c[key + ' explicit-suicide'] += 1
        if x['reason'] == 'HitOtherBody' and x['hit']:
            c[key + ' into ' + ('ally' if x['hit']['team'] == x['team'] else 'enemy')] += 1
        es = eat_by_src.get((x['id'], x['round']), [])
        dropped = math.ceil(x['len'] / 2)
        c[key + ' dropped'] += dropped
        for e in es:
            if e['round'] - x['round'] > 15: continue
            king = rd.get(e['round'] - 1, rd.get(e['round']))[e['team']]['king']
            tag = 'eaten_en' if e['team'] != x['team'] else ('eaten_king' if e['id'] == king else ('eaten_L4+' if (e['len'] or 0) >= 4 else 'eaten_small'))
            c[key + ' ' + tag] += 1
        # nearest enemy head at death
        if x.get('enemy_near'): c[key + ' enemy<=3'] += x['enemy_near'][2] <= 3
print(SIDE, 'vs', OPP, n, 'games')
for who in ('side', 'opp'):
    c = C[who]
    for key in sorted({k.split(' ')[0] for k in c}):
        tot = c[key]
        sub = {k[len(key) + 1:]: round(v / n, 1) for k, v in sorted(c.items()) if k.startswith(key + ' ')}
        print(who, key, 'per game', round(tot / n, 1), sub)
