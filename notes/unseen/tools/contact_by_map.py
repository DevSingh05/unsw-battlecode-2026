#!/usr/bin/env python3
"""Runtime-observable 'enemy contact' and unit curves per map, from real replays.

For each game and team: per round window, the share of that team's dragons that
have an enemy head inside their own 7x7 view (Chebyshev <= 3), the first round any
dragon of the team saw an enemy head, and units / longest at snapshots.
Read-only. Usage (project root):
  python3 notes/unseen/tools/contact_by_map.py [notes/replays/top10b] [jobs]
"""
import collections
import glob
import json
import os
import statistics as st
import sys
from multiprocessing import Pool

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2  # noqa: E402

WIN = ((1, 50), (51, 100), (101, 200), (201, 300), (301, 400), (401, 500))
SNAP = (50, 100, 150, 200, 300, 400)


def reach3(m, src, targets):
    # walking distance <= 3 (kelp blocks, portals followed): a head that could actually reach us soon
    fr = [src]
    seen = {src}
    for _ in range(3):
        nx = []
        for p in fr:
            for d in 'NESW':
                q = m.step(p, d)
                if q is None or q in seen:
                    continue
                if q in targets:
                    return True
                seen.add(q)
                nx.append(q)
        fr = nx
    return False


def one(path):
    try:
        g = sim2.simulate(path)
    except Exception as ex:  # noqa: BLE001
        return None
    m = g['map']
    res = g['result'] or {}
    out = {'path': path, 'area': m.w * m.h, 'last': g['last_round'], 'winner': res.get('winner'),
           'end': res.get('endReason')}
    for T in 'AB':
        acc = collections.defaultdict(lambda: [0, 0])
        first = None
        units = {}
        longest = {}
        for rnd, snap in g['rounds']:
            heads = snap['heads']
            mine = [(p, L) for j, (p, L, t) in heads.items() if t == T]
            theirs = [p for j, (p, L, t) in heads.items() if t != T]
            if rnd in SNAP:
                units[rnd] = len(mine)
                longest[rnd] = max((L for _, L in mine), default=0)
            seen = 0
            tq = set(theirs)
            for p, L in mine:
                if any(m.cheb(p, q) <= 3 for q in theirs) and reach3(m, p, tq):
                    seen += 1
            if seen and first is None:
                first = rnd
            for i, (a, b) in enumerate(WIN):
                if a <= rnd <= b:
                    acc[i][0] += seen
                    acc[i][1] += len(mine)
        out[T] = {'contact': {i: (acc[i][0] / acc[i][1] if acc[i][1] else None) for i in range(len(WIN))},
                  'first': first, 'units': units, 'longest': longest}
    return out


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'notes/replays/top10b')
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    idx_path = os.path.join(folder, 'index.json')
    names = {}
    if os.path.exists(idx_path):
        for mm in json.load(open(idx_path)):
            names[str(mm['id'])] = mm.get('mapName')
    paths = sorted(glob.glob(os.path.join(folder, '*.replay')))
    with Pool(jobs) as p:
        rows = [r for r in p.map(one, paths) if r]
    by = collections.defaultdict(list)
    for r in rows:
        gid = os.path.basename(r['path']).split('.')[0]
        by[names.get(gid, '?')].append(r)
    print('map                games  winnerContact% by window ' + ' '.join(f'{a}-{b}' for a, b in WIN) +
          ' | firstSeen(med) | winner units@' + '/'.join(map(str, SNAP)) + ' | elim%')
    for mp in sorted(by, key=lambda k: st.median([x['area'] for x in by[k]])):
        gs = by[mp]
        wins = [x[x['winner']] for x in gs if x['winner'] in ('A', 'B')]
        allT = [x[T] for x in gs for T in 'AB']
        cont = []
        for i in range(len(WIN)):
            v = [w['contact'][i] for w in allT if w['contact'][i] is not None]
            cont.append(f'{100 * st.median(v):5.1f}' if v else '    -')
        fs = [w['first'] for w in allT if w['first'] is not None]
        us = []
        for s in SNAP:
            v = [w['units'].get(s) for w in wins if w['units'].get(s) is not None]
            us.append(f'{st.median(v):.0f}' if v else '-')
        elim = sum(1 for x in gs if x['last'] < 499) / len(gs)
        print(f'{mp:18s} {len(gs):5d}  ' + ' '.join(cont) + f' | {st.median(fs) if fs else -1:6.0f} | ' + '/'.join(us) +
              f' | {100 * elim:.0f}%  area={gs[0]["area"]}')


if __name__ == '__main__':
    main()
