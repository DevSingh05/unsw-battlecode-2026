#!/usr/bin/env python3
"""King analysis over games.pkl + replays.
    python3 notes/tools/porsli/king.py Portals|Slithery [v28|old|all]
Per team: final king (birth, parent chain), length curve, king eats per 100 rounds by source,
number of L>=10 dragons alive, and big (L>=15) deaths by class with length lost after r350.
"""
import collections, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
from sim2 import simulate
sys.path.insert(0, os.path.dirname(__file__))
from collect import GAPS

G = pickle.load(open(os.path.join(os.path.dirname(__file__), 'games.pkl'), 'rb'))
mp = sys.argv[1] if len(sys.argv) > 1 else 'Portals'
ver = sys.argv[2] if len(sys.argv) > 2 else 'v28'
gs = [g for g in G if g['map'].startswith(mp) and (ver == 'all' or g['ver'] == ver)]
paths = {}
import json
for d in ('v28', 'v19plus', 'v16'):
    for x in json.load(open(os.path.join(ROOT, 'replays', d, 'ledger.json'))):
        paths.setdefault(x['game'], os.path.join(ROOT, 'replays', d, '%d.replay' % x['game']))

agg = {k: collections.defaultdict(list) for k in ('LOSS', 'WIN')}
for g in sorted(gs, key=lambda g: (g['win'], g['game'])):
    S = simulate(paths[g['game']])
    rs = dict(S['rounds'])
    grp = 'WIN' if g['win'] else 'LOSS'
    line = []
    for tag, T in (('us', g['side']), ('them', 'B' if g['side'] == 'A' else 'A')):
        fin = S['rounds'][-1][1][T]
        k = fin['king']
        if k is None:
            continue
        born = S['born'][k]
        # length curve of this dragon
        curve = {c: rs[c][T]['ids'].get(k, 0) for c in (300, 350, 400, 450, 499) if c in rs}
        # eats by the final king per window
        ke = collections.Counter()
        for e in S['eats']:
            if e['id'] == k:
                w = min(e['round'] // 100, 4)
                src = 'c' if e['corpse'] else ('h' if GAPS[g['map']].get(e['tile']) == (1, 1) else 's')
                ke[(w, src)] += 1
        # L>=10 dragons alive
        n10 = {c: sum(1 for L in rs[c][T]['ids'].values() if L >= 10) for c in (400, 450, 499) if c in rs}
        # max length ever and the first round the final king became longest for good
        own = None
        for rn, sn in S['rounds']:
            if sn[T]['king'] != k:
                own = None
            elif own is None:
                own = rn
        maxever = max(sn[T]['max'] for rn, sn in S['rounds'])
        bigd = [d for d in g[tag]['deaths'] if d['len'] >= 15]
        lost350 = sum(d['len'] for d in g[tag]['deaths'] if d['len'] >= 10 and d['round'] >= 350)
        a = agg[grp]
        a[tag + '_born'].append(born); a[tag + '_own'].append(own)
        for c, v in curve.items():
            a['%s_k%d' % (tag, c)].append(v)
        for w in range(5):
            for s in 'hsc':
                a['%s_e%d%s' % (tag, w, s)].append(ke[(w, s)])
        for c, v in n10.items():
            a['%s_n10_%d' % (tag, c)].append(v)
        a[tag + '_maxever'].append(maxever); a[tag + '_lost350'].append(lost350)
        a[tag + '_big15'].append(len(bigd))
        line.append('%s king id%d born r%d longest-from r%s curve %s eats(s/c) %s | n10@450 %s | maxever %d | L>=10 lost r350+ %d' % (
            tag, k, born, own, '/'.join(str(curve.get(c, '-')) for c in (300, 350, 400, 450, 499)),
            ' '.join('%d/%d' % (ke[(w, 's')] + ke[(w, 'h')], ke[(w, 'c')]) for w in range(2, 5)), n10.get(450), maxever, lost350))
    print(g['game'], grp, g['opp'][:14])
    for l in line:
        print('   ', l)

for grp, a in agg.items():
    if not a:
        continue
    print('\n====', grp)
    m = lambda k: sum(a[k]) / len(a[k]) if a[k] else float('nan')
    for tag in ('us', 'them'):
        print(' %s: king born %.0f, longest-from %.0f; curve r300..499 %s; maxever %.1f; L>=10 lost r350+ %.1f; L>=15 deaths %.2f' % (
            tag, m(tag + '_born'), m(tag + '_own'), ' '.join('%.1f' % m('%s_k%d' % (tag, c)) for c in (300, 350, 400, 450, 499)),
            m(tag + '_maxever'), m(tag + '_lost350'), m(tag + '_big15')))
        print('     king eats per 100 (hot/spawn/corpse): ' + '  '.join('r%d: %.1f/%.1f/%.1f' % (w * 100, m('%s_e%dh' % (tag, w)), m('%s_e%ds' % (tag, w)), m('%s_e%dc' % (tag, w))) for w in range(1, 5)))
        print('     L>=10 alive @400/450/499: %s' % ' '.join('%.1f' % m('%s_n10_%d' % (tag, c)) for c in (400, 450, 499)))
