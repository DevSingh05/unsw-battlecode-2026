"""Portal-crossing context for every crossing move, plus portal-mouth occupancy.
For each move whose path crosses a portal edge, records (at the moment of the move, exact state since lower IDs already moved):
  exit tile occupant (none/self/ally/allyH/enemy/enemyH), own/enemy segments within Chebyshev 1 of the exit, own/enemy heads within 3,
  crossed same dragon within last 4 rounds (ping-pong), length, steps, whether the move eats on the far side, died + reason.
Mouth occupancy: every 5 rounds, share of the team's segments that sit on a portal-mouth tile (tile with a portal edge).
Usage: python3 crossing.py [jobs] [maps comma] -> crossing.pkl"""
import os, sys, pickle, collections
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
sys.path.append(os.path.join(H, '../midgame')); sys.path.append(os.path.join(H, '..'))
import analyze as A, sim2, replay_decode as R


def work(args):
    path, tags = args
    o = R.load(path); m = sim2.Map(o['map'])
    if not m.partner: return [], {}
    mouth = set()
    for (orient, x, y) in m.partner:
        if orient == 'H': mouth.add(m.wrap(x, y)); mouth.add(m.wrap(x, y - 1))
        else: mouth.add(m.wrap(x, y)); mouth.add(m.wrap(x - 1, y))
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    pearls = set(); rnd = 0; recs = []; cur = None; lastx = {}; xinfo = {}
    occ_stats = collections.defaultdict(lambda: [0, 0])  # T -> [mouth segs, all segs]
    def finish():
        nonlocal cur
        if cur is not None: recs.append(cur); cur = None
    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            finish(); rnd = e['round']
            if rnd % 5 == 0:
                for j in alive:
                    s = occ_stats[team[j]]; s[1] += len(body[j]); s[0] += sum(1 for p in body[j] if p in mouth)
        elif t == 'turnStart': finish()
        elif t == 'dragonAction':
            finish()
            a = e['action'] or {}; i = e['id']
            mvs = a.get('move', [])
            if not mvs or team[i] not in tags: continue
            pos = body[i][0]; ex = None
            for k, d in enumerate(mvs):
                edge = m.side_edge(pos, d)
                nxt = m.step(pos, d)
                if nxt is None: break
                if m.edges.get(edge, (0, -1))[0] == 2: ex = (k, nxt); break
                pos = nxt
            if ex is None: continue
            T = team[i]; tile = ex[1]
            occ = {}
            for j in alive:
                for si, p in enumerate(body[j]): occ[p] = (j, si == 0)
            if tile in occ:
                j, hd = occ[tile]
                oc = 'self' if j == i else (('ally' if team[j] == T else 'enemy') + ('H' if hd else ''))
            else: oc = 'none'
            rel = None; occ_info = None
            if tile in occ and occ[tile][0] != i:
                j = occ[tile][0]; lc = xinfo.get(j)
                if lc and rnd - lc[0] <= 8:
                    rel = 'convoy' if lc[2] == tile else ('counterflow' if lc[1] == tile else 'crossed_other')
                else: rel = 'resident'
                occ_info = (body[j].index(tile), j, len(body[j]), m.cheb(body[j][0], tile), body[j][0] in mouth, sum(1 for q in body[j] if q in mouth))
            else: occ_info = None
            xinfo[i] = (rnd, body[i][0] if ex[0] == 0 else pos, tile)
            own1 = en1 = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = m.wrap(tile[0] + dx, tile[1] + dy)
                    if p in occ and occ[p][0] != i:
                        if team[occ[p][0]] == T: own1 += 1
                        else: en1 += 1
            ownh3 = sum(1 for j in alive if j != i and team[j] == T and m.cheb(body[j][0], tile) <= 3)
            enh3 = sum(1 for j in alive if team[j] != T and m.cheb(body[j][0], tile) <= 3)
            pp = i in lastx and rnd - lastx[i] <= 4
            lastx[i] = rnd
            cur = dict(tags[T], round=rnd, id=i, L=len(body[i]), steps=len(mvs), exit_occ=oc, own1=own1, en1=en1,
                       ownh3=ownh3, enh3=enh3, rel=rel, occ_info=occ_info, sighted=m.cheb(body[i][0], tile) <= 3, dist_exit=m.cheb(body[i][0], tile), pingpong=pp, exit_pearl=tile in pearls, died=None, dstep=None, units=sum(1 for j in alive if team[j] == T))
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'tileChange':
            if e['hasPearl']: pearls.add(e['tile'])
            else: pearls.discard(e['tile'])
        elif t == 'dragonSplit':
            body[e['parent']] = list(e['parentBody']); body[e['child']] = list(e['childBody']); team[e['child']] = e['team']; alive.add(e['child'])
        elif t == 'dragonDeath':
            i = e['id']
            if cur is not None and cur['id'] == i and cur['died'] is None: cur['died'] = e['reason']
            alive.discard(i)
    finish()
    occ_out = {T: tuple(v) for T, v in occ_stats.items()}
    occ_out['mouth_frac'] = len(mouth) / (m.w * m.h)
    return recs, {T: (tags[T], occ_out.get(T), occ_out['mouth_frac']) for T in tags}


if __name__ == '__main__':
    G = A.games(); by = collections.defaultdict(dict)
    maps = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    for x in G:
        if maps and x['map'] not in maps: continue
        by[x['path']][x['T']] = {k: x[k] for k in ('gid', 'map', 'grp', 'name')}
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(jobs) as P:
        res = P.map(work, sorted(by.items()), chunksize=2)
    recs = []; occ = []
    for r, oc in res:
        recs += r; occ += list(oc.values())
    pickle.dump({'x': recs, 'occ': occ}, open(os.path.join(H, 'crossing.pkl'), 'wb'))
    print(len(recs), len(occ))
