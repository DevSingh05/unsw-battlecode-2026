#!/usr/bin/env python3
"""Devil / Prisoners Dilemma per-game metrics for us vs them (notes/19).

    python3 notes/tools/devdil/collect.py      # builds notes/tools/devdil/games.pkl
Sources: replays/v19plus (ledger), replays/v16 (ledger), replays/ab_v16 (summary). Read-only.
Version guess from battle time (journal): <19:16 v16, <19:31 v17, <20:00 v18/v19, <20:15 v20, <23:09 v21, else v22.
"""
import json, os, pickle, sys, collections, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/v16diag'))
from sim2 import simulate, Map  # noqa
import replay_decode as R  # noqa
from diag import classify  # noqa

MAPS = ('Devil', 'Prisoners Dilemma')
REF = {'Devil': 'notes/maps/Devil__id13.map', 'Prisoners Dilemma': 'notes/maps/Prisoners_Dilemma__id17.map'}
CHECK = [10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500]
PHASES = [(0, 50), (50, 100), (100, 200), (200, 300), (300, 501)]


def version(at):
    if not at: return '?'
    hm = at[11:16]
    if at[:10] < '2026-09-28': return 'old'
    if hm < '19:16': return 'v16'
    if hm < '19:31': return 'v17'
    if hm < '20:00': return 'v18/19'
    if hm < '20:15': return 'v20'
    if hm < '23:09': return 'v21'
    return 'v22'


def games():
    out = {}
    for src in ('v19plus', 'v16'):
        for g in json.load(open(os.path.join(ROOT, 'replays/%s/ledger.json' % src))):
            if g['map'] in MAPS:
                out[g['game']] = dict(g, src=src, ver=version(g.get('at')), path=os.path.join(ROOT, 'replays/%s/%d.replay' % (src, g['game'])))
    for f in glob.glob(os.path.join(ROOT, 'replays/ab_*/summary.json')):
        src = os.path.basename(os.path.dirname(f))
        for g in json.load(open(f)):
            if g['map'] in MAPS and g['id'] not in out:
                out[g['id']] = {'game': g['id'], 'opp': g['opp'], 'map': g['map'], 'win': g['win'], 'side': None, 'ranked': False,
                                'src': src, 'ver': src[3:], 'path': os.path.join(os.path.dirname(f), '%d.replay' % g['id']), 'us_res': g['us']}
    return [g for g in out.values() if os.path.exists(g['path'])]


def analyse(meta):
    G = simulate(meta['path'])
    m = G['map']; res = G['result']
    ref = Map(open(os.path.join(ROOT, REF[meta['map']])).read())
    us = meta['side']
    if us is None:
        u = meta['us_res']; us = 'A' if res['A'] == u else 'B'
    them = 'B' if us == 'A' else 'A'
    rec = {k: meta.get(k) for k in ('game', 'opp', 'oppElo', 'map', 'win', 'ranked', 'src', 'ver', 'path')}
    rec['us'] = us; rec['end'] = res.get('endReason'); rec['last'] = G['last_round']
    rec['final'] = {'us': res[us], 'them': res[them]}
    # layout: which team starts on the left (x<16)
    st = [(t, pts[0]) for t, pts in m.dragons]
    left_team = 'AB'[st[0][0]] if st[0][1][0] < 16 else 'AB'[1 - st[0][0]]
    rec['we_left'] = (left_team == us)
    snaps = dict(G['rounds'])
    tl = {}
    for r in CHECK:
        rr = min(r, G['last_round'])
        s = snaps.get(rr)
        if s is None: continue
        if r > G['last_round']:
            tl[r] = {w: (s[T]['n'], s[T]['total'], s[T]['max']) for w, T in (('us', us), ('them', them))}
        else:
            tl[r] = {w: (s[T]['n'], s[T]['total'], s[T]['max']) for w, T in (('us', us), ('them', them))}
    rec['tl'] = tl
    rec['series'] = [(r, s[us]['n'], s[us]['total'], s[us]['max'], s[them]['n'], s[them]['total'], s[them]['max']) for r, s in G['rounds']]

    def ph(r):
        for i, (a, b) in enumerate(PHASES):
            if a <= r < b: return i
        return len(PHASES) - 1
    eats = collections.defaultdict(collections.Counter)
    for e in G['eats']:
        w = 'us' if e['team'] == us else 'them'
        gap = ref.tiles.get(tuple(e['tile']), (0, 0))
        kind = 'corpse' if e['corpse'] else ('hot' if gap == (1, 1) else 'spawn')
        eats[w][(ph(e['round']), kind)] += 1
    rec['eats'] = {k: dict(v) for k, v in eats.items()}
    deaths = collections.defaultdict(collections.Counter); dl = []
    for d in G['deaths']:
        w = 'us' if d['team'] == us else 'them'
        cat, via = classify(d, G, m)
        deaths[w][(ph(d['round']), cat)] += 1
        dl.append({'round': d['round'], 'who': w, 'id': d['id'], 'len': d['len'], 'cat': cat, 'portal': via, 'head': d['head'],
                   'age': d['age'], 'victim_len': d.get('victim_len'), 'killer_len': d.get('killer_len'), 'move': d.get('move'),
                   'nbrs': d.get('nbrs'), 'enemy_near': d.get('enemy_near'), 'king': d.get('king'), 'actor': d['actor']})
    rec['deaths'] = {k: dict(v) for k, v in deaths.items()}; rec['dl'] = dl
    sp = collections.defaultdict(collections.Counter)
    for s in G['splits']:
        w = 'us' if s['team'] == us else 'them'
        sp[w][ph(s['round'])] += 1
    rec['splits'] = {k: dict(v) for k, v in sp.items()}
    rec['splitlist'] = [dict(s, who='us' if s['team'] == us else 'them') for s in G['splits']]
    return rec


def main():
    out = []
    for meta in sorted(games(), key=lambda g: g['game']):
        try:
            out.append(analyse(meta))
        except Exception as ex:  # noqa
            print('fail', meta['game'], ex)
    pickle.dump(out, open(os.path.join(HERE, 'games.pkl'), 'wb'))
    print(len(out), 'games')


if __name__ == '__main__':
    main()
