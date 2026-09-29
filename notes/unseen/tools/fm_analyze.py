#!/usr/bin/env python3
"""Failure mining for v24 on unseen maps (single-game replays from tools/arena.py).

    python3 notes/unseen/tools/fm_analyze.py notes/unseen/replays/fm [--us v24] [-v]

Replay names are <map>_<seed>_<botA>_vs_<botB>.replay; our side is whichever bot name contains --us.
Per game: result, units/longest/total timeline, death classes for our side, king (longest) deaths,
portal crossings, head coverage, eats per phase, idle dragon-turns.
Death classes (our dragons only):
  feed        r>=300, len<=5, died within cheb 3 of our king (>=8)  -> deliberate feeding
  merge       len>=6, r>=400, HitSelf/HitOtherBody into own team    -> deliberate late merge
  portal      fatal step crossed a portal edge
  trapped     mover had no free/pearl neighbour
  chose_X     mover had a free neighbour but died anyway (X = reason)
  rammed      killed on another dragon's turn (head-on by mover)
  pump_tip    len 2, HitWall/HitSelf with no free neighbour right after a split (pocket-pump parent)
"""
import collections, glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate

def classify(d, m, G, side, kinglen_at):
    nb = d.get('nbrs', {})
    free = [k for k, v in nb.items() if v in ('free', 'pearl')]
    r = d['round']
    kl = kinglen_at(r)
    if d['actor'] != d['id']:
        return 'rammed' if d['reason'] == 'HitHeadToHead' else 'killed_other'
    mv = d.get('move') or ''
    k = d.get('step_failed', 1) - 1
    if mv and k < len(mv):
        e = m.side_edge(d['head'], mv[k])
        if m.edges.get(e, (0, -1))[0] == 2:
            return 'portal_' + d['reason']
    king = d.get('king')
    if r >= 300 and d['len'] <= 5 and king and king[1] >= 8 and king[3] <= 3:
        return 'feed'
    hit = d.get('hit')
    if d['len'] >= 6 and r >= 400 and d['reason'] in ('HitSelf', 'HitOtherBody') and (not hit or hit['team'] == side):
        return 'merge'
    if not free:
        if d['len'] == 2:
            return 'trapped_L2'
        return 'trapped_' + d['reason']
    if d['reason'] == 'HitHeadToHead':
        return 'chose_headon'
    if d['reason'] == 'HitOtherBody' and hit:
        return 'chose_body_' + ('ally' if hit['team'] == side else 'enemy')
    return 'chose_' + d['reason']


def analyze(path, us, verbose=False):
    base = os.path.basename(path)[:-7]
    a, b = base.split('_vs_')
    side = 'A' if us in a.split('_', 2)[-1] or (us in a and us not in b) else 'B'
    # map name is before _<seed>_
    G = simulate(path); m = G['map']; opp = 'B' if side == 'A' else 'A'
    res = G['result']
    rows = dict(G['rounds'])
    def kinglen_at(r):
        s = rows.get(r) or rows.get(max(k for k in rows if k <= r))
        return s[side]['max']
    out = {'path': path, 'map': m.name, 'side': side, 'win': res.get('winner') == side, 'end': res.get('endReason'),
           'last': G['last_round'], 'res': res}
    tl = []
    for r in (50, 100, 150, 200, 250, 300, 350, 400, 450, 500):
        ks = [k for k in rows if k <= r]
        if not ks: continue
        s = rows[max(ks)]
        tl.append((r, s[side]['n'], s[side]['max'], s[side]['total'], s[opp]['n'], s[opp]['max'], s[opp]['total']))
    out['timeline'] = tl
    C = collections.Counter(); CL = collections.Counter(); ex = collections.defaultdict(list)
    for d in G['deaths']:
        if d['team'] != side: continue
        c = classify(d, m, G, side, kinglen_at)
        bucket = 'L2-3' if d['len'] <= 3 else ('L4-7' if d['len'] <= 7 else 'L8+')
        C[c] += 1; CL[(c, bucket)] += 1
        if len(ex[c]) < 3: ex[c].append((d['round'], d['id'], d['len'], d['head']))
    out['deaths'] = C; out['deathsL'] = CL; out['ex'] = ex
    # opponent death classes, for comparison
    CO = collections.Counter()
    for d in G['deaths']:
        if d['team'] == opp: CO[classify(d, m, G, opp, lambda r: rows[max(k for k in rows if k <= r)][opp]['max'])] += 1
    out['odeaths'] = CO
    # king (our longest) life: the largest dragon length ever reached and big deaths
    big = [(d['round'], d['id'], d['len'], classify(d, m, G, side, kinglen_at), d['head']) for d in G['deaths'] if d['team'] == side and d['len'] >= 8]
    out['bigdeaths'] = big
    peak = max((s[side]['max'] for _, s in G['rounds']), default=0)
    opeak = max((s[opp]['max'] for _, s in G['rounds']), default=0)
    out['peak'] = (peak, opeak)
    # portal crossings (our side) + deaths on crossing
    cross = 0; crossdie = 0; crossL = collections.Counter()
    for mv in G['moves']:
        if mv['team'] != side or 'move' not in mv['act']: continue
        p = mv['head']
        for st in mv['act']['move']:
            e = m.side_edge(p, st)
            if m.edges.get(e, (0, -1))[0] == 2:
                cross += 1; crossL['L2-3' if mv['len_before'] <= 3 else 'L4+'] += 1
                if mv.get('died'): crossdie += 1
            np_ = m.step(p, st)
            if np_ is None: break
            p = np_
    out['cross'] = (cross, crossdie, dict(crossL))
    # opponent crossings
    oc = 0
    for mv in G['moves']:
        if mv['team'] != opp or 'move' not in mv['act']: continue
        p = mv['head']
        for st in mv['act']['move']:
            if m.edges.get(m.side_edge(p, st), (0, -1))[0] == 2: oc += 1
            np_ = m.step(p, st)
            if np_ is None: break
            p = np_
    out['ocross'] = oc
    # coverage: fraction of pearl-capable tiles our heads ever stood on, by r100/r250/r500
    cap = [t for t, (lo, hi) in m.tiles.items() if hi > 0]
    ntiles = m.w * m.h
    seen = set(); cov = {}
    for mv in G['moves']:
        if mv['team'] == side and mv.get('head_after'):
            seen.add(mv['head_after'])
        for R in (100, 250, 500):
            if mv['round'] >= R and R not in cov: cov[R] = len(seen) / ntiles
    for R in (100, 250, 500):
        cov.setdefault(R, len(seen) / ntiles)
    # vision coverage (7x7 around heads)
    vis = set(); vcov = {}
    for mv in G['moves']:
        if mv['team'] == side and mv.get('head_after'):
            hx, hy = mv['head_after']
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    vis.add(((hx + dx) % m.w, (hy + dy) % m.h))
        for R in (50, 100, 250):
            if mv['round'] >= R and R not in vcov: vcov[R] = len(vis) / ntiles
    out['cov'] = cov; out['vcov'] = vcov
    # eats per phase
    E = collections.Counter(); EO = collections.Counter()
    for e in G['eats']:
        ph = 'r0-99' if e['round'] < 100 else ('r100-299' if e['round'] < 300 else 'r300+')
        if e['team'] == side: E[ph] += 1
        elif e['team'] == opp: EO[ph] += 1
    out['eats'] = (dict(E), dict(EO))
    # corpse eats
    out['corpse'] = (sum(1 for e in G['eats'] if e['team'] == side and e['corpse']), sum(1 for e in G['eats'] if e['team'] == opp and e['corpse']))
    # idle: our dragon-turns in r50-300 where the dragon has not eaten for >= 30 rounds
    last_eat = {}; born = G['born']; idle = 0; turns = 0
    eat_by = collections.defaultdict(list)
    for e in G['eats']: eat_by[e['id']].append(e['round'])
    for mv in G['moves']:
        if mv['team'] != side or not (50 <= mv['round'] < 300): continue
        i = mv['id']; turns += 1
        le = max([r for r in eat_by[i] if r <= mv['round']] + [born.get(i, 0)])
        if mv['round'] - le >= 30: idle += 1
    out['idle'] = (idle, turns)
    # splits
    sp = [s for s in G['splits'] if s['team'] == side]
    so = [s for s in G['splits'] if s['team'] == opp]
    out['splits'] = (len(sp), len(so), collections.Counter((s['L'], s['k']) for s in sp).most_common(4))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    us = 'v24'
    if '--us' in sys.argv: us = sys.argv[sys.argv.index('--us') + 1]; args = [a for a in args if a != us]
    paths = []
    for a in args:
        paths += sorted(glob.glob(os.path.join(a, '**', '*.replay'), recursive=True)) if os.path.isdir(a) else [a]
    tot = collections.Counter(); totO = collections.Counter(); n = 0
    for p in paths:
        o = analyze(p, us)
        n += 1
        print('=' * 100)
        print(os.path.relpath(p, ROOT), 'side', o['side'], 'WIN' if o['win'] else 'LOSS', o['end'], o['last'], 'final', {k: o['res'][k] for k in 'AB'})
        print('  peak longest us/them', o['peak'], ' splits us/them', o['splits'][:2], o['splits'][2])
        print('  r   n  max tot | n  max tot')
        for t in o['timeline']: print('  %3d %3d %3d %4d | %3d %3d %4d' % t)
        print('  deaths us  ', dict(o['deaths'].most_common()))
        print('  deaths them', dict(o['odeaths'].most_common()))
        print('  big (L>=8) deaths', o['bigdeaths'])
        print('  portal crossings us %d (died %d) %s | them %d' % (o['cross'][0], o['cross'][1], o['cross'][2], o['ocross']))
        print('  head coverage', {k: round(v, 2) for k, v in o['cov'].items()}, ' vision coverage', {k: round(v, 2) for k, v in o['vcov'].items()})
        print('  eats us', o['eats'][0], ' them', o['eats'][1], ' corpse eats us/them', o['corpse'])
        print('  idle>=30r dragon-turns r50-300: %d/%d' % o['idle'])
        for c, e in o['ex'].items(): print('    ex %-22s %s' % (c, e))
        tot.update(o['deaths']); totO.update(o['odeaths'])
    print('=' * 100)
    print('TOTAL us  ', dict(tot.most_common()))
    print('TOTAL them', dict(totO.most_common()))


if __name__ == '__main__':
    main()
