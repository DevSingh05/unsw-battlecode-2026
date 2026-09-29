#!/usr/bin/env python3
"""When do teams cross portals?  Hunger (rounds since the dragon last ate, or was born) at each crossing,
first-time crossings of an edge by that dragon ("exploratory" for its process), and fatality.

Groups: top (top-10 team in notes/replays/top10b), peer (their opponent), us (v16, replays/v16), usopp.
usage (from project root): python3 notes/unseen/tools/cross_hunger.py [jobs=4]
"""
import collections
import os
import pickle
import sys
from multiprocessing import Pool

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/top10b'))
import sim2  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location('top10b_analyze', os.path.join(ROOT, 'notes/tools/top10b/analyze.py'))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

BINS = [(0, 5), (6, 15), (16, 30), (31, 60), (61, 120), (121, 999)]


def hb(h):
    for i, (a, b) in enumerate(BINS):
        if a <= h <= b:
            return i
    return len(BINS) - 1


def work(g):
    try:
        s = sim2.simulate(g['path'])
    except Exception as ex:  # noqa: BLE001
        return None
    m = s['map']
    if not m.partner:
        return None
    mouth = collections.defaultdict(set)
    for (o, x, y) in m.partner:
        if o == 'H':
            mouth[m.wrap(x, y)].add('N'); mouth[m.wrap(x, y - 1)].add('S')
        else:
            mouth[m.wrap(x, y)].add('W'); mouth[m.wrap(x - 1, y)].add('E')
    T = g['T']
    eats = collections.defaultdict(list)
    for e in s['eats']:
        if e['team'] == T:
            eats[e['id']].append(e['round'])
    born = s['born']
    crossed_edges = collections.defaultdict(set)
    turns_h = collections.Counter()      # hunger bin -> dragon-turns
    mouth_h = collections.Counter()      # hunger bin -> turns starting on a mouth tile
    mouth_x = collections.Counter()      # ... and crossing that turn
    xs = []
    for mv in s['moves']:
        if mv['team'] != T or 'move' not in mv['act']:
            continue
        i, r = mv['id'], mv['round']
        last = born.get(i, 0)
        for er in eats[i]:
            if er < r:
                last = max(last, er)
        hunger = r - last
        b = hb(hunger)
        turns_h[b] += 1
        pos = mv['head']
        crossed = None
        for d in mv['act']['move']:
            e = m.side_edge(pos, d)
            if m.edges.get(e, (0, -1))[0] == 2:
                crossed = e
                break
            pos = m.step(pos, d)
            if pos is None:
                break
        if mv['head'] in mouth:
            mouth_h[b] += 1
            if crossed is not None:
                mouth_x[b] += 1
        if crossed is not None:
            first = crossed not in crossed_edges[i] and m.partner.get(crossed) not in crossed_edges[i]
            crossed_edges[i].add(crossed)
            xs.append(dict(h=hunger, first=first, died=mv.get('died') is not None, L=mv['len_before'], r=r,
                           ate=mv.get('ate', 0) > 0))
    return dict(grp=g['grp'], map=g['map'], turns_h=turns_h, mouth_h=mouth_h, mouth_x=mouth_x, xs=xs)


def main():
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    gs = A.games()
    with Pool(jobs) as p:
        res = [r for r in p.map(work, gs) if r]
    pickle.dump(res, open(os.path.join(H, 'cross_hunger.pkl'), 'wb'))
    for grp in ('top', 'peer', 'us', 'usopp'):
        rs = [r for r in res if r['grp'] == grp]
        if not rs:
            continue
        th = sum((r['turns_h'] for r in rs), collections.Counter())
        mh = sum((r['mouth_h'] for r in rs), collections.Counter())
        mx = sum((r['mouth_x'] for r in rs), collections.Counter())
        xs = [x for r in rs for x in r['xs']]
        n = len(rs)
        tot = sum(th.values())
        print(f"\n== {grp}: {n} team-games, {tot / n:.0f} dragon-turns/g, crossings {len(xs) / n:.1f}/g "
              f"({100.0 * len(xs) / max(1, tot):.2f}% of moves), first-time {sum(x['first'] for x in xs) / n:.1f}/g, "
              f"fatal {100.0 * sum(x['died'] for x in xs) / max(1, len(xs)):.1f}%, first-time fatal "
              f"{100.0 * sum(x['died'] for x in xs if x['first']) / max(1, sum(x['first'] for x in xs)):.1f}%, "
              f"eat on crossing move {100.0 * sum(x['ate'] for x in xs) / max(1, len(xs)):.1f}%")
        print("  hunger bin     share of turns   share of crossings   P(cross | head on mouth)")
        for b, (lo, hi) in enumerate(BINS):
            c = sum(1 for x in xs if hb(x['h']) == b)
            print(f"  {lo:>3d}-{hi:<3d}        {100.0 * th[b] / max(1, tot):6.1f}%          {100.0 * c / max(1, len(xs)):6.1f}%"
                  f"            {100.0 * mx[b] / max(1, mh[b]):5.1f}%  (n={mh[b]})")
        bym = collections.defaultdict(list)
        for r in rs:
            bym[r['map']].append(r)
        for mp, rr in sorted(bym.items()):
            xs2 = [x for r in rr for x in r['xs']]
            t2 = sum(sum(r['turns_h'].values()) for r in rr)
            print(f"    {mp:18s} games {len(rr):3d} crossings/g {len(xs2) / len(rr):6.1f} "
                  f"({100.0 * len(xs2) / max(1, t2):.2f}% of moves) fatal {100.0 * sum(x['died'] for x in xs2) / max(1, len(xs2)):4.1f}%")


if __name__ == '__main__':
    main()
