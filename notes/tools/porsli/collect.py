#!/usr/bin/env python3
"""Portals / Slithery Fight game set for notes/21. Read-only over replays.

    python3 notes/tools/porsli/collect.py      # -> notes/tools/porsli/games.pkl

Sets: v28 (replays/v28 ledger), old = v19plus (v19-v23) + v16 ledgers.
(No v24-v27 Portals/Slithery replays exist locally: v19plus ends 09-28 23:19, v28 starts 09-29 05:18.)
Per game and team: timeline (units/total/longest), eats by phase and source, every death
classified, king history.
"""
import collections, json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate, Map

MAPS = {'Portals': 'Portals__id20.map', 'Slithery Fight': 'Slithery_Fight__id21.map'}
GAPS = {k: Map(open(os.path.join(ROOT, 'notes/maps', v)).read()).tiles for k, v in MAPS.items()}
CHK = [25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 499]
PH = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 501)]


def games():
    out = []
    for d, ver in (('v28', 'v28'), ('v19plus', 'old'), ('v16', 'old')):
        for g in json.load(open(os.path.join(ROOT, 'replays', d, 'ledger.json'))):
            if g['map'] not in MAPS:
                continue
            p = os.path.join(ROOT, 'replays', d, '%d.replay' % g['game'])
            if os.path.exists(p):
                out.append(dict(g, path=p, ver=ver, dir=d))
    return out


def classify(G, d, feed_king_dist=4):
    m = G['map']
    if d['actor'] != d['id']:
        return 'rammed' if d['reason'] == 'HitHeadToHead' else 'killed_other'
    mv = d.get('move') or ''
    k = d.get('step_failed', 1) - 1
    crossed = bool(mv) and k < len(mv) and m.edges.get(m.side_edge(d['head'], mv[k]), (0, -1))[0] == 2
    r = d['reason']
    if r == 'HitHeadToHead':
        tgt = 'ally' if d.get('victim_team') == d['team'] else 'enemy'
        return ('portal_' if crossed else '') + 'ram_' + tgt
    if r == 'NoValidAction':
        return 'nva'
    if r == 'HitWall':
        return 'wall'
    hit = d.get('hit')
    what = 'self' if r == 'HitSelf' else ('ally' if hit and hit['team'] == d['team'] else ('enemy' if hit else 'other'))
    if crossed:
        return 'portal_' + what
    nb = d.get('nbrs', {})
    free = [x for x, v in nb.items() if v in ('free', 'pearl')]
    if not free:
        return 'trapped_' + what
    kg = d.get('king')
    if kg and kg[1] > d['len'] and kg[2] <= feed_king_dist:
        return 'feed_' + what
    return 'chose_' + what


def analyse(g):
    G = simulate(g['path'])
    us = g['side']; them = 'B' if us == 'A' else 'A'
    gaps = GAPS[g['map']]
    rs = dict(G['rounds'])
    last = G['last_round']
    res = {'game': g['game'], 'map': g['map'], 'ver': g['ver'], 'ranked': g['ranked'], 'win': g['win'], 'opp': g['opp'],
           'oppElo': g.get('oppElo'), 'side': us, 'end': G['result'].get('endReason'), 'last': last, 'result': G['result']}
    for tag, T in (('us', us), ('them', them)):
        tl = {}
        for c in CHK:
            r = rs.get(min(c, last))
            tl[c] = (r[T]['n'], r[T]['total'], r[T]['max']) if r else (0, 0, 0)
        # longest per round, king id
        kings = [(rn, snap[T]['king'], snap[T]['max']) for rn, snap in G['rounds']]
        eats = collections.Counter()
        for e in G['eats']:
            if e['team'] != T:
                continue
            ph = next(i for i, (a, b) in enumerate(PH) if a <= e['round'] < b)
            gp = gaps.get(e['tile'], (0, 0))
            if e['corpse']:
                src = 'corpse_own' if e['corpse'][1] == T else 'corpse_enemy'
            elif gp == (1, 1):
                src = 'hot'
            else:
                src = 'spawn'
            eats[(ph, src)] += 1
        deaths = []
        for d in G['deaths']:
            if d['team'] != T:
                continue
            c = classify(G, d)
            deaths.append({'round': d['round'], 'id': d['id'], 'len': d['len'], 'cls': c, 'reason': d['reason'], 'head': d['head'],
                           'age': d['age'], 'hit': d.get('hit'), 'king': d.get('king'), 'move': d.get('move'),
                           'killer_len': d.get('killer_len'), 'victim_len': d.get('victim_len'), 'enemy_near': d.get('enemy_near'),
                           'nbrs': d.get('nbrs')})
        # was the dying dragon the team's longest at that moment?
        for dd in deaths:
            snap = rs.get(dd['round'] - 1) or rs.get(dd['round'])
            dd['was_king'] = bool(snap and snap[T]['king'] == dd['id']) or bool(snap and dd['len'] >= snap[T]['max'])
        splits = collections.Counter(next(i for i, (a, b) in enumerate(PH) if a <= s['round'] < b) for s in G['splits'] if s['team'] == T)
        fin = G['rounds'][-1][1][T]
        res[tag] = {'tl': tl, 'eats': eats, 'deaths': deaths, 'splits': splits, 'final_lens': fin['lens'],
                    'kings': kings, 'born': {i: G['born'][i] for i in G['born'] if G['team'][i] == T},
                    'parent': {c: p for c, p in G['parent_of'].items() if G['team'][c] == T}}
    return res


if __name__ == '__main__':
    out = []
    for g in games():
        out.append(analyse(g))
        print(g['game'], g['map'], g['ver'], g['win'], file=sys.stderr)
    pickle.dump(out, open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'wb'))
    print(len(out), 'games')
