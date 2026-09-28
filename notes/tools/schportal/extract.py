#!/usr/bin/env python3
"""Schooltime version of notes/tools/v18portal/extract.py (notes/20).

Every portal crossing (both teams) with the context needed to classify fatal ones, plus what the
crosser's own rays of the previous round saw (all of them, so the bot's PORTAL_ECHO_GUARD can be
replayed exactly: heads/bodies are summed over every ray, not only the warn ray).

Extra vs v18portal: works with summary.json (collect.py dirs, side = result side whose stats equal
'us') or ledger.json (v19plus, explicit side); full-length ray paths are summarised by 'beyond'
(geometric tiles after the exit before kelp); previous action of the crosser (steps / split);
portal id; spawn layout (A = pool, B = no pool); mouth-tile turn log for approach.py.

usage (from project root):
  python3 notes/tools/schportal/extract.py replays/ab_v22 [Schooltime] [jobs]
  python3 notes/tools/schportal/extract.py replays/v19plus [Schooltime] [jobs]
writes notes/tools/schportal/<dirname>_<map>.pkl
"""
import collections
import json
import pathlib
import pickle
import sys
from multiprocessing import Pool

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "notes/tools/midgame"))
sys.path.insert(0, str(ROOT / "notes/tools"))
import replay_decode as R  # noqa: E402
import sim2  # noqa: E402

POOL = {(x, y) for x in range(27, 33) for y in range(34, 39)} - {(27, 34), (32, 34), (27, 38), (32, 38)}


def sonar_path(m, p, d):
    """Tiles a ray from head p in direction d visits (portals pass, kelp stops), ignoring dragons."""
    out = []
    for _ in range(m.w + m.h):
        q = m.step(p, d)
        if q is None:
            break
        out.append(q)
        p = q
    return out


def work(args):
    path, us, side = args
    o = R.load(path)
    m = sim2.Map(o['map'])
    res = o['result']
    if side is None:
        side = next((s for s in 'AB' if res[s] == us), None)
    gid = int(pathlib.Path(path).stem)
    body = {}; team = {}; alive = set(); born = {}
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i); born[i] = 0
    pearls = set(); rnd = 0
    headhist = collections.defaultdict(list)  # id -> [(round, end head, nsteps)]
    prev_snap = {}
    pings = collections.defaultdict(list)
    last_act = {}  # id -> (round, nsteps, split)
    cur = None; nupd = 0; actor = None
    recs = []; turns = collections.Counter()
    pool_spawn = 0
    victim = {}

    def occmap():
        occ = {}
        for j in alive:
            for si, p in enumerate(body[j]):
                occ[p] = (j, si)
        return occ

    def bfs_pearls(start, occ, maxd):
        if start is None:
            return 0, 99
        seen = {start: 0}; q = [start]; n = 0; best = 99
        for u in q:
            du = seen[u]
            if u in pearls:
                n += 1; best = min(best, du)
            if du >= maxd:
                continue
            for d in 'NESW':
                v = m.step(u, d)
                if v is None or v in seen or v in occ:
                    continue
                seen[v] = du + 1; q.append(v)
        return n, best

    mouth = set()
    for (ori, x, y) in m.partner:
        if ori == 'H':
            mouth.add(m.wrap(x, y)); mouth.add(m.wrap(x, y - 1))
        else:
            mouth.add(m.wrap(x, y)); mouth.add(m.wrap(x - 1, y))

    for e in o['events']:
        t = e['t']
        if t == 'roundStart':
            rnd = e['round']
        elif t == 'turnStart':
            actor = e['id']; nupd = 0; cur = None
        elif t == 'dragonAction':
            i = e['id']; a = e['action'] or {}
            turns[team[i]] += 1
            occ = occmap()
            mvs = a.get('move', [])
            T = team[i]
            snap_now = {tl: occ[tl] for tl in mouth if tl in occ}
            ps = prev_snap.get(i)
            prev_snap[i] = (rnd, snap_now)
            cur = None
            if mvs:
                pos = body[i][0]; ex = None
                for k, d in enumerate(mvs):
                    edge = m.side_edge(pos, d)
                    nxt = m.step(pos, d)
                    if nxt is None:
                        break
                    if m.edges.get(edge, (0, -1))[0] == 2:
                        ex = (k, pos, d, nxt, m.edges[edge][1]); break
                    pos = nxt
                if ex is not None:
                    k, ent, d, xt, pid = ex
                    head = body[i][0]
                    oc = occ.get(xt)
                    alts = {}
                    for d2 in 'NESW':
                        v = m.step(head, d2)
                        portal2 = m.edges.get(m.side_edge(head, d2), (0, -1))[0] == 2
                        if v is None:
                            st = 'kelp'
                        elif v in occ:
                            j2, s2 = occ[v]
                            st = 'self' if j2 == i else ('ally' if team[j2] == T else 'enemy') + ('H' if s2 == 0 else '')
                        else:
                            st = 'free'
                        pn, pd = bfs_pearls(v, occ, 3) if st == 'free' else (0, 99)
                        alts[d2] = dict(st=st, portal=portal2, vis=m.cheb(head, v) <= 3 if v else True, pearls3=pn, pd=pd, tile=v)
                    en_heads = [m.dist(head, body[j][0]) for j in alive if team[j] != T]
                    al_heads = [m.cheb(xt, body[j][0]) for j in alive if team[j] == T and j != i]
                    pv = None
                    if ps is not None:
                        pv = dict(round=ps[0], occ=ps[1].get(xt), ent=ps[1].get(ent))
                    myping = None
                    for p_ in reversed(pings.get(i, [])):
                        if p_['round'] < rnd - 1:
                            break
                        if p_['round'] < rnd and p_['origin'] == ent and p_['dir'] == d:
                            myping = p_; break
                    prevpings = [p_ for p_ in pings.get(i, []) if p_['round'] == rnd - 1]
                    cur = dict(gid=gid, team=T, us=(T == side), round=rnd, id=i, L=len(body[i]), move=''.join(mvs), k=k,
                               ent=ent, dir=d, exit=xt, pid=pid, head=head, age=rnd - born[i],
                               exit_occ=None if oc is None else (oc[0], oc[1], team[oc[0]], len(body[oc[0]])),
                               sighted=m.cheb(head, xt) <= 3, prev=pv, prev_act=last_act.get(i),
                               alts=alts, exit_pearl=xt in pearls, exit_pearls3=bfs_pearls(xt, occ, 3),
                               en_d=min(en_heads, default=99), ally_h3_exit=sum(1 for x in al_heads if x <= 3),
                               myping=myping, prevpings=prevpings, died=None, died_step=None, hit=None,
                               units=sum(1 for j in alive if team[j] == T))
                    recs.append(cur)
            last_act[i] = (rnd, len(mvs), 'split' in a)
            if 'split' in a:
                headhist[i].append((rnd, body[i][0], 0))
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]
            b.insert(0, e['head'])
            while b and b[-1] != e['tail']:
                b.pop()
            nupd += 1
            if headhist[i] and headhist[i][-1][0] == rnd and headhist[i][-1][2] >= 1:
                headhist[i][-1] = (rnd, e['head'], headhist[i][-1][2] + 1)
            else:
                headhist[i].append((rnd, e['head'], 1))
        elif t == 'tileChange':
            if e['hasPearl']:
                pearls.add(e['tile'])
                if rnd < 40 and e['tile'] in POOL:
                    pool_spawn += 1
            else:
                pearls.discard(e['tile'])
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c); born[c] = rnd
            headhist[c].append((rnd, body[c][0], -1))
        elif t == 'dragonDeath':
            i = e['id']
            if cur is not None and cur['id'] == i and cur['died'] is None and actor == i:
                cur['died'] = e['reason']; cur['died_step'] = nupd
                if nupd == cur['k']:
                    xt = cur['exit']
                    if e['reason'] == 'HitHeadToHead':
                        cur['hit'] = victim.get((rnd, i))
                    elif e['reason'] == 'HitSelf':
                        cur['hit'] = ('self', body[i].index(xt) if xt in body[i] else -1, team[i], len(body[i]))
                    else:
                        for j in alive:
                            if j != i and xt in body[j]:
                                cur['hit'] = (j, body[j].index(xt), team[j], len(body[j]))
                                break
            elif actor is not None and i != actor and cur is not None and cur['id'] == actor:
                victim[(rnd, actor)] = (i, 0, team[i], len(body[i]))
            alive.discard(i)
        elif t == 'sonarPing':
            s = e['sender']
            gp = sonar_path(m, e['origin'], e['dir'])
            o_ = e['origin']
            thru = bool(gp) and gp[0] != m.wrap(o_[0] + sim2.DV[e['dir']][0], o_[1] + sim2.DV[e['dir']][1])
            occ = occmap()
            occ_path = {}
            for q in gp[:40]:
                if q in occ:
                    occ_path[q] = occ[q]
            pings[s].append(dict(round=rnd, origin=o_, dir=e['dir'], end=e['end'], hitKind=e['hitKind'],
                                 hitId=e['hitId'], path=gp[:40], plen=len(gp), thru=thru, occ_path=occ_path,
                                 len=len(body[s]) if s in body else 0, value=e['value']))
    layout = 'A' if pool_spawn >= 10 else 'B'
    return dict(gid=gid, side=side, map=m.name, recs=recs, pings=dict(pings), headhist=dict(headhist),
                turns=dict(turns), last=rnd, born=born, team=team, result=res, layout=layout, pool_spawn=pool_spawn)


if __name__ == '__main__':
    d = pathlib.Path(sys.argv[1])
    mp = sys.argv[2] if len(sys.argv) > 2 else 'Schooltime'
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    if (d / 'summary.json').exists():
        summ = json.loads((d / 'summary.json').read_text())
        games = [(g['id'], g['us'], None, g['opp'], g['win']) for g in summ if g['map'] == mp]
    else:
        led = json.loads((d / 'ledger.json').read_text())
        games = [(g['game'], None, g['side'], g['opp'], g['win']) for g in led if g['map'] == mp]
    games = [g for g in games if (d / f"{g[0]}.replay").exists()]
    with Pool(jobs) as P:
        out = P.map(work, [(str(d / f"{g[0]}.replay"), g[1], g[2]) for g in games])
    for g, o in zip(games, out):
        o['opp'] = g[3]; o['win'] = g[4]
    dst = HERE / f"{d.name}_{mp}.pkl"
    pickle.dump(out, open(dst, 'wb'))
    print(dst, len(out), 'games', sum(len(x['recs']) for x in out), 'crossings',
          'layouts', collections.Counter(x['layout'] for x in out))
