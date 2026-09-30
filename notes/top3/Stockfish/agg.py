"""Aggregate metrics.pkl. Usage (from project root):
  python3 notes/top3/Stockfish/agg.py overview|timeline|eats|splits|fight|deaths|king|portal|permap KEY [groups]
Map-avg = mean over maps of per-map means (each map equal weight)."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
GR = ['SF', 'SFo', 'SFu', 'U', 'US', 'USo']


def v(r, k):
    x = r.get(k, 0)
    return 0 if x is None else x


def mapavg(rs, k, f=None):
    bym = collections.defaultdict(list)
    for r in rs:
        x = f(r) if f else v(r, k)
        if x is None: continue
        bym[r['map']].append(x)
    if not bym: return float('nan')
    return st.mean(st.mean(l) for l in bym.values())


def g(name, filt=None):
    return [r for r in rows if r['grp'] == name and (filt is None or filt(r))]


def line(label, fn, groups=GR, fmt='{:7.1f}'):
    print(f'{label:28s}', ' '.join(fmt.format(fn(g(x))) for x in groups))


def hdr(groups=GR):
    print(f'{"":28s}', ' '.join(f'{x:>7s}' for x in groups))


cmd = sys.argv[1] if len(sys.argv) > 1 else 'overview'
if cmd == 'overview':
    hdr()
    line('games', lambda rs: len(rs), fmt='{:7d}')
    line('win', lambda rs: mapavg(rs, 'win', lambda r: 1.0 if r['win'] else 0.0), fmt='{:7.2f}')
    line('elim win', lambda rs: mapavg(rs, 'x', lambda r: 1.0 if r['win'] and r['end'] != 'roundLimit' else 0.0), fmt='{:7.2f}')
    line('elim loss', lambda rs: mapavg(rs, 'x', lambda r: 1.0 if (not r['win']) and r['end'] != 'roundLimit' and r['winner'] in 'AB' else 0.0), fmt='{:7.2f}')
    line('first split', lambda rs: mapavg(rs, 'first_split', lambda r: r['first_split']))
    line('maxunits', lambda rs: mapavg(rs, 'maxunits'))
    line('reach16', lambda rs: mapavg(rs, 'reach16', lambda r: r['reach16'] if r['reach16'] is not None else 500))
    line('reach32', lambda rs: mapavg(rs, 'reach32', lambda r: r['reach32'] if r['reach32'] is not None else 500))
    line('frac hit 64', lambda rs: mapavg(rs, 'r64', lambda r: 1.0 if r['r64'] else 0.0), fmt='{:7.2f}')
    line('sonar/g', lambda rs: mapavg(rs, 'sonar'))
elif cmd == 'timeline':
    hdr()
    for k in ('n', 'tot', 'max', 'sec', 'big', 'small'):
        for r_ in (30, 60, 100, 150, 200, 300, 350, 400, 450, 480, 500):
            line(f'{k}{r_}', lambda rs, kk=f'{k}{r_}': mapavg(rs, kk))
        print()
elif cmd == 'eats':
    hdr()
    for p in range(5):
        for k in ('e', 'efast', 'eco', 'ece', 'ek', 'ekown', 'efk', 'efkown'):
            line(f'{k}{p}', lambda rs, kk=f'{k}{p}': mapavg(rs, kk))
        print()
elif cmd == 'splits':
    hdr()
    for p in range(5):
        for k in ('s', 'srev', 'sk2_', 'sp2_', 'sbig'):
            line(f'{k}{p}', lambda rs, kk=f'{k}{p}': mapavg(rs, kk))
        line(f'mean k {p}', lambda rs, p=p: mapavg(rs, 'x', lambda r: v(r, f'sk{p}') / v(r, f's{p}') if v(r, f's{p}') else None))
        line(f'mean L {p}', lambda rs, p=p: mapavg(rs, 'x', lambda r: v(r, f'sL{p}') / v(r, f's{p}') if v(r, f's{p}') else None))
        print()
    for L in range(4, 13): line(f'split at L={L}', lambda rs, L=L: mapavg(rs, f'sL_{L}'))
elif cmd == 'fight':
    hdr()
    for p in range(5):
        for k in ('ram', 'ramL', 'ramown', 'ramking', 'ramspr', 'ram_ahead', 'ram_behind', 'rammed', 'rammedbig', 'blockkill', 'blockkillL', 'dbodyen', 'spr', 'spr_eat', 'spr_kill', 'spr_die', 'spr_evade'):
            line(f'{k}{p}', lambda rs, kk=f'{k}{p}': mapavg(rs, kk))
        print()
elif cmd == 'deaths':
    hdr()
    cats = ('h2h_enemy', 'h2h_ally', 'body_enemy', 'body_ally', 'self', 'wall', 'novalid', 'trapped')
    for p in range(5):
        line(f'd{p}', lambda rs, kk=f'd{p}': mapavg(rs, kk))
        line(f'dL{p}', lambda rs, kk=f'dL{p}': mapavg(rs, kk))
        for c in cats: line(f'  d{p}_{c}', lambda rs, kk=f'd{p}_{c}': mapavg(rs, kk))
        line(f'  bigdeath{p}', lambda rs, kk=f'bigdeath{p}': mapavg(rs, kk))
        print()
elif cmd == 'king':
    hdr()
    for k in ('king_since', 'king_changes_300', 'max10_at', 'max20_at', 'max30_at', 'max40_at'):
        line(k, lambda rs, kk=k: mapavg(rs, kk, lambda r: r[kk] if r[kk] is not None else 500))
    line('feeddeath', lambda rs: mapavg(rs, 'feeddeath'))
    for p in (2, 3, 4): line(f'feeddeath{p}', lambda rs, kk=f'feeddeath{p}': mapavg(rs, kk))
    line('longest_end', lambda rs: mapavg(rs, 'longest_end'))
    line('n_end', lambda rs: mapavg(rs, 'n_end'))
    line('total_end', lambda rs: mapavg(rs, 'total_end'))
elif cmd == 'portal':
    hdr()
    for p in range(5):
        line(f'x{p}', lambda rs, kk=f'x{p}': mapavg(rs, kk))
        line(f'xd{p}', lambda rs, kk=f'xd{p}': mapavg(rs, kk))
elif cmd == 'permap':
    k = sys.argv[2]; groups = sys.argv[3].split(',') if len(sys.argv) > 3 else GR
    maps = sorted({r['map'] for r in rows})
    print(f'{k:22s}', ' '.join(f'{x:>9s}' for x in groups))
    for mp in maps:
        vals = []
        for x in groups:
            rs = [r for r in rows if r['grp'] == x and r['map'] == mp]
            if not rs: vals.append('        -'); continue
            if k == 'win': vals.append(f'{sum(r["win"] for r in rs):3d}/{len(rs):<3d}   ')
            else:
                RK = k.startswith(('reach', 'r64', 'first_split', 'king_since')) or k.endswith('_at')
                vals.append(f'{st.mean((r.get(k) if r.get(k) is not None else 500) if RK else v(r, k) for r in rs):9.1f}')
        print(f'{mp[:22]:22s}', ' '.join(vals))
