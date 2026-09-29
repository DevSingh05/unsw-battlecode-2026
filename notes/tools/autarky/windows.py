"""Per-window summary of one Autarky game from the focus team's view (us, or the top team).
    python3 notes/tools/autarky/windows.py GAME [W=10] [r0] [r1]
cols: units, total, longest (focus/other) | pocket eats home/away (focus ; other) | open spawn / corpse eats | splits | deaths
death codes: R we rammed, r got rammed, S self, W wall, n nva, A ally body, E enemy body, h ally head-on; digit = length if >=4; lowercase p suffix = in pocket"""
import os, sys, pickle, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
a = sys.argv[1:]; gid = int(a[0]); W = int(a[1]) if len(a) > 1 else 10
r0 = int(a[2]) if len(a) > 2 else 0; r1 = int(a[3]) if len(a) > 3 else 501
R = [r for r in pickle.load(open(os.path.join(H, 'games.pkl'), 'rb')) if r['gid'] == gid]
foc = next((r for r in R if r['grp'] in ('us', 'top')), R[0])
path = [g['path'] for g in collect.games() if g['gid'] == gid][0]
S = sim2.simulate(path); m = S['map']; PK = collect.pockets(m); PID = collect.pocket_ids(PK, m)
F = foc['T']; O = 'B' if F == 'A' else 'A'
home = {F: set(foc.get('home', [])), O: set(next((r.get('home', []) for r in R if r['T'] == O), []))}
print(gid, foc['name'], 'vs', foc['oppname'], 'W' if foc['win'] else 'L', 'focus team', F, 'home pockets', sorted(home[F]), 'last', S['last_round'])
snaps = dict(S['rounds'])
print('window    units   total   max  | pk home/away F ; O  | open sp F/O  corpse F/O | splits F/O | deaths F / O')
for w0 in range(r0, min(r1, S['last_round'] + 1), W):
    w1 = w0 + W; s = snaps.get(min(w1, S['last_round']))
    e = collections.Counter()
    for x in S['eats']:
        if not (w0 <= x['round'] < w1): continue
        T = x['team']
        if x['tile'] in PK: e[(T, 'home' if PID[x['tile']] in home[T] else 'away')] += 1
        elif x['corpse']: e[(T, 'c')] += 1
        else: e[(T, 's')] += 1
    sp = collections.Counter(x['team'] for x in S['splits'] if w0 <= x['round'] < w1)
    dd = {F: '', O: ''}
    for d in S['deaths']:
        if not (w0 <= d['round'] < w1): continue
        T = d['team']; rs = d['reason']
        if rs == 'HitHeadToHead':
            if d['id'] != d['actor']: c = 'r' if d.get('killer_team') != T else 'h'
            else: c = 'R' if d.get('victim_team') != T else 'h'
        elif rs == 'HitOtherBody': c = 'E' if (d.get('hit') and d['hit']['team'] != T) else 'A'
        else: c = {'HitSelf': 'S', 'HitWall': 'W'}.get(rs, 'n')
        dd[T] += c + (str(d['len']) if d['len'] >= 4 else '') + ('p' if d['head'] in PK else '')
    print('%3d-%3d  %2d/%2d  %3d/%3d  %2d/%2d | %2d/%2d ; %2d/%2d | %2d/%2d  %2d/%2d | %2d/%2d | %s / %s' % (
        w0, w1, s[F]['n'], s[O]['n'], s[F]['total'], s[O]['total'], s[F]['max'], s[O]['max'],
        e[(F, 'home')], e[(F, 'away')], e[(O, 'home')], e[(O, 'away')], e[(F, 's')], e[(O, 's')], e[(F, 'c')], e[(O, 'c')], sp[F], sp[O], dd[F], dd[O]))
