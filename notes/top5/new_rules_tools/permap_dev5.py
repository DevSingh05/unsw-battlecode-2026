"""Per-map table, DEV vs us (scratch dev5/prof.pkl): our wins, endings, median totals r100/r200/r300 (us v DEV), longest r400,
queen alive at end (us / DEV), our queen death median round, our self-feed deaths/g (HitSelf+ally body+wall) vs DEV (NoValid+HitSelf+body)."""
import pickle, collections, statistics as st
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
M = collections.defaultdict(list)
for gid, o in D.items():
    if not o: continue
    lab = o['meta']['lab']
    for T in 'AB':
        E = 'B' if T == 'A' else 'A'
        if lab[T] in OURS and lab[E] == 'DEV': M[o['meta']['map']].append((o['meta'], o[T], o[E], T))
med = lambda xs: (int(st.median(xs)) if xs else '-')
print('| map | us W/n | endings (our view) | total r100 | r200 | r300 | longest r400 | queen alive end us/DEV | our queen death med | self-deaths/g us/DEV |')
print('|---|---|---|---|---|---|---|---|---|---|')
for mp, ps in sorted(M.items()):
    n = len(ps); w = sum(1 for mt, a, b, T in ps if mt['winner'] == T)
    endc = collections.Counter()
    for mt, a, b, T in ps:
        r = 'W' if mt['winner'] == T else 'L'
        if mt['reason'] != 'roundLimit': endc[r + '-elim'] += 1
        elif a['final'][0] != b['final'][0]: endc[r + '-queen'] += 1
        else: endc[r + '-longest'] += 1
    def tot(k, key='total'):
        xs = [a[key][k] for mt, a, b, T in ps if mt['last'] >= k]; ys = [b[key][k] for mt, a, b, T in ps if mt['last'] >= k]
        return f'{med(xs)} v {med(ys)}'
    qa = sum(1 for mt, a, b, T in ps if a['q_death'] is None); qb = sum(1 for mt, a, b, T in ps if b['q_death'] is None)
    qd = med([a['q_death'][0] for mt, a, b, T in ps if a['q_death']])
    sd = lambda r, whys: sum(1 for d in r['deaths'] if not d['q'] and d['reason'] in whys)
    us_sd = sum(sd(a, ('HitSelf', 'HitOtherBody', 'HitWall')) for mt, a, b, T in ps) / n
    dv_sd = sum(sd(b, ('NoValidAction', 'HitSelf', 'HitOtherBody')) for mt, a, b, T in ps) / n
    print(f"| {mp} | {w}/{n} | {', '.join(f'{k} {v}' for k, v in sorted(endc.items()))} | {tot(100)} | {tot(200)} | {tot(300)} | {tot(400, 'max')} | {qa}/{qb} | r{qd} | {us_sd:.0f} / {dv_sd:.0f} |")
