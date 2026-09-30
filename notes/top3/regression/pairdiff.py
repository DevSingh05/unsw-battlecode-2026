"""Compare two binaries' decisions on our dragons' reconstructed lives for chosen games.
python3 notes/top3/regression/pairdiff.py NAME_A NAME_B MAP[,MAP] fam[,fam]   (runs mech.py for missing pkls)"""
import json, os, sys, pickle, subprocess
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); from versions import version, FAMILY
na, nb = sys.argv[1], sys.argv[2]; maps = sys.argv[3].split(','); fams = sys.argv[4].split(',')
L = json.load(open(os.path.join(H, 'ledger_all.json')))
for r in sorted(L, key=lambda r: r['at']):
    if r['map'] not in maps or FAMILY[version(r['at'])] not in fams: continue
    g = r['game']
    if not os.path.exists(os.path.join(ROOT, 'replays/regcheck/%d.replay' % g)): continue
    need = [n for n in (na, nb) if not os.path.exists(os.path.join(H, 'mech', '%d_%s.pkl' % (g, n)))]
    if need:
        subprocess.run([sys.executable, os.path.join(H, 'mech.py'), str(g), r['side']] + ['%s=%s/bin/%s' % (n, H, n) for n in need], cwd=ROOT, capture_output=True)
    a = pickle.load(open(os.path.join(H, 'mech', '%d_%s.pkl' % (g, na)), 'rb'))
    b = pickle.load(open(os.path.join(H, 'mech', '%d_%s.pkl' % (g, nb)), 'rb'))
    tot = ag = 0; divs = []
    for i in a:
        for x, y in zip(a[i], b[i]):
            tot += 1; ag += x['real'] == x['bot']
            if x['bot'] != y['bot']:
                divs.append((i, x['round'], x['len'], x['real'], x['bot'], y['bot'])); break
    print('%d %-7s %-5s %-20s %s turns %5d real==%s %.3f lives diverging %s/%s: %d' % (g, r['map'][:7], version(r['at']), r['opp'][:20],
          'W' if r['win'] else 'L', tot, na, ag / max(1, tot), na, nb, len(divs)))
    for d in divs[:12]: print('      id%d r%d L%d real=%s %s=%s %s=%s' % (d[0], d[1], d[2], d[3], na, d[4], nb, d[5]))
