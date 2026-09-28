#!/usr/bin/env python3
"""Every portal crossing (both teams) in a collect.py batch dir, with the context needed to classify
fatal ones: exit occupant now and at the crosser's previous turn, the blocker's head history and its
PORTAL_WARN-style pings from the exit, the crosser's own ray through the portal on its previous turn,
alternatives (safe non-crossing moves), pearls near the exit / near alternatives, enemy heads near.

usage (from project root):  python3 notes/tools/v18portal/extract.py replays/ab_v18 [Default] [jobs]
writes notes/tools/v18portal/<dirname>_<map>.pkl
"""
import collections
import json
import os
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

OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


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
    path, us = args
    o = R.load(path)
    m = sim2.Map(o['map'])
    res = o['result']
    side = next((s for s in 'AB' if res[s] == us), None)
    gid = int(pathlib.Path(path).stem)
    mouth = {}  # tile -> list of dirs that cross a portal
    for (ori, x, y) in m.partner:
        if ori == 'H':
            mouth.setdefault(m.wrap(x, y), []).append('N')
            mouth.setdefault(m.wrap(x, y - 1), []).append('S')
        else:
            mouth.setdefault(m.wrap(x, y), []).append('W')
            mouth.setdefault(m.wrap(x - 1, y), []).append('E')
    body = {}; team = {}; alive = set(); born = {}
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i); born[i] = 0
    pearls = set(); rnd = 0
    headhist = collections.defaultdict(list)  # id -> [(round, end head, nsteps)]
    prev_snap = {}  # id -> (round, {mouth tile: (j, seg)})
    pings = collections.defaultdict(list)  # sender -> [ping dict]
    last_turn = {}  # id -> round of its last dragonAction
    cur = None; nupd = 0; actor = None
    recs = []
    turns = collections.Counter()  # team -> dragon-turns
    mouth_end = []  # (team, id, round, tile, crossed_next) filled lazily

    def occmap():
        occ = {}
        for j in alive:
            for si, p in enumerate(body[j]):
                occ[p] = (j, si)
        return occ

    def bfs_pearls(start, occ, maxd):
        """pearls reachable within maxd steps from start (start counted at 0), true state."""
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
                        ex = (k, pos, d, nxt); break
                    pos = nxt
                if ex is not None:
                    k, ent, d, xt = ex
                    head = body[i][0]
                    oc = occ.get(xt)
                    # alternatives from the current head (first step only)
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
                        alts[d2] = dict(st=st, portal=portal2, vis=m.cheb(head, v) <= 3 if v else True, pearls3=pn, pd=pd)
                    en_heads = [m.dist(head, body[j][0]) for j in alive if team[j] != T]
                    al_heads = [m.cheb(xt, body[j][0]) for j in alive if team[j] == T and j != i]
                    pv = None
                    if ps is not None:
                        pv = dict(round=ps[0], occ=ps[1].get(xt), ent=ps[1].get(ent))
                    # own ray through this portal on the previous turn (from the entrance tile)
                    myping = None
                    for p_ in reversed(pings.get(i, [])):
                        if p_['round'] < rnd - 1:
                            break
                        if p_['round'] < rnd and p_['origin'] == ent and p_['dir'] == d:
                            myping = p_; break
                    cur = dict(gid=gid, team=T, us=(T == side), round=rnd, id=i, L=len(body[i]), move=''.join(mvs), k=k,
                               ent=ent, dir=d, exit=xt, head=head, age=rnd - born[i],
                               exit_occ=None if oc is None else (oc[0], oc[1], team[oc[0]], len(body[oc[0]])),
                               sighted=m.cheb(head, xt) <= 3, prev=pv, prev_turn_round=last_turn.get(i),
                               alts=alts, exit_pearl=xt in pearls, exit_pearls3=bfs_pearls(xt, occ, 3),
                               en_d=min(en_heads, default=99), ally_h3_exit=sum(1 for x in al_heads if x <= 3),
                               myping=myping, died=None, died_step=None, hit=None, units=sum(1 for j in alive if team[j] == T))
                    recs.append(cur)
            last_turn[i] = rnd
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
            else:
                pearls.discard(e['tile'])
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c); born[c] = rnd
            headhist[c].append((rnd, body[c][0], -1))  # -1: born here
        elif t == 'dragonDeath':
            i = e['id']
            if cur is not None and cur['id'] == i and cur['died'] is None and actor == i:
                cur['died'] = e['reason']; cur['died_step'] = nupd
                if nupd == cur['k']:
                    # state is exact here: the fatal step is the portal step
                    xt = cur['exit']
                    if e['reason'] == 'HitHeadToHead':
                        # victim already removed; it was the head on the exit
                        vic = recs_victim.get((rnd, i))
                        cur['hit'] = vic
                    elif e['reason'] == 'HitSelf':
                        cur['hit'] = ('self', body[i].index(xt) if xt in body[i] else -1, team[i], len(body[i]))
                    else:
                        for j in alive:
                            if j != i and xt in body[j]:
                                cur['hit'] = (j, body[j].index(xt), team[j], len(body[j]))
                                break
            elif actor is not None and i != actor and cur is not None and cur['id'] == actor:
                recs_victim[(rnd, actor)] = (i, 0, team[i], len(body[i]))
            alive.discard(i)
        elif t == 'sonarPing':
            s = e['sender']
            occ_path = {}
            gp = sonar_path(m, e['origin'], e['dir'])
            occ = None
            # who sits on the geometric path at ping time (first 12 tiles is plenty on Default)
            occ = occmap()
            for q in gp[:16]:
                if q in occ:
                    occ_path[q] = occ[q]
            pings[s].append(dict(round=rnd, origin=e['origin'], dir=e['dir'], end=e['end'], hitKind=e['hitKind'],
                                 hitId=e['hitId'], path=gp[:16], occ_path=occ_path, len=len(body[s]) if s in body else 0,
                                 value=e['value']))
    return dict(gid=gid, side=side, map=m.name, recs=recs, pings=dict(pings), headhist=dict(headhist),
                turns=dict(turns), last=rnd, born=born, team=team, result=res)


recs_victim = {}

if __name__ == '__main__':
    d = pathlib.Path(sys.argv[1])
    mp = sys.argv[2] if len(sys.argv) > 2 else 'Default'
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    summ = json.loads((d / 'summary.json').read_text())
    args = [(str(d / f"{g['id']}.replay"), g['us']) for g in summ if g['map'] == mp and (d / f"{g['id']}.replay").exists()]
    with Pool(jobs) as P:
        out = P.map(work, args)
    for g, o in zip([g for g in summ if g['map'] == mp and (d / f"{g['id']}.replay").exists()], out):
        o['opp'] = g['opp']; o['win'] = g['win']
    dst = HERE / f"{d.name}_{mp}.pkl"
    pickle.dump(out, open(dst, 'wb'))
    print(dst, len(out), 'games', sum(len(x['recs']) for x in out), 'crossings')
