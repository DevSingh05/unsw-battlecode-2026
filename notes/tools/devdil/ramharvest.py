#!/usr/bin/env python3
"""Head-on trades between teams: who initiated, lengths, local heads (Manhattan <=R) at the moment,
team units, and who ate the corpse pearls of both dragons.
    python3 notes/tools/devdil/ramharvest.py MAP [R=4]"""
import os, sys, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
GS = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
M = sys.argv[1]; RAD = int(sys.argv[2]) if len(sys.argv) > 2 else 4
agg = collections.defaultdict(lambda: collections.defaultdict(float))
rows = []
for g in GS:
    if not g['map'].startswith(M): continue
    S = simulate(g['path']); us = g['us']; m = S['map']
    snaps = dict(S['rounds'])
    eaten = collections.defaultdict(collections.Counter)  # dead id -> team that ate
    for e in S['eats']:
        if e['corpse']: eaten[e['corpse'][0]]['us' if e['team'] == us else 'them'] += 1
    D = S['deaths']
    for i, d in enumerate(D):
        if d['reason'] != 'HitHeadToHead' or 'victim' not in d: continue
        if d['victim_team'] == d['team']: continue
        init = 'us' if d['team'] == us else 'them'
        vid = d['victim']
        s = snaps.get(d['round'] - 1) or snaps.get(d['round'])
        heads = s['heads'] if s else {}
        loc = collections.Counter()
        for j, (h, L, T) in heads.items():
            if j in (d['id'], vid): continue
            if m.dist(h, d['head']) <= RAD: loc['us' if T == us else 'them'] += 1
        uu = s[us]['n'] if s else 0; tt = s['B' if us == 'A' else 'A']['n'] if s else 0
        eu = eaten[d['id']]['us'] + eaten[vid]['us']; et = eaten[d['id']]['them'] + eaten[vid]['them']
        key = (g['win'], init)
        a = agg[key]
        a['n'] += 1; a['eat_us'] += eu; a['eat_them'] += et
        a['len_init'] += d['len']; a['len_vict'] += d['victim_len']
        a['behind'] += (uu < tt); a['loc_adv'] += (loc['us'] - loc['them']) * (1 if init == 'us' else 1)
        a['games'] = a.get('games', 0)
        # locally outnumbered when we initiated?
        if init == 'us':
            a['init_loc_out'] += (loc['us'] < loc['them'])
        rows.append((g['game'], g['win'], d['round'], init, d['len'], d['victim_len'], uu, tt, loc['us'], loc['them'], eu, et))
ng = collections.Counter(g['win'] for g in GS if g['map'].startswith(M))
for (win, init), a in sorted(agg.items()):
    n = a['n']
    print('%s games(%d) initiated by %-4s: %.1f/g | len initiator %.2f victim %.2f | corpse pearls eaten us %.2f them %.2f per trade | we were behind in units %.0f%% | local heads (r<=%d) us-them %+.2f%s' % (
        'WIN ' if win else 'LOSS', ng[win], init, n / ng[win], a['len_init'] / n, a['len_vict'] / n, a['eat_us'] / n, a['eat_them'] / n, 100 * a['behind'] / n, RAD, a['loc_adv'] / n,
        (' | we initiated while locally outnumbered %.0f%%' % (100 * a['init_loc_out'] / n)) if init == 'us' else ''))
pickle.dump(rows, open(os.path.join(HERE, 'rams_%s.pkl' % M[:3]), 'wb'))
