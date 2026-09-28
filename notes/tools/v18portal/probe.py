#!/usr/bin/env python3
"""Would the crosser's own ray through the portal, cast at the end of its previous turn from the entrance
tile, have predicted the fatal exit?  Our bot already sends that ray (PORTAL_WARN: on Default every entrance
tile is also an exit tile) but ignores the echo.  Also: how opponents approach portals.

usage (from project root): python3 notes/tools/v18portal/probe.py [ab_v18_Default]
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 else 'ab_v18_Default'
G = pickle.load(open(HERE / f'{name}.pkl', 'rb'))
NG = len(G)


def fatal(r):
    return r['died'] is not None and r['died_step'] == r['k']


for us in (True, False):
    who = 'us' if us else 'them'
    rs = [r for g in G for r in g['recs'] if r['us'] == us and len(r['move']) == 1 and r['age'] > 0]
    c = collections.Counter()
    for r in rs:
        p = r['myping']
        if p is None:
            key = 'no ray through portal last turn'
        else:
            hk = p['hitKind'] or 'none'
            at_exit = p['end'] == r['exit']
            key = 'ray hit %s %s' % (hk, 'AT exit' if at_exit else 'beyond exit') if hk not in ('kelp', 'empty', 'none') else 'ray clean (%s)' % hk
        c[(key, fatal(r))] += 1
    keys = sorted({k for k, _ in c})
    print(f'== {who}: single-step crossings (age>0) {len(rs) / NG:.1f}/g')
    for k in keys:
        n = c[(k, True)] + c[(k, False)]
        print(f'   {k:40s} crossings {n / NG:6.1f}/g  fatal {c[(k, True)] / NG:5.1f}/g  ({100 * c[(k, True)] / max(1, n):4.1f}%)')

# ---- opponents' approach behaviour: at every turn a dragon ENDS on an entrance tile (tile with a portal edge),
# does it cross next turn?  Split by whether the exit was occupied at the end of that turn (only knowable via sonar).
print()
for us in (True, False):
    who = 'us' if us else 'them'
    # use crossings' prev snapshot for exit occupancy at decision; plus direction mix
    rs = [r for g in G for r in g['recs'] if r['us'] == us]
    dirs = collections.Counter(r['dir'] for r in rs)
    pp = collections.Counter()
    for g in G:
        seq = collections.defaultdict(list)
        for r in g['recs']:
            if r['us'] == us:
                seq[r['id']].append(r['round'])
        for i, rr in seq.items():
            for a, b in zip(rr, rr[1:]):
                pp['back<=4' if b - a <= 4 else 'later'] += 1
    by_L = collections.Counter(min(r['L'], 6) for r in rs)
    fat_L = collections.Counter(min(r['L'], 6) for r in rs if fatal(r))
    print(f'{who}: dirs {dict(dirs)}  re-cross within 4 rounds {100 * pp["back<=4"] / max(1, sum(pp.values())):.0f}%')
    print('   crossings/g by L:', ', '.join(f'L{k}{"+" if k == 6 else ""} {by_L[k] / NG:.1f} ({100 * fat_L[k] / max(1, by_L[k]):.0f}% fatal)' for k in sorted(by_L)))
    ah = collections.Counter(min(r['ally_h3_exit'], 3) for r in rs)
    fah = collections.Counter(min(r['ally_h3_exit'], 3) for r in rs if fatal(r))
    print('   own heads within 3 of exit:', ', '.join(f'{k}: {ah[k] / NG:.1f}/g fatal {100 * fah[k] / max(1, ah[k]):.0f}%' for k in sorted(ah)))
    ep = sum(1 for r in rs if r['exit_pearl']); e3 = sum(1 for r in rs if r['exit_pearls3'][0] > 0)
    print(f'   pearl on exit {100 * ep / max(1, len(rs)):.0f}%  pearl within 3 beyond exit {100 * e3 / max(1, len(rs)):.0f}%')
    pre = collections.Counter()
    for r in rs:
        pv = r['prev']
        if pv is None or pv['round'] != r['round'] - 1:
            pre['n/a'] += 1
        else:
            pre['exit occupied at prev turn' if pv['occ'] is not None else 'exit empty at prev turn'] += 1
    print('   ', dict(pre))


# ---- rule simulation on OUR single-step crossings: the echo of last turn's rays decides
def echo_of(g, r):
    """Echo counts the crosser got at the start of round r from all its rays of round r-1 (ours only)."""
    ps = [p for p in g['pings'].get(r['id'], []) if p['round'] == r['round'] - 1]
    e = collections.Counter()
    for p in ps:
        hk = p['hitKind']
        if hk in ('ally', 'allyHead', 'enemy', 'enemyHead', 'kelp'):
            e[hk] += 1
    return ps, e


print('\n== rule simulation (ours, single-step, age>0)')
rules = {
    'R1 head echo (allyHead|enemyHead)>0': lambda e, beyond: e['allyHead'] + e['enemyHead'] > 0,
    'R2 any dragon echo >0': lambda e, beyond: e['allyHead'] + e['enemyHead'] + e['ally'] + e['enemy'] > 0,
    'R3 head echo, or body echo when ray path ends at exit': lambda e, beyond: e['allyHead'] + e['enemyHead'] > 0 or (e['ally'] + e['enemy'] > 0 and beyond == 0),
    'R4 head echo, or body echo when ray path ends <=3 past exit': lambda e, beyond: e['allyHead'] + e['enemyHead'] > 0 or (e['ally'] + e['enemy'] > 0 and beyond <= 3),
}
nrays = collections.Counter(); selfhit = 0
for name_, f in rules.items():
    blk = blk_f = 0; kept_f = 0
    for g in G:
        for r in g['recs']:
            if not r['us'] or len(r['move']) != 1 or r['age'] == 0:
                continue
            ps, e = echo_of(g, r)
            p = r['myping']
            beyond = 99
            if p is not None and r['exit'] in p['path']:
                ix = p['path'].index(r['exit'])
                # tiles after the exit before the ray is stopped by kelp (geometric, dragons ignored)
                beyond = len(p['path']) - ix - 1 if len(p['path']) < 16 else 99
            if name_.startswith('R1'):
                nrays[min(len(ps), 4)] += 1
                if p is not None and p['hitId'] == r['id']:
                    selfhit += 1
            if f(e, beyond):
                blk += 1; blk_f += fatal(r)
            else:
                kept_f += fatal(r)
    print(f'   {name_:55s} blocks {blk / NG:6.1f}/g of which fatal {blk_f / NG:5.1f}/g; fatal left {kept_f / NG:5.1f}/g')
print('   rays sent by crosser on its previous turn:', dict(nrays), ' ray hit own body:', selfhit)
bey = collections.Counter()
for g in G:
    for r in g['recs']:
        p = r['myping']
        if r['us'] and p is not None and r['exit'] in p['path']:
            ix = p['path'].index(r['exit'])
            bey[(r['ent'], r['dir'], len(p['path']) - ix - 1)] += 1
print('   geometric tiles beyond exit per (entrance, dir):', sorted(set((k[1], k[2]) for k in bey)))
