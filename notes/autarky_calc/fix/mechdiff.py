"""First-divergence decisions per dragon life: base vs each fixed binary (mech_<g>_<name>.pkl).
python3 mechdiff.py NAME [verbose]"""
import sys, pickle, os, collections, re
H = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]; verbose = len(sys.argv) > 2
C = collections.Counter(); rows = []
for g in (625768, 617872, 612737, 608221):
    B = pickle.load(open(os.path.join(H, 'mech_%d_base.pkl' % g), 'rb'))
    X = pickle.load(open(os.path.join(H, 'mech_%d_%s.pkl' % (g, name)), 'rb'))
    for i in B:
        for k, (b, x) in enumerate(zip(B[i], X[i])):
            if b['bot'] != x['bot']:
                tag = 'TIP2' if 'TIP2' in x['dbg'] else ('POCKET' if 'POCKET' in x['dbg'] else 'other')
                pk = re.findall(r'POCKET (\S+)', b['dbg']); pk2 = re.findall(r'POCKET (\S+)', x['dbg'])
                key = '%s L%d %s -> %s' % (tag, b['len'], b['bot'].split()[0] + (' ' + b['bot'].split()[1] if b['bot'].startswith('SPLIT') else ''),
                                             x['bot'].split()[0] + (' ' + x['bot'].split()[1] if x['bot'].startswith('SPLIT') else ''))
                C[key] += 1
                rows.append((g, b['round'], i, b['head'], b['len'], b['real'], b['bot'], x['bot'], pk, pk2))
                break
print(name, 'lives with a changed decision:', len(rows))
for k, v in C.most_common(): print('  %4d  %s' % (v, k))
if verbose:
    for r in rows: print('   g%d r%d id%d head=%s L%d real=%s base=%s fix=%s base-pocket=%s fix-pocket=%s' % r)
