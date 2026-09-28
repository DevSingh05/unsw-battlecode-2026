#!/usr/bin/env python3
"""v16 Default/Trauma loss diagnosis: per-game mechanics for us vs them.

Usage (from project root):
    python3 notes/tools/v16diag/diag.py            # builds notes/tools/v16diag/games.pkl
Reads replays/v16 (+ v15, ab_base for comparison). Read-only over replays.
"""
import json, os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'midgame'))
sys.path.insert(0, os.path.join(HERE, '..'))
from sim2 import simulate  # noqa

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CHECK = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
PHASES = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 501)]
MAPS = ('Default', 'Trauma')


def games():
    out = []
    for g in json.load(open(os.path.join(ROOT, 'replays/v16/ledger.json'))):
        if g['map'] in MAPS:
            out.append(dict(g, src='v16', path=os.path.join(ROOT, 'replays/v16/%d.replay' % g['game'])))
    for g in json.load(open(os.path.join(ROOT, 'replays/v15/ledger.json'))):
        if g['map'] in MAPS:
            out.append(dict(g, src='v15', path=os.path.join(ROOT, 'replays/v15/%d.replay' % g['game'])))
    for g in json.load(open(os.path.join(ROOT, 'replays/ab_base/summary.json'))):
        if g['map'] in MAPS:
            out.append({'game': g['id'], 'opp': g['opp'], 'map': g['map'], 'win': g['win'], 'side': None, 'ranked': False,
                        'src': 'ab_base', 'path': os.path.join(ROOT, 'replays/ab_base/%d.replay' % g['id']), 'us_res': g['us']})
    return [g for g in out if os.path.exists(g['path'])]


def classify(d, G, m):
    """Return (category, via_portal)."""
    r = d['reason']; T = d['team']
    via = False
    mv = d.get('move')
    if mv:
        k = d.get('step_failed', 1) - 1
        if 0 <= k < len(mv):
            e = m.side_edge(d['head'], mv[k])
            via = m.edges.get(e, (0, -1))[0] == 2
    nb = d.get('nbrs', {})
    free = sum(1 for v in nb.values() if v in ('free', 'pearl'))
    trapped = free == 0
    if r == 'HitHeadToHead':
        if 'killer' in d:  # we were standing, someone moved into our head
            cat = 'rammed_by_enemy' if d['killer_team'] != T else 'headon_ally'
        elif 'victim' in d:
            cat = 'ram_enemy' if d['victim_team'] != T else 'headon_ally'
        else:
            cat = 'headon_?'
    elif r == 'HitOtherBody':
        h = d.get('hit')
        if h is None: cat = 'body_?'
        else: cat = 'ally_body' if h['team'] == T else 'enemy_body'
        if trapped: cat += '_trapped'
    elif r == 'HitSelf':
        cat = 'self_trapped' if trapped else 'self'
    elif r == 'HitWall':
        cat = 'wall_trapped' if trapped else 'wall'
    else:
        cat = 'nva'
    return cat, via


def analyse(meta):
    G = simulate(meta['path'])
    m = G['map']; res = G['result']
    us = meta['side']
    if us is None:  # ab_base: match summary
        u = meta['us_res']
        us = 'A' if (res['A']['longest'], res['A']['total']) == (u['longest'], u['total']) else 'B'
    them = 'B' if us == 'A' else 'A'
    rec = {k: meta[k] for k in ('game', 'opp', 'map', 'win', 'ranked', 'src')}
    rec['oppElo'] = meta.get('oppElo'); rec['us'] = us
    rec['end'] = res.get('endReason'); rec['last'] = G['last_round']
    rec['final'] = {'us': res[us], 'them': res[them]}
    # timeline
    snap = dict(G['rounds'])
    tl = {}
    for c in CHECK:
        rr = min(c, G['last_round'])
        s = snap.get(rr) or snap[max(k for k in snap if k <= rr)]
        tl[c] = {side: (s[T]['n'], s[T]['total'], s[T]['max']) for side, T in (('us', us), ('them', them))}
    rec['tl'] = tl
    # first round each side's max >= 8, 12, 16
    firsts = {}
    for side, T in (('us', us), ('them', them)):
        for th in (8, 12, 16, 20):
            firsts[(side, th)] = next((r for r, s in G['rounds'] if s[T]['max'] >= th), None)
    rec['first'] = firsts
    # eats per phase
    eats = collections.Counter()
    for e in G['eats']:
        side = 'us' if e['team'] == us else 'them'
        ph = next(i for i, (a, b) in enumerate(PHASES) if a <= e['round'] < b)
        src = 'spawn' if e['corpse'] is None else ('ownc' if e['corpse'][1] == e['team'] else 'encorpse')
        eats[(side, ph, src)] += 1
    rec['eats'] = eats
    # deaths
    deaths = []
    for d in G['deaths']:
        cat, via = classify(d, G, m)
        side = 'us' if d['team'] == us else 'them'
        king = d.get('king')
        deaths.append({'side': side, 'round': d['round'], 'len': d['len'], 'cat': cat, 'portal': via, 'head': d['head'],
                       'reason': d['reason'], 'age': d['age'], 'id': d['id'],
                       'king_len': king[1] if king else 0, 'king_dist': king[2] if king else None,
                       'enemy_dist': d.get('enemy_near', (0, 0, 99))[2], 'move': d.get('move'),
                       'hit': d.get('hit'), 'nbrs': d.get('nbrs'), 'killer_len': d.get('killer_len'), 'victim_len': d.get('victim_len')})
    rec['deaths'] = deaths
    # was the current longest killed? track top dragon deaths
    # splits
    sp = []
    died_at = {d['id']: (d['round'], d['cat'], d['len']) for d in deaths}
    for s in G['splits']:
        side = 'us' if s['team'] == us else 'them'
        sp.append({'side': side, 'round': s['round'], 'L': s['L'], 'k': s['k'], 'exits': s['exits'], 'enemy_dist': s['enemy_dist'],
                   'parent': s['parent'], 'child': s['child'],
                   'pdeath': died_at.get(s['parent']), 'cdeath': died_at.get(s['child'])})
    rec['splits'] = sp
    # portal crossings (moves whose first step crosses a portal edge)
    cross = collections.Counter()
    for mv in G['moves']:
        steps = mv['act'].get('move', [])
        if not steps: continue
        e = m.side_edge(mv['head'], steps[0])
        if m.edges.get(e, (0, -1))[0] == 2:
            side = 'us' if mv['team'] == us else 'them'
            cross[(side, 'n')] += 1
            if mv.get('died'): cross[(side, 'died')] += 1
    rec['cross'] = cross
    # moves counts / sprints
    rec['nmoves'] = collections.Counter(('us' if mv['team'] == us else 'them') for mv in G['moves'])
    # king (longest) track per round for us/them
    rec['maxlen'] = [(r, s[us]['max'], s[them]['max'], s[us]['n'], s[them]['n'], s[us]['total'], s[them]['total']) for r, s in G['rounds']]
    # our king death events: deaths of dragons that were team max at that time (len>=8)
    return rec


if __name__ == '__main__':
    out = []
    for g in games():
        try:
            out.append(analyse(g))
        except Exception as ex:  # keep going
            print('fail', g['game'], ex)
    pickle.dump(out, open(os.path.join(HERE, 'games.pkl'), 'wb'))
    print(len(out), 'games')
