"""Were self-inflicted deaths forced? For a sample of HitSelf / ally-body / NoValidAction deaths per side, rebuild the state just
before the unit acted and count free exits (no kelp, no body except the own tail which moves, ally/enemy tails ignored).
usage: python3 forced_dev5.py GID [GID...]"""
import sys, collections
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
import pickle
D = pickle.load(open('/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/prof.pkl', 'rb'))
C = collections.Counter()
for gid in sys.argv[1:]:
    g = sim2.simulate(RD + f'{gid}.replay')
    # replay once more, capturing the state at each self-death actor turn: reuse stop= per death (slow but exact), sample <=40
    ds = [x for x in g['deaths'] if x['id'] > 1 and x['reason'] in ('HitSelf', 'HitOtherBody', 'NoValidAction', 'HitWall') and x['actor'] == x['id']]
    step = max(1, len(ds) // 40)
    for x in ds[::step]:
        st = sim2.simulate(RD + f'{gid}.replay', stop=(x['round'], x['id']))
        m = st['map']; body = st['body']; team = st['team']; i = x['id']
        occ = {}
        for j, b in body.items():
            for k, s in enumerate(b): occ[s] = (j, k == len(b) - 1)
        h = body[i][0]; free = 0; pearl = 0
        for d in 'NESW':
            t = m.step(h, d)
            if t is None: continue
            if t in occ and (occ[t][0] == i or not occ[t][1]): continue
            free += 1; pearl += t in st['pearls']
        units = sum(1 for j in body if team[j] == team[i])
        lab = D[int(gid)]['meta']['lab'][team[i]]; key = ('DEV' if lab == 'DEV' else 'us', x['reason'][:8])
        C[key + ('n',)] += 1; C[key + ('free0',)] += free == 0; C[key + ('free>=2',)] += free >= 2
        C[key + ('L2',)] += len(body[i]) == 2; C[key + ('units>=56',)] += units >= 56
        C[key + ('age<=1',)] += x['age'] <= 1
    print(gid, g['map'].name, 'team of id0 =', g['team'][0], flush=True)
for k in sorted({k[:2] for k in C}):
    n = C[k + ('n',)]
    print(k, 'n', n, {s: f"{100 * C[k + (s,)] / n:.0f}%" for s in ('free0', 'free>=2', 'L2', 'units>=56', 'age<=1')})
