#!/usr/bin/env python3
"""Every ram of one of OUR dragons with length >= MINL (killed head-to-head on another dragon's turn),
reconstructed at our last decision before the ram.

    python3 notes/tools/rams/rams.py [MINL=8]        -> writes notes/tools/rams/rams.pkl, prints one line per ram

Per ram: killer len/id/order, killer head distance to our head (BFS over free tiles incl. portals) and
Chebyshev (view), whether the killer existed / was visible / how many of its segments we saw, the killer's
actual move (steps, portal crossed), our chosen move, and for every legal alternative (4 moves + split):
  - true safety: no enemy head can reach the landing tile with its real sprint reach (len-1 steps, BFS
    over tiles free after our move; the enemy's own tail vacates as it sprints)
  - bot-model safety: reproduction of computeThreats() (visible heads only, reach=min(visLen-1, cap))
  - room: time-aware flood area from the landing tile (>= our length = 'survivable')
"""
import collections, glob, json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
import replay_decode as R

MINL = int(sys.argv[1]) if len(sys.argv) > 1 else 8
KING_MIN_LEN, KING_THREAT_REACH, MAX_THREAT_REACH = 8, 4, 1
DIRS = 'NESW'


def load_games():
    games = {}
    for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
        games[g['game']] = (os.path.join(ROOT, 'replays/v16/%d.replay' % g['game']), g['side'], g['map'], g['win'], 'v16')
    for d in glob.glob(os.path.join(ROOT, 'replays/ab_*/summary.json')):
        src = os.path.basename(os.path.dirname(d))
        for g in json.load(open(d)):
            p = os.path.join(os.path.dirname(d), '%d.replay' % g['id'])
            if not os.path.exists(p): continue
            res = R.load(p)['result']
            side = 'A' if res['A'] == g['us'] else ('B' if res['B'] == g['us'] else None)
            if side is None: continue
            games[g['id']] = (p, side, g['map'], g['win'], src)
    return games


def reach_dist(m, occ_block, own_body, start, target, maxd):
    """Min steps for a head at `start` to move INTO `target` (an occupied head tile), sprinting up to maxd
    steps. occ_block: tiles blocked for the whole sprint. own_body: the mover's body (index 0 = head);
    segment i vacates after len-i steps... a sprint of k steps removes 2k-1 tail segments by the end, but
    per step: step s (1-based) is checked against the body left by step s-1, whose tail has moved s-1
    times and lost s-2 extra segments -> segments with index >= L-(2s-2) are gone (approx)."""
    L = len(own_body)
    idx = {t: i for i, t in enumerate(own_body)}
    from collections import deque
    dist = {start: 0}; q = deque([start])
    while q:
        u = q.popleft(); du = dist[u]
        if du >= maxd: continue
        for d in DIRS:
            v = m.step(u, d)
            if v is None: continue
            s = du + 1
            if v == target: return s
            if v in dist: continue
            if v in occ_block: continue
            if v in idx:
                gone = max(0, (s - 1) + max(0, s - 2))  # tail moves s-1 times, s-2 extra removals
                if idx[v] < L - gone: continue
            dist[v] = s; q.append(v)
    return None


def flood_area(m, occ_free, start, cap):
    """time-aware flood: occ_free[tile] = step at which the tile becomes free."""
    from collections import deque
    dist = {start: 0}; q = deque([start]); n = 0
    while q and n < cap:
        u = q.popleft(); n += 1
        for d in DIRS:
            v = m.step(u, d)
            if v is None or v in dist: continue
            if occ_free.get(v, 0) > dist[u] + 1: continue
            dist[v] = dist[u] + 1; q.append(v)
    return n


def cheb(m, a, b): return m.cheb(a, b)


def analyse(G, p, side, gid, mp, win, src, d):
    us = d['id']; Rd = d['round']; killer = d.get('killer')
    rec = {'game': gid, 'map': mp, 'win': win, 'src': src, 'round': Rd, 'id': us, 'len': d['len'], 'killer': killer,
           'killer_len': d.get('killer_len'), 'killer_team': d.get('killer_team')}
    # killer's fatal move
    km = [mv for mv in G['moves'] if mv['id'] == killer and mv['round'] == Rd]
    km = km[-1] if km else None
    rec['killer_move'] = ''.join(km['act'].get('move', [])) if km else None
    rec['killer_from'] = km['head'] if km else None
    m = G['map']
    if km:
        pos = km['head']; crossed = False
        for s in rec['killer_move']:
            if m.edges.get(m.side_edge(pos, s), (0, -1))[0] == 2: crossed = True
            pos = m.step(pos, s)
            if pos is None: break
        rec['killer_portal'] = crossed
    rec['killer_born'] = G['born'].get(killer); rec['killer_parent'] = G['parent_of'].get(killer)
    # our last action before the ram
    acts = [(mv['round'], 'move') for mv in G['moves'] if mv['id'] == us and mv['round'] <= Rd]
    acts += [(s['round'], 'split') for s in G['splits'] if s['parent'] == us and s['round'] <= Rd]
    if not acts: return None
    R0, kind = max(acts)
    rec['R0'] = R0; rec['our_act_kind'] = kind; rec['killer_before_us'] = killer < us
    rec['same_round'] = (R0 == Rd)
    S = simulate(p, stop=(R0, us))
    body = S['body']; team = S['team']; pearls = S['pearls']
    me = body[us]; head = me[0]; L = len(me)
    rec['len_at_R0'] = L; rec['act'] = S['act']
    rec['killer_exists'] = killer in body
    # occupancy
    occ = {}
    for j, b in body.items():
        for i, t in enumerate(b): occ[t] = (j, i)
    enemies = [j for j in body if team[j] != side]
    units = sum(1 for j in body if team[j] == side)
    rec['units'] = units; rec['enemy_units'] = len(enemies)
    # visibility (7x7 around our head, plain wrap)
    vis = lambda t: cheb(m, head, t) <= 3
    vislen = {j: sum(1 for t in body[j] if vis(t)) for j in enemies}
    if killer in body:
        kh = body[killer][0]
        rec['k_cheb'] = cheb(m, head, kh); rec['k_manh'] = m.dist(head, kh)
        rec['k_vis_head'] = vis(kh); rec['k_vislen'] = vislen.get(killer, 0); rec['k_len_R0'] = len(body[killer])
    # neck direction
    neck = me[1] if L > 1 else None
    opts = []
    for dch in DIRS:
        t = m.step(head, dch)
        o = {'d': dch, 't': t}
        if t is None: o['legal'] = 'kelp'; opts.append(o); continue
        if t in occ:
            j, i = occ[t]
            o['legal'] = 'self' if j == us else ('head' if i == 0 else 'body')
            opts.append(o); continue
        o['legal'] = 'ok'
        eat = t in pearls
        newme = [t] + (me if eat else me[:-1])
        opts.append(o); o['newme'] = newme
    # split options: parent head stays (split 2 .. L-2); reverse split L-2 moves bulk to tail
    if L >= 4 and units < 64:
        opts.append({'d': 'SPLIT2', 't': head, 'legal': 'ok', 'newme': me[:-2], 'split': 2})
        opts.append({'d': 'RSPLIT', 't': me[-1], 'legal': 'ok', 'newme': list(reversed(me[2:])), 'split': L - 2})
    # sprints of 2-3 steps (cost 1-2 segments); others static, own body simulated per engine rules
    others = set()
    for j, b in body.items():
        if j != us: others.update(b)
    def sprint(seq):
        b = list(me)
        for k, dch in enumerate(seq):
            if k > 0 and len(b) < 3: return None
            v = m.step(b[0], dch)
            if v is None or v in b or v in others: return None
            eat = v in pearls and k == 0
            b = [v] + (b if eat else b[:-1])
            if k > 0: b = b[:-1]
        return b
    for n in (2, 3):
        if L - (n - 1) < 2: continue
        import itertools
        best = {}
        for seq in itertools.product(DIRS, repeat=n):
            nb = sprint(seq)
            if nb is None: continue
            best.setdefault(nb[0], (''.join(seq), nb))
        for t, (seq, nb) in best.items():
            opts.append({'d': 'SPR' + seq, 't': t, 'legal': 'ok', 'newme': nb, 'sprint': n})
    # chosen
    a = S['act']
    if 'move' in a:
        chosen = a['move'][0] if len(a['move']) == 1 else 'SPR' + ''.join(a['move'])
    elif 'split' in a:
        k = a['split']; chosen = 'RSPLIT' if k == L - 2 and k > 2 else ('SPLIT2' if k == 2 else 'SPLIT%d' % k)
    else:
        chosen = 'suicide'
    rec['chosen'] = chosen
    rec['our_portal'] = ('move' in a) and m.edges.get(m.side_edge(head, a['move'][0]), (0, -1))[0] == 2
    # evaluate options
    for o in opts:
        if o['legal'] != 'ok': continue
        t = o['t']; newme = o['newme']
        # board after our action
        blocked = set()
        for j, b in body.items():
            if j == us: continue
            blocked.update(b)
        mine = set(newme)
        if o['d'] == 'SPLIT2': mine = set(me)  # child sits on the rest
        if o['d'] == 'RSPLIT': mine = set(me)
        threats = []
        bot_threat = []
        for j in enemies:
            eb = body[j]; Lj = len(eb)
            blk = (blocked - set(eb)) | (mine - {t})
            dj = reach_dist(m, blk, eb, eb[0], t, max(1, Lj - 1))
            if dj is not None: threats.append((j, Lj, dj))
            # bot model: visible heads, reach capped, BFS on pre-move board (freeT>1 stops expansion)
            if vis(eb[0]):
                cap = KING_THREAT_REACH if L >= KING_MIN_LEN else MAX_THREAT_REACH
                rch = min(max(1, vislen[j] - 1), cap)
                bd = bot_bfs(m, occ, body, eb[0], t, cap, vis, us)
                if bd is not None:
                    o.setdefault('bot_raw', []).append((j, vislen[j], vislen[j] >= Lj, bd))
                    if bd <= rch: bot_threat.append((j, vislen[j], bd))
        o['threats'] = threats; o['bot_threat'] = bot_threat
        # room
        free = {}
        for j, b in body.items():
            bb = newme if j == us else b
            for i, s in enumerate(bb): free[s] = len(bb) - i
        if o['d'] in ('SPLIT2',):
            for i, s in enumerate(me): free[s] = len(me) - i
        o['area'] = flood_area(m, free, t, 3 * L + 30)
        o['safe'] = not threats
        o['room'] = o['area'] >= L + 3
        o['keepdist'] = min((m.dist(body[j][0], t) for j in enemies if vis(body[j][0])), default=99)
    rec['head'] = head; rec['tail'] = me[-1]; rec['tail_cheb'] = cheb(m, head, me[-1])
    rec['opts'] = [{k: v for k, v in o.items() if k != 'newme'} for o in opts]
    return rec


def bot_bfs(m, occ, body, start, target, reach, vis, us):
    """computeThreats(): BFS from an enemy head up to `reach`; tiles whose freeT>1 (occupied, not a tail
    about to vacate) are marked but not expanded. Occupancy known only inside our view + our own body."""
    from collections import deque
    dist = {start: 0}; q = deque([start])
    while q:
        u = q.popleft()
        if dist[u] >= reach: continue
        for d in DIRS:
            v = m.step(u, d)
            if v is None or v in dist: continue
            dist[v] = dist[u] + 1
            if v == target: return dist[v]
            blocked = False
            if v in occ:
                j, i = occ[v]
                known = (j == us) or vis(v)
                if known and i < len(body[j]) - 1: blocked = True
            if not blocked: q.append(v)
    return None


def main():
    games = load_games()
    out = []; ngames = collections.Counter(); nrams_other = 0
    for gid, (p, side, mp, win, src) in sorted(games.items()):
        if not os.path.exists(p): continue
        G = simulate(p); ngames[mp] += 1
        for d in G['deaths']:
            if d['team'] != side or d['len'] < MINL: continue
            if d['actor'] == d['id'] or d['reason'] != 'HitHeadToHead': continue
            if d.get('killer_team') == side: nrams_other += 1
            r = analyse(G, p, side, gid, mp, win, src, d)
            if r: out.append(r); print(fmt(r), flush=True)
    pickle.dump({'rams': out, 'ngames': dict(ngames), 'ally_rams': nrams_other}, open(os.path.join(os.path.dirname(__file__), 'rams.pkl'), 'wb'))
    print('games', sum(ngames.values()), dict(ngames), 'rams', len(out), 'ally rams', nrams_other)


def fmt(r):
    ch = [o for o in r['opts'] if o['d'] == r['chosen']]
    s = '%s %d %-10s r%d L%d id%d k=id%s L%s mv=%s P=%s | R0=%d %s kexist=%s cheb=%s manh=%s vis=%s vislen=%s | chose %s' % (
        r['src'], r['game'], r['map'][:10], r['round'], r['len'], r['id'], r['killer'], r['killer_len'], r['killer_move'],
        int(bool(r.get('killer_portal'))), r['R0'], r['our_act_kind'], int(r['killer_exists']), r.get('k_cheb'), r.get('k_manh'),
        int(bool(r.get('k_vis_head'))), r.get('k_vislen'), r['chosen'])
    spr = [o for o in r['opts'] if o['d'].startswith('SPR') and o.get('safe') and o.get('room')]
    s += ' safeSPR:%d' % len(spr)
    for o in r['opts']:
        if o['d'].startswith('SPR'): continue
        if o['legal'] != 'ok': s += ' %s:%s' % (o['d'], o['legal'][:2]); continue
        s += ' %s:%s%s%s' % (o['d'], 'S' if o['safe'] else 'x', 'r' if o['room'] else '-', 'b' if o['bot_threat'] else '.')
    return s


if __name__ == '__main__':
    main()
