"""Replay state reconstruction for UNSW Battlecode 2026 replays.

Replays each event against the map to track full dragon bodies, pearls, and who
ate/killed what. Produces flat record lists that analysis scripts consume.

    from replay_sim import simulate
    g = simulate('notes/replays/339122.replay')
    g['splits'], g['moves'], g['deaths'], g['eats'], g['sonars'], g['rounds']
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools/midgame'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools'))
import replay_decode as R

DV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


class Map:
    def __init__(self, text):
        self.tiles = {}; self.edges = {}; self.dragons = []; self.sym = None; self.name = ''
        for line in text.splitlines():
            f = line.split()
            if not f: continue
            if f[0] == 'MAP': self.w, self.h = int(f[1]), int(f[2])
            elif f[0] == 'SYMMETRY': self.sym = f[1]
            elif f[0] == 'MAP_NAME': self.name = ' '.join(f[1:])
            elif f[0] == 'TILE': self.tiles[(int(f[1]), int(f[2]))] = (int(f[3]), int(f[4]))
            elif f[0] == 'EDGE':
                idx, kind, pid = int(f[1]), int(f[2]), int(f[3])
                e = self.edge_of_index(idx)
                if e is None: continue
                self.edges[e] = (kind, pid)
            elif f[0] == 'DRAGON':
                team, n = int(f[1]), int(f[2]); pts = [(int(f[3 + 2 * i]), int(f[4 + 2 * i])) for i in range(n)]
                self.dragons.append((team, pts))
        # portal partners
        byid = {}
        for e, (k, p) in self.edges.items():
            if k == 2: byid.setdefault(p, []).append(e)
        self.partner = {}
        for p, es in byid.items():
            if len(es) == 2: self.partner[es[0]] = es[1]; self.partner[es[1]] = es[0]

    def edge_of_index(self, idx):
        st = self.w + 1; col = idx % st; row = idx // st
        if row % 2 == 0:
            if col == self.w or row == 2 * self.h: return None
            return ('H', col, row // 2)
        if col == self.w: return None
        return ('V', col, (row - 1) // 2)

    def wrap(self, x, y): return (x % self.w, y % self.h)

    def side_edge(self, p, d):
        x, y = p
        if d == 'N': return ('H', x, y)
        if d == 'S': return ('H', x, (y + 1) % self.h)
        if d == 'W': return ('V', x, y)
        return ('V', (x + 1) % self.w, y)

    def step(self, p, d):
        e = self.side_edge(p, d)
        k, pid = self.edges.get(e, (0, -1))
        if k == 1: return None
        if k == 2 and e in self.partner:
            o, ex, ey = self.partner[e]
            if o == 'H': return self.wrap(ex, ey if d == 'S' else ey - 1)
            return self.wrap(ex if d == 'E' else ex - 1, ey)
        return self.wrap(p[0] + DV[d][0], p[1] + DV[d][1])

    def dist(self, a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return min(dx, self.w - dx) + min(dy, self.h - dy)

    def cheb(self, a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return max(min(dx, self.w - dx), min(dy, self.h - dy))


def simulate(path, stop=None):
    o = R.load(path)
    m = Map(o['map'])
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons):
        body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    pearls = set(); corpse = {}  # tile -> (dead id, team, round)
    rnd = 0; actor = None; action = None; nupd = 0; pre = None
    splits = []; moves = []; deaths = []; eats = []; sonars = []; rounds = []
    born = {i: 0 for i in body}; parent_of = {}
    pending_deaths = []; appears = []

    def snapshot():
        rows = {}
        for T in 'AB':
            ds = [i for i in alive if team[i] == T]
            ls = sorted((len(body[i]), -i) for i in ds)
            rows[T] = {'ids': {j: len(body[j]) for j in ds}, 'n': len(ds), 'max': ls[-1][0] if ls else 0, 'total': sum(len(body[i]) for i in ds),
                       'king': -ls[-1][1] if ls else None, 'lens': sorted((len(body[i]) for i in ds), reverse=True)}
        rows['heads'] = {j: (body[j][0], len(body[j]), team[j]) for j in alive}
        rows['bodies'] = {j: list(body[j]) for j in alive}
        rows['pearls'] = set(pearls)
        return rows

    def close_action():
        nonlocal action
        if action is None: return
        a = action
        if 'move' in a['act']:
            a['len_after'] = len(body[a['id']]) if a['id'] in alive else 0
            a['head_after'] = body[a['id']][0] if a['id'] in alive else None
            nd = a['near_enemy_head']
            a['enemy_after'] = (m.dist(a['head_after'], body[nd[1]][0]) if (nd and a['head_after'] and nd[1] in alive) else None)
            moves.append(a)
        action = None

    evs = o['events']
    for e in evs:
        t = e['t']
        if t == 'roundStart':
            close_action()
            if rnd > 0: rounds.append((rnd, snapshot()))
            rnd = e['round']
        elif t == 'turnStart':
            close_action(); actor = e['id']; nupd = 0
        elif t == 'dragonAction':
            a = e['action'] or {'suicide': 1}
            i = e['id']
            if stop and (rnd, i) == stop:
                return {'map': m, 'body': {j: list(body[j]) for j in alive}, 'team': dict(team), 'pearls': set(pearls), 'act': a, 'e': e}
            # context before acting
            my = body[i][0]
            enemies = [j for j in alive if team[j] != team[i]]
            near = None
            for j in enemies:
                d = m.dist(my, body[j][0])
                if near is None or d < near[0]: near = (d, j, len(body[j]))
            action = {'round': rnd, 'id': i, 'team': team[i], 'act': a, 'len_before': len(body[i]),
                      'head': my, 'steps': len(a['move']) if 'move' in a else 0, 'near_enemy_head': near,
                      'ate': 0, 'killed': [], 'died': None}
            if 'suicide' in a:
                action['len_after'] = 0; moves.append(dict(action, suicide=True)); action = None
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]
            b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
            nupd += 1
        elif t == 'tileChange':
            tile = e['tile']
            if e['hasPearl']:
                pearls.add(tile)
                c_ = corpse.get(tile)
                appears.append((rnd, tile, bool(c_ and c_[2] == rnd)))
            else:
                pearls.discard(tile)
                src = corpse.pop(tile, None)
                who = actor
                en_ = [m.dist(tile, body[j][0]) for j in alive if team[j] != team.get(who)]
                al_ = [m.dist(tile, body[j][0]) for j in alive if team[j] == team.get(who) and j != who]
                eats.append({'round': rnd, 'id': who, 'team': team.get(who), 'tile': tile, 'corpse': src, 'en': min(en_, default=99), 'al': min(al_, default=99),
                             'gap': m.tiles.get(tile), 'len': len(body[who]) if who in body else None})
                if action is not None and action['id'] == who: action['ate'] += 1
        elif t == 'dragonSplit':
            p = e['parent']; c = e['child']
            L = len(body[p])
            occ = set()
            for j in alive: occ.update(body[j])
            exits = 0
            for dd_ in 'NESW':
                nt = m.step(body[p][0], dd_)
                if nt is not None and nt not in occ: exits += 1
            en_near = min((m.dist(body[p][0], body[j][0]) for j in alive if team[j] != team[p]), default=99)
            body[p] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
            born[c] = rnd; parent_of[c] = p
            splits.append({'round': rnd, 'parent': p, 'child': c, 'team': e['team'], 'L': L, 'k': len(e['childBody']),
                           'parent_age': rnd - born[p], 'exits': exits, 'enemy_dist': en_near, 'units_before': sum(1 for j in alive if team[j] == e['team']) - 1})
            action = None
        elif t == 'dragonDeath':
            i = e['id']; L = len(body[i]); reason = e['reason']
            rec = {'round': rnd, 'id': i, 'team': team[i], 'len': L, 'reason': reason, 'actor': actor,
                   'head': body[i][0], 'age': rnd - born[i], 'hit': None}
            if reason == 'HitHeadToHead':
                if i != actor:
                    rec['killer'] = actor; rec['killer_len'] = len(body[actor]); rec['killer_team'] = team[actor]
                else:
                    # mover: find the victim recorded just before
                    v = deaths[-1] if deaths and deaths[-1]['round'] == rnd and deaths[-1].get('killer') == i else None
                    if v: rec['victim'] = v['id']; rec['victim_len'] = v['len']; rec['victim_team'] = v['team']
            elif reason == 'HitOtherBody' and action is not None and action['id'] == i:
                steps = action['act'].get('move', [])
                if nupd < len(steps):
                    dest = m.step(body[i][0], steps[nupd])
                    for j in alive:
                        if j != i and dest in body[j]:
                            rec['hit'] = {'id': j, 'team': team[j], 'len': len(body[j]), 'seg': body[j].index(dest)}
                            break
            if action is not None and action['id'] == i:
                rec['steps'] = action['steps']; rec['step_failed'] = nupd + 1
                rec['move'] = ''.join(action['act'].get('move', []))
            # context: allies / king / enemies around the death
            allies = [j for j in alive if j != i and team[j] == team[i]]
            if allies:
                kj = max(allies, key=lambda j: (len(body[j]), -j))
                rec['king'] = (kj, len(body[kj]), m.dist(body[i][0], body[kj][0]), m.cheb(body[i][0], body[kj][0]))
                rec['king_head2'] = list(body[kj][:2])
                nj = min(allies, key=lambda j: m.dist(body[i][0], body[j][0]))
                rec['ally_near'] = (nj, len(body[nj]), m.dist(body[i][0], body[nj][0]))
            en = [j for j in alive if team[j] != team[i]]
            if en:
                nj = min(en, key=lambda j: m.dist(body[i][0], body[j][0]))
                rec['enemy_near'] = (nj, len(body[nj]), m.dist(body[i][0], body[nj][0]))
            rec['body'] = list(body[i])
            # neighbour status of the dying head at the moment of death (added for loss_diag):
            # per direction: 'kelp', 'free', 'pearl', ('self'|'ally'|'enemy', is_head)
            occ_ = {}
            for j in alive:
                for si, s in enumerate(body[j]): occ_[s] = (j, si == 0)
            nb = {}
            for dd_ in 'NESW':
                nt = m.step(body[i][0], dd_)
                if nt is None: nb[dd_] = 'kelp'
                elif nt in occ_:
                    j, hd = occ_[nt]
                    nb[dd_] = ('self' if j == i else ('ally' if team[j] == team[i] else 'enemy'), hd)
                else: nb[dd_] = 'pearl' if nt in pearls else 'free'
            rec['nbrs'] = nb
            # pearls land on even segments
            for s in body[i][::2]: corpse[s] = (i, team[i], rnd, L)
            deaths.append(rec)
            if action is not None and action['id'] == actor and i != actor:
                action['killed'].append((i, team[i], L))
            if action is not None and action['id'] == i: action['died'] = reason
            alive.discard(i)
        elif t == 'sonarPing':
            s = e['sender']
            sonars.append({'round': rnd, 'id': s, 'team': team.get(s), 'dir': e['dir'], 'value': e['value'],
                           'origin': e['origin'], 'end': e['end'], 'hitKind': e['hitKind'], 'hitId': e['hitId'],
                           'head': body[s][0] if s in body else None,
                           'facing': None, 'len': len(body[s]) if s in body else None})
    close_action()
    rounds.append((rnd, snapshot()))
    return {'map': m, 'result': o['result'], 'splits': splits, 'moves': moves, 'deaths': deaths, 'eats': eats,
            'sonars': sonars, 'rounds': rounds, 'last_round': rnd, 'body': body, 'alive': alive, 'team': team,
            'parent_of': parent_of, 'born': born, 'appears': appears}


if __name__ == '__main__':
    g = simulate(sys.argv[1])
    print(g['map'].name, g['result'], 'last round', g['last_round'])
    print('final snapshot', {k: (v['n'], v['max'], v['total']) for k, v in g['rounds'][-1][1].items()})
