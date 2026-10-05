"""Our deaths into ALLY bodies (HitOtherBody): which segment (tail?), what the ally did that round before us
(split / moved / not yet acted / died), ages. usage: python3 allybody_dev5.py LABELSET(US|DEV|VIB..) [maxgames]"""
import sys, pickle, collections
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
W = sys.argv[1]; MX = int(sys.argv[2]) if len(sys.argv) > 2 else 30
C = collections.Counter(); n = 0; ex = []
for gid, o in sorted(D.items()):
    if not o or n >= MX: continue
    Ts = [T for T in 'AB' if ((o['meta']['lab'][T] in OURS) if W == 'US' else o['meta']['lab'][T] == W)]
    if not Ts: continue
    n += 1; T0 = Ts[0]
    g = sim2.simulate(RD + f'{gid}.replay')
    # order of events per round: who split / acted
    splits_r = collections.defaultdict(set)
    for s in g['splits']: splits_r[s['round']].add(s['parent'])
    acted = collections.defaultdict(set)
    for a in g['moves']: acted[a['round']].add(a['id'])
    for x in g['deaths']:
        if x['team'] != T0 or x['reason'] != 'HitOtherBody' or not x['hit'] or x['hit']['team'] != T0: continue
        h = x['hit']; L = h['len']; seg = h['seg']
        pos = 'tail' if seg == L - 1 else ('neck/head' if seg <= 1 else 'mid')
        aid = h['id']
        # did the ally act before us this round? ids act ascending; children appended act later
        before = aid < x['id']
        what = 'split' if aid in splits_r[x['round']] else ('moved' if aid in acted[x['round']] else 'no-move-yet')
        C[(pos, 'ally acted before' if before else 'ally acts after', what)] += 1
        C['n'] += 1; C['age<=1'] += x['age'] <= 1
        C['L%d' % min(x['len'], 4)] += 1
        if len(ex) < 12 and pos == 'tail': ex.append((gid, x['round'], x['id'], x['len'], x['move'], aid, L, what, 'before' if before else 'after'))
print(W, n, 'games; per game:')
for k, v in sorted(C.items(), key=lambda kv: -kv[1]): print('  ', k, round(v / n, 2))
for e in ex: print('  ex', e)
