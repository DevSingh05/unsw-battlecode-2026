"""Aggregate metrics.pkl. Map-averaged means (each map weighted equally among maps present for that group).
Usage: python3 agg.py [section] [groups=cheji,uspeer,cvsus,usvc] [maps=all|Default,...]"""
import pickle, os, sys, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
sec = sys.argv[1] if len(sys.argv) > 1 else 'all'
GR = (sys.argv[2] if len(sys.argv) > 2 else 'cheji,cpeer,uspeer,uspeerop,cvsus,usvc').split(',')
MAPS = None if len(sys.argv) <= 3 or sys.argv[3] == 'all' else sys.argv[3].split(',')


def val(r, k):
    v = r.get(k, 0)
    if callable(k): return k(r)
    return 0 if v is None else v


def mavg(g, k, maps=None, raw=False):
    rs = [r for r in rows if r['grp'] == g and (maps is None or r['map'] in maps)]
    by = collections.defaultdict(list)
    for r in rs:
        v = k(r) if callable(k) else r.get(k, 0)
        if v is None: continue
        by[r['map']].append(v)
    if not by: return None
    if raw: return st.mean([x for v in by.values() for x in v])
    return st.mean(st.mean(v) for v in by.values())


def table(title, keys, maps=MAPS):
    print(f'\n== {title}')
    print('%-26s' % 'metric' + ''.join('%10s' % g for g in GR))
    for k in keys:
        name = k if isinstance(k, str) else k[0]
        f = k if isinstance(k, str) else k[1]
        vals = [mavg(g, f, maps) for g in GR]
        print('%-26s' % name[:26] + ''.join(('%10.2f' % v) if v is not None else '%10s' % '-' for v in vals))


def ratio(a, b): return lambda r: (r.get(a, 0) or 0) / max(1, r.get(b, 0) or 0)


PH = range(4)
S = {
    'overview': ['win', ('elim_loss', lambda r: r['end'] == 'teamEliminated' and not r['win']), ('elim_win', lambda r: r['end'] == 'teamEliminated' and r['win']), 'last'],
    'snap': [f'{p}{r}' for r in (30, 60, 100, 200, 300, 400, 450, 500) for p in ('n', 'tot', 'max')],
    'snap2': [f'{p}{r}' for r in (100, 200, 300, 400, 500) for p in ('sec', 'big', 'small')],
    'opening': ['split_r0', 'first_split', 'n20', 'n40', 'n60', 'tot40', 'tot60', 'eat0', 'd0', 'nn30', 'nn60', 'cells60', 'reach8', 'reach16', 'reach32', 'max_units'],
    'eats': [f'eat{p}' for p in PH] + [(f'eat/hr{p}', ratio(f'eat{p}', f'hr{p}')) for p in PH] + [f'eatce{p}' for p in PH] + [f'eatco{p}' for p in PH] + [f'eatdead{p}' for p in PH] + [f'eathot{p}' for p in PH],
    'deaths': [f'd{p}' for p in PH] + [(f'dmeanL{p}', ratio(f'dL{p}', f'd{p}')) for p in PH] + [f'd{p}_{c}' for p in PH for c in ('rammed', 'ram_trade', 'h2h_ally', 'body_enemy', 'body_ally', 'self', 'wall', 'novalid', 'trap', 'chosen', 'dead')],
    'fight': [f'{k}{p}' for p in PH for k in ('ram', 'ramsprint', 'ramahead', 'blockkill')] + [(f'ramvL{p}', ratio(f'ramvL{p}', f'ram{p}')) for p in PH] + [(f'ramaL{p}', ratio(f'ramaL{p}', f'ram{p}')) for p in PH] + ['ram_big', 'ram_smallbig'],
    'sprint': [f'sprint{p}' for p in PH] + [(f'sprint%{p}', lambda r, p=p: 100 * (r.get(f'sprint{p}', 0)) / max(1, r.get(f'mv{p}', 0))) for p in PH] + [f'sprintkill{p}' for p in PH] + [f'sprinteat{p}' for p in PH],
    'splits': [f'split{p}' for p in PH] + [f'splitk{p}_{k}' for p in PH for k in (2, 3, 4, 5)] + [f'splitL{p}_{L}' for p in PH for L in (4, 5, 6, 7, 8, 9)] + [f'splitrev{p}' for p in PH] + [f'splitbig{p}' for p in PH],
    'king': ['fk_len', 'fk_since', 'fk_born', 'king_changes300', 'fk_eat', 'fk_eat_co', 'fk_eat_ce', 'feed_deaths', 'feed_len', 'king_en_dist400', 'king_en_close400'] + [f'bigdeath{p}' for p in PH] + ['bigdeath_rammed', 'bigdeath_ram_trade', 'bigdeath_body_enemy', 'bigdeath_body_ally', 'bigdeath_self', 'bigdeath_wall', 'bigdeath_novalid'],
    'portal': [f'x{p}' for p in PH] + [f'xd{p}' for p in PH],
}
if __name__ == '__main__':
    print('games per group:', {g: sum(1 for r in rows if r['grp'] == g) for g in GR})
    for name, keys in S.items():
        if sec in ('all', name): table(name, keys)
