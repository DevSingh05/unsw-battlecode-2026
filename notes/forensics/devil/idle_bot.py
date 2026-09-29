#!/usr/bin/env python3
"""Idle decisions (our small dragon outside the hub, no eat for >= 8 rounds, r10..R1) re-run through v29 and a
patched binary. For each: does the chosen step reduce the static walking distance to the nearest every-round
(hot) tile? Also the max 'pearls' term the bot saw (how flat the pearl gradient is).
    python3 notes/forensics/devil/idle_bot.py BIN_BASE BIN_NEW [R1=60] [games...]
"""
import sys, os, re, collections
from common import games, sim, GDIR, ROOT, REFMAP as m
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/rams'))
import botview as BV

A, B = sys.argv[1], sys.argv[2]
R1 = int(sys.argv[3]) if len(sys.argv) > 3 else 60
G = {g['game']: g for g in games()}
gids = [int(x) for x in sys.argv[4:]] or [g for g in G if not G[g]['win']]
# static distance to nearest hot tile
hot = [t for t, gg in m.tiles.items() if gg[1] == 1]
dist = {t: 0 for t in hot}; q = list(hot)
for u in q:
    for d in 'NESW':
        v = m.step(u, d)
        if v is not None and v not in dist: dist[v] = dist[u] + 1; q.append(v)
DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
inhub = lambda t: 12 <= t[0] <= 19
CRE = re.compile(r'cand (\w) t=\((\d+),(\d+)\) pearls=([-\d.]+)')


def dec(binary, did, turns):
    outs, dbg = BV.run_bot(binary, did, turns)
    d = {}
    for blk in re.split(r'\n(?=R\d+ id=)', dbg):
        mm = re.match(r'R(\d+) id=\d+ len=(\d+) dir=\w head=\((\d+),(\d+)\)', blk)
        if not mm: continue
        ar = re.findall(r'-> (\w)\n', blk + '\n')
        pe = [float(x.group(4)) for x in CRE.finditer(blk)]
        d[int(mm.group(1))] = (ar[-1] if ar else None, (int(mm.group(3)), int(mm.group(4))), int(mm.group(2)), max(pe) if pe else 0)
    return d


tot = collections.Counter(); pmax = []
for gid in gids:
    S = sim(gid); us = G[gid]['side']
    last = collections.defaultdict(int)
    for e in S['eats']: pass
    eats = collections.defaultdict(list)
    for e in S['eats']: eats[e['id']].append(e['round'])
    death = {d['id']: d['round'] for d in S['deaths']}
    for did in [j for j in S['team'] if S['team'][j] == us and S['born'].get(j, 0) < R1]:
        b = S['born'].get(did, 0); e = min(death.get(did, R1), R1)
        if e - b < 10: continue
        m_, turns = BV.capture(os.path.join(GDIR, '%d.replay' % gid), did, b, e)
        if not turns: continue
        da = dec(A, did, turns); db = dec(B, did, turns)
        for r, (mv, head, L, pm) in da.items():
            if r < 10 or inhub(head) or L > 4 or mv is None: continue
            le = max([x for x in eats[did] if x <= r] + [b])
            if r - le < 8: continue
            tot['idle'] += 1; pmax.append(pm)
            h0 = dist.get(head, 99)
            for tag, mv2 in (('base', mv), ('new', db.get(r, (None,))[0])):
                if mv2 is None: continue
                t = m.step(head, mv2)
                if t is not None and dist.get(t, 99) < h0: tot[tag + '_closer'] += 1
            if db.get(r, (None,))[0] != mv: tot['changed'] += 1
    print(gid, dict(tot), flush=True)
pmax.sort()
if pmax:
    print('idle decisions %d: base moves closer to hot %.0f%%, new %.0f%%, changed %.0f%%; max pearls term median %.2f, 90th pct %.2f' % (
        tot['idle'], 100 * tot['base_closer'] / tot['idle'], 100 * tot['new_closer'] / tot['idle'], 100 * tot['changed'] / tot['idle'],
        pmax[len(pmax) // 2], pmax[int(len(pmax) * .9)]))
