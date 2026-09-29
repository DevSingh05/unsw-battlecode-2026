"""Pocket throughput: inter-dive gaps, diver origin, child fate after exit."""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
for lab, f in (('CALC vs US', lambda e: e['calc'] and e['vsus']), ('US', lambda e: not e['calc'] and e['vsus']), ('CALC vs oth', lambda e: e['calc'] and not e['vsus']), ('oth', lambda e: not e['calc'] and not e['vsus'])):
    X = [e for e in E if f(e)]
    gaps = []; origin = collections.Counter(); prevd = collections.Counter()
    by = collections.defaultdict(list)
    for e in X: by[(e['gid'], e['p'])].append(e)
    childset = {}
    for e in X:
        for a in [e.get('child')]:
            if a is not None: childset[(e['gid'], a)] = e
    for k, L in by.items():
        L.sort(key=lambda e: e['r0'])
        for a, b in zip(L, L[1:]):
            end_a = a.get('rdeath', a.get('rout', a['r1']))
            gaps.append(b['r0'] - end_a)
    for e in X:
        g = sim(e['gid'])
        par = g['parent_of'].get(e['id'])
        src = childset.get((e['gid'], e['id']))
        if src is not None: origin['child of pocket dive (%s pocket)' % ('same' if src['p'] == e['p'] else 'other')] += 1
        else: origin['other'] += 1
    print('%-12s dives %d  gap(last diver leaves -> next enters) median %s  dist %s' % (lab, len(X), st.median(gaps) if gaps else None, sorted(collections.Counter(min(x, 20) for x in gaps).items())))
    print('     diver origin: %s' % dict(origin))
