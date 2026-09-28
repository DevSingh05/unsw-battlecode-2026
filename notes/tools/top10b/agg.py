"""Aggregate metrics.pkl. Usage: python3 agg.py [section] [maps,comma]
Sections: overview, deaths, portals, early, end. Per-map per-group means; 'ALL' = mean over maps (equal weight)."""
import pickle, sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
sec = sys.argv[1] if len(sys.argv) > 1 else 'overview'
maps = sys.argv[2].split(',') if len(sys.argv) > 2 else sorted({r['map'] for r in rows})
GR = ('top', 'peer', 'us', 'usopp')
F = {
    'overview': ['n', 'win', 'last', 'n100', 'n200', 'n300', 'n400', 'n500', 'max300', 'max400', 'max500', 'mean300', 'eat0', 'eat1', 'eat2'],
    'deaths': ['d0', 'd1', 'd2', 'd1_h2h_enemy', 'd1_h2h_ally', 'd1_body_ally', 'd1_body_enemy', 'd1_self', 'd1_wall', 'd1_novalid', 'd1_trapped', 'kill1', 'blockkill1', 'd2_feed', 'd2_h2h_enemy', 'd2_h2h_ally', 'd2_body_ally', 'd2_body_enemy', 'd2_self', 'd2_wall', 'd2_trapped'],
    'portals': ['mv1', 'x0', 'x1', 'x2', 'xd1', 'xd2', 'xpp1', 'xd1_HitOtherBody', 'xd1_HitHeadToHead', 'xd1_HitSelf', 'xd1_HitWall'],
    'early': ['first_split', 'reach4', 'reach8', 'reach16', 'n30', 'n40', 'n60', 'tot60', 'max60', 'eat0', 'split0', 'd0', 'd0_h2h_enemy', 'd0_self', 'd0_body_ally', 'nn60', 'cells60', 'kill0'],
    'end': ['max350', 'max400', 'max450', 'max500', 'second500', 'en_max500', 'n350', 'n500', 'tot500', 'king_eat_late', 'd2', 'd2_feed', 'd2_big', 'king_death', 'kill_king', 'kill2', 'blockkill2', 'bigsplit_late', 'sprint2', 'win'],
}[sec]


def val(r, f):
    if f == 'n': return 1
    if f == 'win': return 1.0 if r['win'] else 0.0
    v = r.get(f)
    if v is None: return 0 if (f[0] in 'dxkebs' and f not in ('first_split',)) else None
    return v


def cell(rs, f):
    if f == 'n': return len(rs)
    vs = [val(r, f) for r in rs]; vs = [v for v in vs if v is not None]
    return (st.mean(vs) if vs else None)


def fmt(v):
    if v is None: return '-'
    return f'{v:.2f}' if abs(v) < 10 else f'{v:.0f}'


print('map/grp'.ljust(22) + ''.join(f[:9].rjust(10) for f in F))
allm = collections.defaultdict(list)
for mp in maps:
    for g in GR:
        rs = [r for r in rows if r['map'] == mp and r['grp'] == g]
        if not rs: continue
        vals = [cell(rs, f) for f in F]
        allm[g].append(vals)
        print(f'{mp[:14]:14s} {g:7s}' + ''.join(fmt(v).rjust(10) for v in vals))
print()
for g in GR:
    if not allm[g]: continue
    cols = list(zip(*allm[g]))
    print(f'{"ALL(map-avg)":14s} {g:7s}' + ''.join(fmt(st.mean([x for x in c if x is not None]) if any(x is not None for x in c) else None).rjust(10) for c in cols))
