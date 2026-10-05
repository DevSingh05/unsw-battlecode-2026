"""Aggregate scratch dev5/prof.pkl (prof_dev5.py). usage: python3 agg_dev5.py SIDE OPP [--since ISO] [--until ISO] [--maps a,b]
SIDE/OPP are labels (DEV, VIB, FTM, SSS, Sponge, f1, h1, q1, US = any of our builds). Prints a profile of SIDE in games vs OPP,
with OPP's numbers in the same games for comparison."""
import sys, pickle, collections, statistics as st, math
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
args = sys.argv[1:]
SIDE, OPP = args[0], args[1]
since = args[args.index('--since') + 1] if '--since' in args else ''
until = args[args.index('--until') + 1] if '--until' in args else 'Z'
maps = set(args[args.index('--maps') + 1].split(',')) if '--maps' in args else None
match = lambda lab, want: (lab in OURS) if want == 'US' else (want == 'ANY' or lab == want)
pairs = []
for gid, o in D.items():
    if not o: continue
    mt = o['meta']
    if not (since <= mt['at'] < until): continue
    if maps and mt['map'] not in maps: continue
    for T in 'AB':
        E = 'B' if T == 'A' else 'A'
        if match(mt['lab'][T], SIDE) and match(mt['lab'][E], OPP) and mt['lab'][T] != mt['lab'][E]:
            pairs.append((mt, o[T], o[E], T))
n = len(pairs)
print(f'{SIDE} vs {OPP}: {n} games')
if not n: sys.exit()
med = lambda xs: (round(st.median(xs), 1) if xs else None)
mean = lambda xs: (round(sum(xs) / len(xs), 2) if xs else None)
wins = sum(1 for mt, a, b, T in pairs if mt['winner'] == T)
print('wins', wins, '/', n)
# per map
pm = collections.defaultdict(lambda: [0, 0])
for mt, a, b, T in pairs: pm[mt['map']][0] += mt['winner'] == T; pm[mt['map']][1] += 1
print('per map:', ', '.join(f'{k} {v[0]}/{v[1]}' for k, v in sorted(pm.items())))
# endings
endc = collections.Counter()
for mt, a, b, T in pairs:
    w = 'W' if mt['winner'] == T else 'L'
    if mt['reason'] != 'roundLimit': endc[w + ' elim'] += 1
    elif a['final'][0] != b['final'][0]: endc[w + ' queen'] += 1
    elif a['final'][1] != b['final'][1]: endc[w + ' longest'] += 1
    else: endc[w + ' total'] += 1
print('endings', dict(endc))
print('\n## economy (median; side | opp)')
for key in ('n', 'total', 'max'):
    row = []
    for k in (10, 25, 50, 100, 150, 200, 300, 400, 500):
        xs = [a[key][k] for mt, a, b, T in pairs if a[key][k] is not None and mt['last'] >= k]
        ys = [b[key][k] for mt, a, b, T in pairs if b[key][k] is not None and mt['last'] >= k]
        row.append(f'r{k} {med(xs)}|{med(ys)}')
    print(key, '  '.join(row))
print('\n## unit-round length mix per bucket (side | opp)')
BK = ['r0-49', 'r50-99', 'r100-199', 'r200-299', 'r300-399', 'r400-500']
for b in range(6):
    def sh(idx):
        c = collections.Counter()
        for p in pairs:
            for k, v in p[idx].get('mix', {}).get(b, {}).items(): c[k] += v
        t = sum(c.values()) or 1
        return ' '.join(f"{k}:{100 * c[k] / t:.0f}%" for k in ('L2', 'L3', 'L4-7', 'L8+')) + f' ({t / n:.0f}/g)'
    print(BK[b], sh(1), ' | ', sh(2))
print('\n## kings: #units L>=10 / L>=20 / L>=8 at checkpoints (mean); first round longest >= X (median)')
for idx, nm in ((1, 'side'), (2, 'opp')):
    rr = []
    for k in (100, 200, 300, 400):
        xs = [p[idx]['nkings'].get(k) for p in pairs if p[idx]['nkings'].get(k)]
        if xs: rr.append(f'r{k} ' + '/'.join(str(mean([x[i] for x in xs])) for i in range(3)))
    ff = ' '.join(f'L{th}:{med([p[idx][f"first{th}"] for p in pairs if p[idx][f"first{th}"]])}({sum(1 for p in pairs if p[idx][f"first{th}"])})' for th in (8, 10, 15, 20, 30, 40))
    print(nm, ' '.join(rr), '| first', ff)
print('\n## splits per game by bucket: peel(k=2) / bulk(k>=L-2,L>=5) / mid ; stillborn(life<=1) ; child k hist')
for idx, nm in ((1, 'side'), (2, 'opp')):
    c = collections.Counter(); kh = collections.Counter(); lk = collections.Counter(); sb = 0; tot = 0; qsp = []
    for p in pairs:
        for (r, L, k, isq, ex, ed, life, why) in p[idx]['splits']:
            b = min(5, 0 if r < 50 else 1 if r < 100 else 2 if r < 200 else 3 if r < 300 else 4 if r < 400 else 5)
            kind = 'peel' if k == 2 and L > 4 else ('bulk' if (k >= L - 2 and L >= 5) else ('L4k2' if L == 4 else 'mid'))
            c[(b, kind)] += 1; kh[min(k, 10)] += 1; lk[(min(L, 12), min(k, 10))] += 1; tot += 1
            if life <= 1: sb += 1
    print(nm, 'splits/g', round(tot / n, 1), 'stillborn/g', round(sb / n, 1))
    for b in range(6): print('   ', BK[b], {kk: round(c[(b, kk)] / n, 1) for kk in ('L4k2', 'peel', 'bulk', 'mid')})
    print('    child k hist/g', {k: round(v / n, 1) for k, v in sorted(kh.items())})
    print('    top (L,k)/g', [(lk_, round(v / n, 1)) for lk_, v in lk.most_common(12)])
print('\n## deaths per game (own, non-queen) by reason x bucket; L at death; dist to own king')
for idx, nm in ((1, 'side'), (2, 'opp')):
    c = collections.Counter(); Ls = collections.defaultdict(list); kd = collections.defaultdict(list)
    for p in pairs:
        for d in p[idx]['deaths']:
            if d['q']: continue
            b = 0 if d['round'] < 100 else 1 if d['round'] < 300 else 2
            c[(d['reason'], b)] += 1; Ls[d['reason']].append(d['len'])
            if d['kingd'] is not None: kd[d['reason']].append(d['kingd'])
    for why in sorted({k[0] for k in c}):
        print('   ', nm, f'{why:15s}', 'r<100', round(c[(why, 0)] / n, 1), 'r100-299', round(c[(why, 1)] / n, 1), 'r300+', round(c[(why, 2)] / n, 1),
              'medL', med(Ls[why]), 'L hist', dict(collections.Counter(min(x, 8) for x in Ls[why]).most_common(4)), 'med dist king', med(kd[why]))
print('\n## corpse pearls: own corpses eaten by own king / own queen / own other / enemy (per game), median delay')
for idx, nm in ((1, 'side'), (2, 'opp')):
    c = collections.Counter(); dl = []
    for p in pairs:
        for e in p[idx]['corpse_eats']:
            if e['src_team'] != 'own': continue
            who = 'enemy' if e['eater_team'] == 'en' else ('queen' if e['eater_q'] else 'king' if e['eater_is_king'] else ('own L8+' if (e['eater_len'] or 0) >= 8 else 'own small'))
            c[who] += 1; dl.append(e['delay'])
    print('   ', nm, {k: round(v / n, 1) for k, v in c.most_common()}, 'delay med', med(dl))
    # eats fresh vs corpse per bucket
    ec = collections.Counter()
    for p in pairs:
        for k, v in p[idx]['eats'].items(): ec[k] += v
    print('    eats/g fresh by bucket', [round(ec[(b, 'fresh')] / n) for b in range(6)], 'own-corpse', [round(ec[(b, 'cown')] / n) for b in range(6)], 'enemy-corpse', [round(ec[(b, 'cen')] / n) for b in range(6)])
    print('    fresh eats/g by eater class', {c_: round(ec[('cls', c_, 'fresh')] / n) for c_ in ('L2', 'L3', 'L4-7', 'L8+')})
print('\n## queen')
for idx, nm in ((1, 'side'), (2, 'opp')):
    fs = [p[idx]['q_splits'][0][0] for p in pairs if p[idx]['q_splits']]
    nev = sum(1 for p in pairs if not p[idx]['q_splits'])
    ql = '  '.join(f"r{k} {med([p[idx]['q_len'][k] for p in pairs if p[0]['last'] >= k])}" for k in (25, 50, 100, 200, 300, 400, 500))
    alive = sum(1 for p in pairs if p[idx]['q_death'] is None)
    crown = sum(1 for p in pairs if p[idx]['q_isking'].get(500) and p[idx]['final'][0] >= 15)
    dc = collections.Counter()
    for p in pairs:
        d = p[idx]['q_death']
        if d: dc[(d[1][:9], 'early' if d[0] < 100 else 'mid' if d[0] < 300 else 'late')] += 1
    dr = [p[idx]['q_death'][0] for p in pairs if p[idx]['q_death']]
    qsp = collections.Counter((min(L, 9), k) for p in pairs for (r, L, k, ex) in p[idx]['q_splits'])
    print(nm, f'first split med r{med(fs)} (never {nev}); splits/g {round(sum(len(p[idx]["q_splits"]) for p in pairs) / n, 1)}; (L,k) {qsp.most_common(5)}')
    print('    len', ql, f'| alive at end {alive}/{n}; crowned(L>=15 & king at end) {crown}; death med r{med(dr)}', dict(dc))
    for b in (0, 1, 2):
        print(f'    phase {b}: dist from spawn {med([p[idx]["q_spawnd"].get(b) for p in pairs if p[idx]["q_spawnd"].get(b) is not None])}, nearest enemy head {med([p[idx]["q_enemyd"].get(b) for p in pairs if p[idx]["q_enemyd"].get(b) is not None])}, allies<=4 {med([p[idx]["q_allies4"].get(b) for p in pairs if p[idx]["q_allies4"].get(b) is not None])}')
    print('    queen eats (all/own corpse/fresh) mean', [mean([p[idx]['q_eats'][i] for p in pairs]) for i in range(3)])
print('\n## kills (head-on, by this side)')
for idx, nm in ((1, 'side'), (2, 'opp')):
    K = [k for p in pairs for k in p[idx]['kills']]
    stc = collections.Counter(min(k['steps'], 5) for k in K)
    print(nm, 'kills/g', round(len(K) / n, 1), 'steps', {s: round(v / n, 1) for s, v in sorted(stc.items())},
          'paid', round(sum(1 for k in K if k['paid']) / n, 1), 'paid+ate', round(sum(1 for k in K if k['paid'] and k['ate']) / n, 1),
          'mutual', round(sum(1 for k in K if k['mutual']) / n, 1))
    print('    killer L', {c_: round(sum(1 for k in K if (('L2' if k['kl'] <= 2 else 'L3' if k['kl'] == 3 else 'L4-7' if k['kl'] <= 7 else 'L8+') == c_)) / n, 1) for c_ in ('L2', 'L3', 'L4-7', 'L8+')},
          'victim L', {c_: round(sum(1 for k in K if (('L2' if k['vlen'] <= 2 else 'L3' if k['vlen'] == 3 else 'L4-9' if k['vlen'] <= 9 else 'L10+') == c_)) / n, 1) for c_ in ('L2', 'L3', 'L4-9', 'L10+')},
          'queen kills', sum(1 for k in K if k['vq']), 'king kills', sum(1 for k in K if k['vking'] and not k['vq']), 'len killed/g', round(sum(k['vlen'] for k in K) / n, 1))
    big = [k for k in K if k['vlen'] >= 10]
    print('    vs L10+: n', len(big), 'steps', dict(collections.Counter(k['steps'] for k in big)), 'killerL', dict(collections.Counter(min(k['kl'], 9) for k in big)),
          'approach med dist r-1/-2/-3/-4/-6', [med([k['approach'][i] for k in big if k['approach'][i] is not None]) for i in range(5)])
    print('    paid moves w/o kill/g', round(sum(p[idx]['paid_nokill'] for p in pairs) / n, 1), 'of which ate', round(sum(p[idx]['paid_nokill_eat'] for p in pairs) / n, 1),
          'body kills/g', round(sum(p[idx]['body_kills'] for p in pairs) / n, 1), 'queen body kills', sum(p[idx]['body_kills_q'] for p in pairs))
    por = [p[idx]['portal'] for p in pairs if p[idx]['portal'] is not None]
    if por: print('    portal crossings/g (portal maps)', med(por), 'n', len(por))
print('\n## opening (median): units / total / heads own-half / enemy-half / top-5 lens')
for idx, nm in ((1, 'side'), (2, 'opp')):
    print(nm, '  '.join(f"r{k} {med([p[idx]['open'][k]['n'] for p in pairs if k in p[idx]['open']])}/{med([p[idx]['open'][k]['tot'] for p in pairs if k in p[idx]['open']])}/{med([p[idx]['open'][k]['own'] for p in pairs if k in p[idx]['open']])}/{med([p[idx]['open'][k]['en'] for p in pairs if k in p[idx]['open']])}" for k in (10, 20, 30, 45, 60)))
