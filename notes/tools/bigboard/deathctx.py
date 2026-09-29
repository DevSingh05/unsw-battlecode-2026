#!/usr/bin/env python3
"""Per-death context for notes/23 (BIG + STRONG maps, top-15 games).  -> deathctx.pkl
    python3 notes/tools/bigboard/deathctx.py [--jobs 6]
Per death: team tag, round, len, class, age, static degree of the head tile, pocket (leaf-pruned dead end),
units of the team, parent-split in the last 5 rounds (child len), pearls dropped / re-eaten by own / enemy.
Also per game: every split (L, k, units_before, exits, pocket) and unit-cap rounds.
"""
import collections, os, pickle, sys
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '..', '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
from collect import games, classify
BIG = ['Schooltime', 'Slithery Fight', 'Autarky']; STRONG = ['Trauma', 'Default', 'Prisoners Dilemma']


def pockets(m):
    deg = {}
    nb = {}
    for x in range(m.w):
        for y in range(m.h):
            t = (x, y); ns = [m.step(t, d) for d in 'NESW']; ns = [n for n in ns if n is not None and n != t]
            nb[t] = ns; deg[t] = len(set(ns))
    d = dict(deg); alive = set(deg); q = [t for t in alive if d[t] <= 1]; pk = set()
    while q:
        t = q.pop()
        if t not in alive: continue
        alive.discard(t); pk.add(t)
        for n in set(nb[t]):
            if n in alive:
                d[n] -= 1
                if d[n] <= 1: q.append(n)
    return deg, pk


def run(g):
    try:
        G = simulate(g['path'])
    except Exception as ex:
        return None
    m = G['map']; deg, pk = pockets(m)
    us = g['side']
    tag = lambda T: 'us' if T == us else 'them'
    rs = dict(G['rounds'])
    lastsplit = {}
    for s in G['splits']:
        lastsplit.setdefault(s['parent'], []).append((s['round'], s['k'], s['L']))
    # corpse reclaim: eats with corpse (id, team, round, L)
    rec = collections.defaultdict(lambda: [0, 0])
    for e in G['eats']:
        if e['corpse']:
            did = e['corpse'][0]
            rec[did][0 if e['team'] == e['corpse'][1] else 1] += 1
    D = []
    for d in G['deaths']:
        T = d['team']; snap = rs.get(d['round'] - 1) or rs.get(d['round'])
        units = snap[T]['n'] if snap else None
        ls = [x for x in lastsplit.get(d['id'], []) if d['round'] - x[0] <= 5]
        D.append({'tag': tag(T), 'round': d['round'], 'len': d['len'], 'cls': classify(m, d), 'age': d['age'],
                  'deg': deg.get(d['head']), 'pocket': d['head'] in pk, 'units': units,
                  'split5': ls[-1] if ls else None, 'drop': (d['len'] + 1) // 2, 'own_re': rec[d['id']][0], 'en_re': rec[d['id']][1],
                  'born_by_split': d['id'] in G['parent_of'],
                  'nbrs': tuple(v if isinstance(v, str) else v[0] for v in (d.get('nbrs') or {}).values()),
                  'ally_near': (d.get('ally_near') or (0, 0, 99))[2], 'enemy_near': (d.get('enemy_near') or (0, 0, 99))[2],
                  'reason': d['reason'], 'x': d['head']})
    S = []
    for s in G['splits']:
        S.append({'tag': tag(s['team']), 'round': s['round'], 'L': s['L'], 'k': s['k'], 'units': s['units_before'],
                  'exits': s['exits'], 'enemy_dist': s['enemy_dist']})
    cap = {t: sum(1 for r, sn in G['rounds'] if sn[T]['n'] >= 60) for T, t in ((us, 'us'), ('B' if us == 'A' else 'A', 'them'))}
    return {'game': g['game'], 'map': g['map'], 'win': g['win'], 'top': g['top'], 'deaths': D, 'splits': S, 'cap60': cap,
            'npk': len(pk), 'ntiles': m.w * m.h}


if __name__ == '__main__':
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 6
    gs = [g for g in games() if g['map'] in BIG + STRONG and g['top']]
    with Pool(jobs) as p:
        res = [r for r in p.imap(run, gs, chunksize=2) if r]
    pickle.dump(res, open(os.path.join(H, 'deathctx.pkl'), 'wb'))
    print(len(res))
