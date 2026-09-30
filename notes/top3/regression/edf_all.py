"""Count lives where ESCAPE_DEADEND_FIX changes a decision (v31 vs v31_noedf) in every v31-family game that had any
v31/v30 divergence.  python3 notes/top3/regression/edf_all.py"""
import json, os, sys, pickle, subprocess
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
S = json.load(open(os.path.join(H, 'mech_summary_v31.json')))
L = {r['game']: r for r in json.load(open(os.path.join(H, 'ledger_all.json')))}
tot = 0
for s in S:
    if not s['divs']: continue
    g = s['game']; fp = os.path.join(H, 'mech', '%d_v31_noedf.pkl' % g)
    if not os.path.exists(fp):
        subprocess.run([sys.executable, os.path.join(H, 'mech.py'), str(g), L[g]['side'], 'v31_noedf=%s/bin/v31_noedf' % H], cwd=ROOT, capture_output=True)
    a = pickle.load(open(os.path.join(H, 'mech', '%d_v31.pkl' % g), 'rb')); b = pickle.load(open(fp, 'rb'))
    rows = []
    for i in a:
        for x, y in zip(a[i], b[i]):
            if x['bot'] != y['bot']:
                rows.append('id%d r%d L%d v31=%s noEDF=%s' % (i, x['round'], x['len'], x['bot'], y['bot'])); break
    tot += len(rows)
    print(g, s['map'], s['opp'][:18], 'W' if s['win'] else 'L', 'EDF lives', len(rows), '; '.join(rows), flush=True)
print('total EDF-changed lives', tot)
