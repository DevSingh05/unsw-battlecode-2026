"""Run mech.py (v31 vs v30 binaries) on every game in the ledger played by the v31 family (or given families)
and summarise decision divergences.  python3 notes/top3/regression/run_all.py [fam,fam] [maps]"""
import json, os, sys, pickle, subprocess, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); from versions import version, FAMILY
fams = (sys.argv[1] if len(sys.argv) > 1 else 'v31').split(',')
maps = sys.argv[2].split(',') if len(sys.argv) > 2 else None
L = json.load(open(os.path.join(H, 'ledger_all.json')))
B = os.path.join(H, 'bin')
out = []
for r in sorted(L, key=lambda r: r['at']):
    if FAMILY[version(r['at'])] not in fams or (maps and r['map'] not in maps): continue
    g = r['game']
    if not os.path.exists(os.path.join(ROOT, 'replays/regcheck/%d.replay' % g)): continue
    need = [n for n in ('v31', 'v30') if not os.path.exists(os.path.join(H, 'mech', '%d_%s.pkl' % (g, n)))]
    if need:
        subprocess.run([sys.executable, os.path.join(H, 'mech.py'), str(g), r['side']] + ['%s=%s/%s' % (n, B, n) for n in need],
                       cwd=ROOT, capture_output=True, text=True)
    try:
        a = pickle.load(open(os.path.join(H, 'mech', '%d_v31.pkl' % g), 'rb'))
        b = pickle.load(open(os.path.join(H, 'mech', '%d_v30.pkl' % g), 'rb'))
    except Exception as e:
        print('fail', g, e); continue
    tot = agree = 0; divs = []
    for i in a:
        for x, y in zip(a[i], b[i]):
            tot += 1; agree += x['real'] == x['bot']
            if x['bot'] != y['bot']:
                divs.append((i, x['round'], x['len'], x['head'], x['real'], x['bot'], y['bot']))
                break
    out.append({'game': g, 'map': r['map'], 'opp': r['opp'], 'win': r['win'], 'ranked': r['ranked'], 'ver': version(r['at']),
                'turns': tot, 'agree': agree / max(1, tot), 'divs': divs})
    print('%d %-17s %-22s %s %s turns %5d real==v31 %.3f  lives diverging v31/v30: %d' % (
        g, r['map'], r['opp'][:22], 'W' if r['win'] else 'L', version(r['at']), tot, agree / max(1, tot), len(divs)), flush=True)
    for d in divs: print('      id%d r%d L%d head=%s real=%s v31=%s v30=%s' % d)
json.dump(out, open(os.path.join(H, 'mech_summary_%s.json' % '_'.join(fams)), 'w'), indent=1, default=str)
