#!/usr/bin/env python3
"""Tables for notes/23.  python3 notes/tools/bigboard/report.py [section ...]
sections: list tl terr eats deaths splits gap end king maps
"""
import collections, os, pickle, sys
H = os.path.dirname(os.path.abspath(__file__))
GS = pickle.load(open(os.path.join(H, 'games.pkl'), 'rb'))
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']
STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']
CHK = [25, 50, 100, 150, 200, 300, 400, 500]


def tlv(g, tag, r):
    tl = g[tag]['tl']
    if r - 1 < len(tl):
        return tl[r - 1]
    # game ended early: carry the final state (eliminated team 0)
    f = g[tag]['final'] or {}
    return (f.get('dragonCount', 0), f.get('total', 0), f.get('longest', 0))


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float('nan')


def groups(top=True):
    out = collections.OrderedDict()
    for name, maps in (('BIG', BIG), ('STRONG', STRONG)):
        gs = [g for g in GS if g['map'] in maps and g['top'] == top]
        out[name] = gs
    return out


def sec_list():
    c = collections.defaultdict(lambda: [0, 0, 0, 0])
    for g in GS:
        k = c[g['map']]
        k[0 if g['top'] else 2] += g['win']; k[1 if g['top'] else 3] += 1
    print('map  WxH  area  reach  top W/N  nontop W/N  spawns/g')
    for mp, k in sorted(c.items(), key=lambda kv: -kv[1][0] / max(1, kv[1][1])):
        gs = [g for g in GS if g['map'] == mp]
        g0 = gs[0]
        print('%-18s %2dx%-2d %5d %5d  %2d/%-2d %.2f   %2d/%-2d  %4.0f  startdist %d  startlen %s' % (
            mp, g0['w'], g0['h'], g0['w'] * g0['h'], g0['ntiles'], k[0], k[1], k[0] / max(1, k[1]), k[2], k[3],
            mean(g['spawns'] for g in gs), g0['start_dist'], g0['start_len']))


def sec_tl(top=True, split_win=True):
    for name, gs in groups(top).items():
        for wl in ((True, False) if split_win else (None,)):
            sub = [g for g in gs if wl is None or g['win'] == wl]
            print('%s top=%s win=%s n=%d' % (name, top, wl, len(sub)))
            for what, i in (('units', 0), ('total', 1), ('max', 2)):
                row = []
                for r in CHK:
                    u = mean(tlv(g, 'us', r)[i] for g in sub); t = mean(tlv(g, 'them', r)[i] for g in sub)
                    row.append('%5.1f/%-5.1f' % (u, t))
                print('  %-6s' % what, ' '.join(row))
    print('  cols:', CHK)


def sec_permap_tl():
    for mp in BIG + STRONG:
        sub = [g for g in GS if g['map'] == mp and g['top']]
        print('%s n=%d W=%d' % (mp, len(sub), sum(g['win'] for g in sub)))
        for what, i in (('units', 0), ('total', 1), ('max', 2)):
            row = []
            for r in CHK:
                u = mean(tlv(g, 'us', r)[i] for g in sub); t = mean(tlv(g, 'them', r)[i] for g in sub)
                row.append('%5.1f/%-5.1f' % (u, t))
            print('  %-6s' % what, ' '.join(row))


def sec_terr(top=True):
    R = [25, 50, 75, 100, 150, 200, 300, 400]
    for mp in BIG + STRONG + ['BIG', 'STRONG']:
        sub = [g for g in GS if (g['map'] == mp or (mp == 'BIG' and g['map'] in BIG) or (mp == 'STRONG' and g['map'] in STRONG)) and g['top'] == top]
        print('%-18s n=%d  tile-share / income-share / cover(us) / cover(them)' % (mp, len(sub)))
        for idx, nm in ((0, 'tile'), (1, 'income'), (2, 'cov_us'), (3, 'cov_th')):
            row = []
            for r in R:
                vals = []
                for g in sub:
                    if r not in g['us']['terr']:
                        # ended: eliminated side has 0
                        continue
                    if idx < 2: vals.append(g['us']['terr'][r][idx])
                    elif idx == 2: vals.append(g['us']['terr'][r][2])
                    else: vals.append(g['them']['terr'][r][2])
                row.append('%5.2f' % mean(vals))
            print('   %-7s' % nm, ' '.join(row))
        # expansion and spread
        for nm, T, idx in (('exp_us', 'us', 4), ('exp_th', 'them', 4), ('nn_us', 'us', 5), ('nn_th', 'them', 5),
                           ('home_us', 'us', 0), ('home_th', 'them', 0), ('far_us', 'us', 2), ('far_th', 'them', 2)):
            row = []
            for r in R:
                vals = [g[T]['zonefrac'][r][idx] for g in sub if r in g[T]['zonefrac'] and len(g[T]['zonefrac'][r]) > 5 and g[T]['zonefrac'][r][3] > 0]
                row.append('%5.2f' % mean(vals))
            print('   %-7s' % nm, ' '.join(row))
    print('   cols', R)


def sec_eats(top=True):
    for name, gs in groups(top).items():
        for wl in (True, False, None):
            sub = [g for g in gs if wl is None or g['win'] == wl]
            if not sub: continue
            print('%s win=%s n=%d  eats per game per 100 rounds: us/them' % (name, wl, len(sub)))
            for lab, f in (('all', lambda k: True), ('spawn', lambda k: k[2] == 'spawn'), ('corpse', lambda k: k[2] != 'spawn'),
                           ('home', lambda k: k[1] == 'home'), ('mid', lambda k: k[1] == 'mid'), ('far', lambda k: k[1] == 'far'),
                           ('near25', lambda k: k[3]), ('notnear', lambda k: not k[3]),
                           ('spawn-near', lambda k: k[3] and k[2] == 'spawn'), ('spawn-notnear', lambda k: (not k[3]) and k[2] == 'spawn')):
                row = []
                for ph in range(5):
                    u = mean(sum(v for k, v in g['us']['eats'].items() if k[0] == ph and f(k)) for g in sub)
                    t = mean(sum(v for k, v in g['them']['eats'].items() if k[0] == ph and f(k)) for g in sub)
                    row.append('%5.1f/%-5.1f' % (u, t))
                print('  %-14s' % lab, ' '.join(row))


def dcat(c):
    if c.startswith('portal'): return 'portal'
    if c.startswith('rammed_enemy') or c == 'ram_enemy': return 'headon_enemy'
    if 'ram_ally' in c or c == 'rammed_ally': return 'headon_ally'
    if c.startswith('trapped'): return 'trapped'
    if c.startswith('feed'): return 'feed'
    if c in ('chose_enemy',): return 'into_enemy_body'
    if c in ('chose_ally',): return 'into_ally_body'
    if c in ('chose_self',): return 'chose_self'
    return c


def sec_deaths(top=True):
    PH = [(0, 100), (100, 200), (200, 350), (350, 501)]
    for name, gs in groups(top).items():
        for wl in (True, False):
            sub = [g for g in gs if g['win'] == wl]
            if not sub: continue
            print('%s win=%s n=%d  deaths/g (len lost) per phase us | them' % (name, wl, len(sub)))
            cats = collections.Counter()
            for g in sub:
                for tag in ('us', 'them'):
                    for d in g[tag]['deaths']: cats[dcat(d[2])] += 1
            for c, _ in cats.most_common(9):
                row = []
                for a, b in PH:
                    u = sum(1 for g in sub for d in g['us']['deaths'] if a <= d[0] < b and dcat(d[2]) == c) / len(sub)
                    t = sum(1 for g in sub for d in g['them']['deaths'] if a <= d[0] < b and dcat(d[2]) == c) / len(sub)
                    row.append('%5.1f/%-5.1f' % (u, t))
                print('  %-16s' % c, ' '.join(row))
            # length lost and far-zone deaths
            row = []
            for a, b in PH:
                u = sum(d[1] for g in sub for d in g['us']['deaths'] if a <= d[0] < b) / len(sub)
                t = sum(d[1] for g in sub for d in g['them']['deaths'] if a <= d[0] < b) / len(sub)
                row.append('%5.0f/%-5.0f' % (u, t))
            print('  %-16s' % 'LEN LOST', ' '.join(row))
            row = []
            for a, b in PH:
                u = sum(1 for g in sub for d in g['us']['deaths'] if a <= d[0] < b and not d[5]) / len(sub)
                t = sum(1 for g in sub for d in g['them']['deaths'] if a <= d[0] < b and not d[5]) / len(sub)
                row.append('%5.1f/%-5.1f' % (u, t))
            print('  %-16s' % 'deaths notnear', ' '.join(row))


def sec_splits(top=True):
    for name, gs in groups(top).items():
        for wl in (True, False):
            sub = [g for g in gs if g['win'] == wl]
            if not sub: continue
            row = []
            for ph in range(5):
                u = mean(sum(v for k, v in g['us']['splits'].items() if k[0] == ph) for g in sub)
                t = mean(sum(v for k, v in g['them']['splits'].items() if k[0] == ph) for g in sub)
                row.append('%5.1f/%-5.1f' % (u, t))
            print('%-7s win=%-5s n=%2d splits/100r us/them' % (name, wl, len(sub)), ' '.join(row))


def gap_round(g, key=1, frac=0.2, mn=8):
    tu = g['us']['tl']; tt = g['them']['tl']
    n = min(len(tu), len(tt))
    first = None
    for r in range(10, n):
        u = tu[r][key]; t = tt[r][key]
        if t - u >= max(mn, frac * max(u, 1)):
            if all(tt[q][key] >= tu[q][key] for q in range(r, n)):
                return r + 1
    return None


def sec_gap(top=True):
    for name, gs in groups(top).items():
        L = [g for g in gs if not g['win']]
        rs = [gap_round(g) for g in L]
        rs2 = [gap_round(g, key=0, frac=0.25, mn=4) for g in L]
        have = sorted(r for r in rs if r)
        print('%s losses n=%d: total-length gap opens (never closed) in %d; round quartiles %s' % (
            name, len(L), len(have), [have[int(q * (len(have) - 1))] for q in (0, .25, .5, .75, 1)] if have else None))
        have2 = sorted(r for r in rs2 if r)
        print('   units gap: %d; quartiles %s' % (len(have2), [have2[int(q * (len(have2) - 1))] for q in (0, .25, .5, .75, 1)] if have2 else None))
        for mp in sorted(set(g['map'] for g in L)):
            x = sorted(r for g, r in zip(L, rs) if g['map'] == mp and r)
            print('     %-18s %s' % (mp, x))


def sec_end(top=True):
    for name, gs in groups(top).items():
        for wl in (True, False):
            sub = [g for g in gs if g['win'] == wl]
            if not sub: continue
            el = [g for g in sub if g['end'] != 'roundLimit']
            rl = [g for g in sub if g['end'] == 'roundLimit']
            print('%-7s win=%-5s n=%2d elim %2d (mean end r%.0f)  roundlimit %2d: longest us/them %.1f/%.1f total %.0f/%.0f units %.1f/%.1f' % (
                name, wl, len(sub), len(el), mean(g['last'] for g in el), len(rl),
                mean(g['us']['final']['longest'] for g in rl), mean(g['them']['final']['longest'] for g in rl),
                mean(g['us']['final']['total'] for g in rl), mean(g['them']['final']['total'] for g in rl),
                mean(g['us']['final']['dragonCount'] for g in rl), mean(g['them']['final']['dragonCount'] for g in rl)))


def first_reach(tl, L):
    for i, x in enumerate(tl):
        if x[2] >= L: return i + 1
    return None


def sec_king(top=True):
    for name, gs in groups(top).items():
        rl = [g for g in gs if g['end'] == 'roundLimit']
        for wl in (True, False):
            sub = [g for g in rl if g['win'] == wl]
            if not sub: continue
            row = []
            for L in (8, 12, 16, 20, 30):
                u = [first_reach(g['us']['tl'], L) or 600 for g in sub]
                t = [first_reach(g['them']['tl'], L) or 600 for g in sub]
                row.append('L%d r%.0f/%.0f' % (L, sorted(u)[len(u) // 2], sorted(t)[len(t) // 2]))
            # king share of mass at 450
            ks = mean(tlv(g, 'us', 450)[2] / max(1, tlv(g, 'us', 450)[1]) for g in sub)
            kt = mean(tlv(g, 'them', 450)[2] / max(1, tlv(g, 'them', 450)[1]) for g in sub)
            print('%-7s roundlimit win=%-5s n=%2d median first round: %s  king/total@450 %.2f/%.2f' % (name, wl, len(sub), '  '.join(row), ks, kt))


if __name__ == '__main__':
    secs = sys.argv[1:] or ['list', 'tl', 'terr', 'eats', 'deaths', 'splits', 'gap', 'end', 'king']
    top = '--nontop' not in secs
    secs = [s for s in secs if s != '--nontop']
    for s in secs:
        print('=' * 20, s, 'top' if top else 'NONTOP')
        f = globals()['sec_' + s]
        f() if s in ('list', 'permap_tl') else f(top)
