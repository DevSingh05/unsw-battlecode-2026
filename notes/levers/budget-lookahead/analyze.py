#!/usr/bin/env python3
"""Summarise replycheck.py output.  python3 analyze.py OUT.pkl"""
import pickle, sys, collections
R = pickle.load(open(sys.argv[1], 'rb'))
first = lambda a: (a or '')[:1] if a and len(a) == 1 else a
pre = collections.Counter(); far = collections.Counter()
for key, x in R.items():
    b, c, R0 = x['base'], x['cand'], x['R0']
    for rn in c:
        if rn not in b or b[rn]['L'] < 8: continue
        k = R0 - rn
        bucket = pre if 1 <= k <= 3 else (far if k >= 6 else None)
        if bucket is None: continue
        bucket['dec'] += 1
        ba, ca = b[rn]['arrow'], c[rn]['arrow']
        rep = c[rn]['reply']
        if rep: bucket['fired'] += 1
        bf = rep.get(ba) if ba in rep else None
        if bf and bf[1] <= 1: bucket['base_forced'] += 1
        if ba != ca:
            bucket['changed'] += 1
            cf = rep.get(ca)
            if bf and bf[1] <= 1 and not (cf and cf[1] <= 1): bucket['changed_to_unforced'] += 1
print('R0-1..3 (pre-ram):', dict(pre))
print('R0-6.. (ordinary):', dict(far))
# per ram: did the candidate move differently in the 3 decisions before the ram, and to an unforced move?
per = collections.Counter(); bycat = collections.defaultdict(collections.Counter)
for key, x in R.items():
    b, c, R0 = x['base'], x['cand'], x['R0']
    ch = any(rn in b and b[rn]['arrow'] != c[rn]['arrow'] and 1 <= R0 - rn <= 3 for rn in c)
    atR0 = R0 in b and R0 in c and b[R0]['arrow'] != c[R0]['arrow']
    per['rams'] += 1; per['changed_R0-1..3'] += ch; per['changed_at_R0'] += atR0
    bycat[x['cat']]['n'] += 1; bycat[x['cat']]['changed'] += ch
print('per ram:', dict(per))
for k, v in sorted(bycat.items(), key=lambda kv: -kv[1]['n']): print('  %-32s %s' % (k, dict(v)))
