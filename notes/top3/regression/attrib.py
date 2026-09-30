"""Attribute v31-vs-v30 decision divergences to KING_CONSENSUS or ESCAPE_DEADEND_FIX: a life whose first decision
differs between v31 and v31_nokc (KC=0) is a KC life; between v31 and v31_noedf an EDF life.
python3 notes/top3/regression/attrib.py GAME SIDE [GAME SIDE ...]"""
import os, sys, pickle, subprocess
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
args = sys.argv[1:]
for g, side in zip(args[::2], args[1::2]):
    need = [n for n in ('v31', 'v30', 'v31_nokc', 'v31_noedf') if not os.path.exists(os.path.join(H, 'mech', '%s_%s.pkl' % (g, n)))]
    if need:
        subprocess.run([sys.executable, os.path.join(H, 'mech.py'), g, side] + ['%s=%s/bin/%s' % (n, H, n) for n in need], cwd=ROOT, capture_output=True)
    P = {n: pickle.load(open(os.path.join(H, 'mech', '%s_%s.pkl' % (g, n)), 'rb')) for n in ('v31', 'v30', 'v31_nokc', 'v31_noedf')}
    def firstdiv(a, b):
        out = {}
        for i in a:
            for x, y in zip(a[i], b[i]):
                if x['bot'] != y['bot']:
                    out[i] = (x['round'], x['len'], x['bot'], y['bot'], x['dbg']); break
        return out
    d30, dkc, ded = firstdiv(P['v31'], P['v30']), firstdiv(P['v31'], P['v31_nokc']), firstdiv(P['v31'], P['v31_noedf'])
    print('game', g, 'lives v31!=v30: %d  KC lives: %d  EDF lives: %d' % (len(d30), len(dkc), len(ded)))
    for i, (r, L, a, b, dbg) in sorted(ded.items(), key=lambda x: x[1][0]):
        print('   EDF id%d r%d L%d v31=%s noEDF=%s' % (i, r, L, a, b))
    lens = sorted(v[1] for v in dkc.values())
    print('   KC first-divergence rounds:', sorted(v[0] for v in dkc.values())[:40], 'lens', lens[:40])
