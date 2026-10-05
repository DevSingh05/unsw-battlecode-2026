"""Decisive moment per game, our builds vs DEV (replays/devtest, scratch dev5/prof.pkl). usage: python3 h2h_dev5.py [L|W|all]
Prints one line per game plus a summary of loss shapes."""
import sys, pickle, collections
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
WANT = sys.argv[1] if len(sys.argv) > 1 else 'L'
shape = collections.Counter(); rows = []
for gid, o in sorted(D.items()):
    if not o: continue
    lab = o['meta']['lab']; Ts = [T for T in 'AB' if lab[T] in OURS]
    if not Ts or 'DEV' not in lab.values(): continue
    T = Ts[0]; E = 'B' if T == 'A' else 'A'; mt = o['meta']; a = o[T]; b = o[E]
    res = 'W' if mt['winner'] == T else 'L'
    if WANT != 'all' and res != WANT: continue
    g = sim2.simulate(RD + f'{gid}.replay'); rd = dict(g['rounds']); last = g['last_round']; m = g['map']
    qi = [i for i in (0, 1) if g['team'][i] == T][0]; eq = 1 - qi
    def qd(i):
        x = next((x for x in g['deaths'] if x['id'] == i), None)
        if not x: return None
        kl = x.get('killer_len') or x.get('victim_len'); st = None; mvs = ''
        if 'killer' in x:
            mv = [q for q in g['moves'] if q['id'] == x['killer'] and q['round'] == x['round']]
            if mv: st = mv[0]['steps']; mvs = ''.join(mv[0]['act'].get('move', []))
        return (x['round'], x['reason'][:8], x['len'], kl, st, mvs)
    col = next((k for k, s in g['rounds'] if s[E]['total'] >= 20 and s[T]['total'] < 0.5 * s[E]['total']), None)
    tot = lambda k, t: rd[k][t]['total'] if k in rd else '-'
    lon = lambda k, t: rd[k][t]['max'] if k in rd else '-'
    big = [(x['round'], x['len'], x.get('killer_len'), x['id'] == qi) for x in g['deaths'] if x['team'] == T and x['len'] >= 10 and x['reason'] == 'HitHeadToHead']
    oq = qd(qi); tq = qd(eq)
    if mt['reason'] != 'roundLimit':
        sh = 'elim'
        dec = f"our queen {oq or 'alive'}; below half their mass r{col}; tot100 {tot(100, T)}v{tot(100, E)}; out r{last}"
    elif a['final'][0] != b['final'][0]:
        sh = 'queen' + ('-ourdead' if a['final'][0] == 0 else '-bothalive' if b['final'][0] else '-theirdead')
        dec = f"queen {a['final'][0]}v{b['final'][0]}; our queen {oq}; theirs {tq}"
    else:
        sh = 'longest'
        late = [x for x in big if x[0] >= 300]
        dec = f"longest {a['final'][1]}v{b['final'][1]} (queens {a['final'][0]}v{b['final'][0]}); tot300 {tot(300, T)}v{tot(300, E)} lg300 {lon(300, T)}v{lon(300, E)} lg400 {lon(400, T)}v{lon(400, E)}; our L10+ rammed r300+: {late}"
    shape[(res, sh)] += 1
    rows.append((mt['map'], gid, mt['lab'][T], res, sh, dec))
for r in sorted(rows): print('|', ' | '.join(str(x) for x in r), '|')
print(dict(shape))
