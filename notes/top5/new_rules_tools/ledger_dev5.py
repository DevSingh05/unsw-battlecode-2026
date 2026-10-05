"""Mass ledger per side (scratch dev5/prof.pkl): per game, per round bucket, + eats (fresh/own corpse/enemy corpse)
and - length lost in deaths by reason (queen separate). usage: python3 ledger_dev5.py SIDE OPP"""
import sys, pickle, collections
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/dev5/'
D = pickle.load(open(S + 'prof.pkl', 'rb'))
OURS = {'q1', 'f1', 'h1', 'b1', 'amb'}
SIDE, OPP = sys.argv[1], sys.argv[2]
m = lambda lab, w: (lab in OURS) if w == 'US' else lab == w
B = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 501)]
for who in ('side', 'opp'):
    C = collections.Counter(); n = 0
    for gid, o in D.items():
        if not o: continue
        lab = o['meta']['lab']
        for T in 'AB':
            E = 'B' if T == 'A' else 'A'
            if not (m(lab[T], SIDE) and m(lab[E], OPP)): continue
            n += 1; r = o[T] if who == 'side' else o[E]
            for (k, v) in r['eats'].items():
                if k[0] == 'cls': continue
                b, kind = k
                bb = 0 if b <= 1 else b - 1
                C[(bb, '+' + kind)] += v
            for d in r['deaths']:
                bb = next(i for i, (lo, hi) in enumerate(B) if lo <= d['round'] < hi)
                why = 'queen' if d['q'] else d['reason'][:8]
                C[(bb, '-' + why)] += d['len']; C[(bb, '#' + why)] += 1
    print(f'== {who} ({SIDE} vs {OPP}), {n} games: per game, per 100 rounds')
    keys = sorted({k[1] for k in C})
    print('%-14s' % '', ' '.join('%9s' % f'r{lo}-{hi - 1}' for lo, hi in B))
    for k in keys:
        print('%-14s' % k, ' '.join('%9.1f' % (C[(b, k)] / n) for b in range(5)))
