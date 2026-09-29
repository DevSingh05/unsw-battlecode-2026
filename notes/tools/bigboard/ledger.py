#!/usr/bin/env python3
"""Length ledger per 100 rounds (notes/23): eats by source vs length lost in deaths, per map/group.
    python3 notes/tools/bigboard/ledger.py
net = spawn + enemy-corpse eats - (own death length - own-corpse eats) - (length given to enemy... ) ; residual = sprint cost
"""
import collections, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import GS, BIG, STRONG, tlv, mean, dcat

def ledger(sub, tag, a, b):
    sp = mean(sum(v for k, v in g[tag]['eats'].items() if a <= k[0] * 100 < b and k[2] == 'spawn') for g in sub)
    own = mean(sum(v for k, v in g[tag]['eats'].items() if a <= k[0] * 100 < b and k[2] == 'own') for g in sub)
    en = mean(sum(v for k, v in g[tag]['eats'].items() if a <= k[0] * 100 < b and k[2] == 'enemy') for g in sub)
    dl = mean(sum(d[1] for d in g[tag]['deaths'] if a <= d[0] < b) for g in sub)
    dn = mean(sum(1 for d in g[tag]['deaths'] if a <= d[0] < b) for g in sub)
    dtr = mean(sum(d[1] for d in g[tag]['deaths'] if a <= d[0] < b and dcat(d[2]) in ('trapped', 'wall', 'nva', 'chose_self', 'feed')) for g in sub)
    dh = mean(sum(d[1] for d in g[tag]['deaths'] if a <= d[0] < b and dcat(d[2]) == 'headon_enemy') for g in sub)
    d0 = mean(tlv(g, tag, max(1, a))[1] for g in sub); d1 = mean(tlv(g, tag, min(500, b))[1] for g in sub)
    return sp, own, en, dl, dn, dtr, dh, d1 - d0

groups = [('BIG top L', lambda g: g['map'] in BIG and g['top'] and not g['win']),
          ('BIG top W', lambda g: g['map'] in BIG and g['top'] and g['win']),
          ('BIG nontop W', lambda g: g['map'] in BIG and not g['top'] and g['win']),
          ('STRONG top W', lambda g: g['map'] in STRONG and g['top'] and g['win'])]
for mp in BIG + STRONG:
    groups.append((mp + ' top', lambda g, mp=mp: g['map'] == mp and g['top']))
print('per 100 rounds: spawn / ownCorpse / enemyCorpse eats | deaths n, len (selfinflicted len, headon len) | dTotal  -- us || them')
for name, f in groups:
    sub = [g for g in GS if f(g)]
    print('%s n=%d' % (name, len(sub)))
    for a, b in ((0, 100), (100, 200), (200, 300), (300, 400), (400, 500)):
        s = []
        for tag in ('us', 'them'):
            sp, own, en, dl, dn, dtr, dh, dt = ledger(sub, tag, a, b)
            s.append('%5.0f %5.0f %4.0f | %4.0f %4.0f (%4.0f %3.0f) | %+5.0f' % (sp, own, en, dn, dl, dtr, dh, dt))
        print('  r%3d  %s  ||  %s' % (a, s[0], s[1]))
