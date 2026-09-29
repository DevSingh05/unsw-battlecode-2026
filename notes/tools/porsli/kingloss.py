#!/usr/bin/env python3
"""Where does the king's length go?  python3 notes/tools/porsli/kingloss.py Portals|Slithery [v28|old|all] [-v]
For every turn taken by the team's current longest dragon (longest at the end of the previous round),
r250-499: eats, sprint cost (steps-1), split-away length (reverse splits: the child becomes the new
longest, so the mass stays -> counted separately), death (length lost), and handovers (the longest
changes to a different lineage without a split or death, i.e. someone else outgrew it).
"""
import collections, json, os, sys, pickle
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
verbose = '-v' in sys.argv
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
paths = {}
for d in ('v28', 'v19plus', 'v16'):
    for x in json.load(open(os.path.join(ROOT, 'replays', d, 'ledger.json'))):
        paths.setdefault(x['game'], os.path.join(ROOT, 'replays', d, '%d.replay' % x['game']))
agg = {k: collections.Counter() for k in ('LOSS', 'WIN')}
cnt = collections.Counter()
for g in gs:
    S = simulate(paths[g['game']])
    grp = 'WIN' if g['win'] else 'LOSS'
    cnt[grp] += 1
    kingAt = {rn: sn[T]['king'] for rn, sn in S['rounds'] for T in [None]} if False else None
    for tag, T in (('us', g['side']), ('them', 'B' if g['side'] == 'A' else 'A')):
        kAt = {rn: (sn[T]['king'], sn[T]['max']) for rn, sn in S['rounds']}
        C = agg[grp]
        ev = []
        for mv in S['moves']:
            r = mv['round']
            if r < 250 or mv['team'] != T:
                continue
            k = kAt.get(r - 1)
            if not k or mv['id'] != k[0] or k[1] < 8:
                continue
            if mv.get('suicide'):
                C[tag + '_suicide'] += 1
                continue
            C[tag + '_eat'] += mv['ate']
            if mv['steps'] > 1:
                C[tag + '_sprints'] += 1
                paid = mv['steps'] - 1 if not mv.get('died') else max(0, mv['steps'] - 1)
                C[tag + '_sprintcost'] += paid
                if verbose and tag == 'us':
                    ev.append('r%d sprint %d L%d' % (r, mv['steps'], mv['len_before']))
            if mv.get('died'):
                C[tag + '_death'] += 1
                C[tag + '_deathlen'] += mv['len_before']
                if verbose and tag == 'us':
                    ev.append('r%d DIED L%d %s' % (r, mv['len_before'], mv['died']))
        for s in S['splits']:
            r = s['round']
            if r < 250 or s['team'] != T:
                continue
            k = kAt.get(r - 1)
            if not k or s['parent'] != k[0] or k[1] < 8:
                continue
            if s['k'] >= s['L'] - s['k']:
                C[tag + '_revsplit'] += 1
                C[tag + '_revsplit_left'] += s['L'] - s['k']   # parent head part left behind
                if verbose and tag == 'us':
                    ev.append('r%d revsplit L%d->child %d' % (r, s['L'], s['k']))
            else:
                C[tag + '_peel'] += 1
                C[tag + '_peel_len'] += s['k']
                if verbose and tag == 'us':
                    ev.append('r%d peel L%d k%d' % (r, s['L'], s['k']))
        for d in S['deaths']:
            r = d['round']
            if r < 250 or d['team'] != T:
                continue
            k = kAt.get(r - 1)
            if k and k[1] >= 8 and d['id'] == k[0] and d['actor'] != d['id']:
                C[tag + '_rammed'] += 1
                C[tag + '_rammedlen'] += d['len']
                if verbose and tag == 'us':
                    ev.append('r%d RAMMED L%d' % (r, d['len']))
        if verbose and tag == 'us':
            print(g['game'], 'W' if g['win'] else 'L', ' | '.join(ev))
for grp in ('LOSS', 'WIN'):
    n = cnt[grp]
    if not n:
        continue
    C = agg[grp]
    print('==== %s %s %s (%d), current-longest (L>=8) turns r250-499, per game' % (mp, ver, grp, n))
    for tag in ('us', 'them'):
        f = lambda k: C[tag + '_' + k] / n
        print('  %-4s eats %.1f | sprints %.1f cost %.1f | peel splits %.1f (len %.1f) | reverse splits %.1f (head part left %.1f) | died on own move %.2f (len %.1f) | rammed %.2f (len %.1f) | suicide %.2f' % (
            tag, f('eat'), f('sprints'), f('sprintcost'), f('peel'), f('peel_len'), f('revsplit'), f('revsplit_left'), f('death'), f('deathlen'), f('rammed'), f('rammedlen'), f('suicide')))
