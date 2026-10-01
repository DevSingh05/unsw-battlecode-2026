"""For each queen killed head-on: at her last turn before death, did a 1-step move exist that left her outside every enemy head's reach? usage: qescape.py <dir>"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
import sim2
def reach(L): return -(-L // 4) + max(0, L - 2)
for p in sorted(glob.glob(os.path.join(sys.argv[1], 'v3*_s?.replay'))):
    tag = os.path.basename(p)[:-7]; g = sim2.simulate(p); m = g['map']; a, b = tag.split('_')[:2]
    for d in g['deaths']:
        q = d['id']
        if q not in (0, 1) or 'killer' not in d: continue
        last = [x for x in g['moves'] if x['id'] == q and x['round'] < d['round'] or (x['id'] == q and x['round'] == d['round'] and q < d['killer'])]
        if not last: continue
        lr = last[-1]['round']; st = sim2.simulate(p, stop=(lr, q))
        if not isinstance(st, dict) or 'body' not in st: continue
        body, team = st['body'], st['team']; occ = set(s for j in body for s in body[j][:-1])
        h = body[q][0]; en = [(body[j][0], len(body[j])) for j in body if team[j] != team[q]]
        def threats(t): return [(L, m.dist(t, eh)) for eh, L in en if m.dist(t, eh) <= reach(L)]
        opts = []
        for dd in 'NESW':
            t = m.step(h, dd)
            if t is None or t in occ: continue
            opts.append((dd, len(threats(t)) == 0))
        print(f"{tag:26} q{q} {(a,b)[q]:4} r{lr}->{d['round']} L{len(body[q])} took={''.join(st['act'].get('move',[]))} threats_now={threats(h)} legal1={[o[0] for o in opts]} safe1={[o[0] for o in opts if o[1]]}")
