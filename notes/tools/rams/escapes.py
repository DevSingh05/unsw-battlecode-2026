#!/usr/bin/env python3
"""Which fix would have saved each ram?  Reads rams.pkl (rams.py, with sprint options + raw bot distances).
    python3 notes/tools/rams/escapes.py [-v]

Escape actions (all evaluated with the TRUE reach of every enemy, len-1 steps; 'room' = flood area >= L+3):
  step    a 1-step move that is safe
  spr2    a 2-step sprint that is safe (cost 1 segment)
  hold    SPLIT 2 with the head staying put, safe (cost: 2 segments move into a new L2 unit)
  rsplit  SPLIT L-2: the bulk becomes a child whose head is our old tail, tail tile safe (and in view)
  spr3    a 3-step sprint (cost 2)
For a fix the bot must also SEE the option as safe: 'botok' = no visible head flags it under the given rule.
"""
import collections, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(HERE, 'rams.pkl'), 'rb'))
exec(open(os.path.join(HERE, 'agg.py')).read().split("cats = collections.Counter()")[0].split("rams = D['rams']")[0].replace(
    "D = pickle.load(open(os.path.join(os.path.dirname(__file__), 'rams.pkl'), 'rb'))", ""))
exec("def classify" + open(os.path.join(HERE, 'agg.py')).read().split("def classify")[1].split("cats = collections.Counter()")[0])
V = '-v' in sys.argv

RULES = {
    'current': lambda vl, tk: min(max(1, vl - 1), 4),
    'unk3': lambda vl, tk: min(max(1, vl - 1) if tk else max(vl - 1, 3), 4),
}


def botok(o, rule):
    return not any(bd <= rule(vl, tk) for (j, vl, tk, bd) in o.get('bot_raw', []))


def kind(o):
    d = o['d']
    if d in 'NESW': return 'step'
    if d == 'SPLIT2': return 'hold'
    if d == 'RSPLIT': return 'rsplit'
    if d.startswith('SPR'): return 'spr%d' % (len(d) - 3)
    return d


def escapes(r, rule):
    got = collections.OrderedDict()
    for o in r['opts']:
        if o.get('legal') != 'ok' or o['d'] == r['chosen']: continue
        k = kind(o)
        ok = o['safe'] and o['room'] and botok(o, RULES[rule])
        if k == 'rsplit': ok = ok and r['tail_cheb'] <= 3
        if ok: got.setdefault(k, o['d'])
    return got


ORDER = ['step', 'spr2', 'hold', 'rsplit', 'spr3']
tab = collections.Counter(); first = collections.Counter(); ex = collections.defaultdict(list)
for r in D['rams']:
    c = classify(r).split(':')[0]
    # under the current model, the bot sees the chosen tile as threatened only in 'seen'; under unk3 recompute
    ch = next((o for o in r['opts'] if o['d'] == r['chosen']), None)
    seen_unk3 = ch is not None and not botok(ch, RULES['unk3'])
    for rule in ('current', 'unk3'):
        e = escapes(r, rule)
        f = next((k for k in ORDER if k in e), 'none')
        first[(rule, c, f)] += 1
    r['seen_unk3'] = seen_unk3
    tab[(c, 'chosen flagged by unk3' if seen_unk3 else 'not flagged by unk3')] += 1
    if V: print(c, r['game'], r['round'], r['map'][:8], 'L%d' % r['len'], 'chosen', r['chosen'], dict(escapes(r, 'unk3')))

print('chosen tile flagged under tail-unknown rule (unk3):')
for k, v in sorted(tab.items()): print('  %-24s %-26s %3d' % (k[0], k[1], v))
for rule in ('current', 'unk3'):
    print('\nfirst escape (order %s), rule %s:' % (ORDER, rule))
    cats = sorted(set(k[1] for k in first if k[0] == rule))
    for c in cats:
        print('  %-14s' % c, {f: first[(rule, c, f)] for f in ORDER + ['none'] if first[(rule, c, f)]})
