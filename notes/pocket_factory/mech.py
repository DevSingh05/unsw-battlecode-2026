#!/usr/bin/env python3
"""Pocket-factory mechanism metrics: play CAND vs BASE (both sides) with replays, then per side:
dives, net/dive, dive shapes, stub deaths (len of dragons dying inside pockets), big in-pocket deaths (L>=4),
pocket eats, jam rounds (>=2 own heads inside one pocket component), units/total at r100/r200/end, result.

usage (from project root): python3 notes/pocket_factory/mech.py "bot:-DPOCKET_FACTORY=1" [--base variants/v29]
        [--maps autarky,dilemma] [--seeds 2] [--seed-base 7000] [--jobs 3] [--keep DIR]
Also: python3 notes/pocket_factory/mech.py --replay FILE TEAM   (metrics for one replay/team)
"""
import argparse, collections, concurrent.futures as cf, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'notes/autarky_calc/jam'))
sys.path.insert(0, str(ROOT / 'notes/tools/autarky'))
sys.path.insert(0, str(ROOT / 'notes/tools/midgame'))
sys.path.insert(0, str(ROOT / 'notes/tools'))
import simj  # noqa
from collect import pockets  # noqa


def comps(m, PK):
    cid = {}
    for t in PK:
        if t in cid: continue
        st = [t]; cid[t] = t
        while st:
            u = st.pop()
            for d in 'NESW':
                v = m.step(u, d)
                if v in PK and v not in cid: cid[v] = t; st.append(v)
    return cid


def metrics(path, T):
    S = simj.simulate(path); m = S['map']; PK = pockets(m); cid = comps(m, PK)
    R = dict(S['rounds'])
    ate = collections.Counter((e['id'], e['round']) for e in S['eats'] if e['tile'] in PK)
    splits = collections.defaultdict(list)
    for s in S['splits']: splits[(s['parent'], s['round'])].append(s['k'])
    dives = []; prev = {}
    jam = 0
    for r in sorted(R):
        occ = collections.Counter()
        for j, (t, L, TT) in R[r]['heads'].items():
            if TT == T and t in PK: occ[cid[t]] += 1
            if TT != T: continue
            p = prev.get(j)
            if t in PK and p is not None and p not in PK:
                entry = L - ate[(j, r)]; kids = []; rr = r
                while True:
                    kids += splits.get((j, rr), []); st = R.get(rr)
                    if st is None or j not in st['heads']: out = ('died', 0); break
                    if st['heads'][j][0] not in PK: out = ('out', st['heads'][j][1]); break
                    rr += 1
                    if rr > r + 30: out = ('stuck', 0); break
                dives.append((entry, tuple(kids), out[0], sum(kids) + (out[1] if out[0] == 'out' else 0) - entry))
        jam += sum(1 for v in occ.values() if v >= 2)
        prev = {j: v[0] for j, v in R[r]['heads'].items()}
    pdeath = collections.Counter(); bigdeath = 0
    for d in S['deaths']:
        if d['team'] == T and d['head'] in PK:
            pdeath[min(d['len'], 5)] += 1
            if d['len'] >= 4: bigdeath += 1
    peat = sum(1 for e in S['eats'] if e['team'] == T and e['tile'] in PK)
    eats = sum(1 for e in S['eats'] if e['team'] == T)
    def at(r):
        rs = [x for x in R if x <= r]
        return R[max(rs)][T] if rs else {'n': 0, 'total': 0, 'max': 0}
    res = S['result']
    return {'dives': len(dives), 'net': sum(x[3] for x in dives), 'shapes': collections.Counter((e, k) for e, k, o, _ in dives),
            'pdeath': pdeath, 'bigdeath': bigdeath, 'peat': peat, 'eats': eats, 'jam': jam,
            'r100': at(100), 'r200': at(200), 'end': at(10 ** 9), 'last': S['last_round'], 'result': res}


def run_one(a, b, mp, seed, out):
    cmd = ['unswbc', 'run', str(ROOT / 'maps' / f'{mp}.map'), a, b, '--seed', str(seed), '--no-debug', '-o', out]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cand', nargs='?')
    ap.add_argument('--base', default='variants/v29')
    ap.add_argument('--maps', default='autarky,dilemma')
    ap.add_argument('--seeds', type=int, default=2)
    ap.add_argument('--seed-base', type=int, default=7000)
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--keep', default=None)
    ap.add_argument('--replay', nargs=2, default=None)
    ap.add_argument('--reuse', action='store_true', help='reuse replays already in --keep')
    a = ap.parse_args()
    if a.replay:
        print(metrics(a.replay[0], a.replay[1])); return
    from arena import build, WIN
    ca, ba = build(a.cand), build(a.base)
    tmp = pathlib.Path(a.keep or tempfile.mkdtemp(prefix='pf_', dir=os.environ.get('TMPDIR', '/tmp')))
    tmp.mkdir(parents=True, exist_ok=True)
    jobs = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for mp in a.maps.split(','):
            for s in range(a.seeds):
                seed = a.seed_base + s
                for sw in (False, True):
                    x, y = (ba, ca) if sw else (ca, ba)
                    f = str(tmp / f'{mp}_{seed}_{"B" if sw else "A"}.replay')
                    if a.reuse and os.path.exists(f):
                        jobs.append((mp, seed, sw, f, None)); continue
                    jobs.append((mp, seed, sw, f, ex.submit(run_one, x, y, mp, seed, f)))
        agg = collections.defaultdict(lambda: collections.defaultdict(float))
        for mp, seed, sw, f, fut in jobs:
            if fut is not None:
                fut.result()
            ct, bt = ('B', 'A') if sw else ('A', 'B')
            try:
                win_ = simj.R.load(f)['result'].get('winner')
            except Exception:  # noqa
                win_ = None
            w = 0.5 if win_ not in ('A', 'B') else float(win_ == ct)
            lines = []
            for who, T in (('cand', ct), ('base', bt)):
                try:
                    M = metrics(f, T)
                except Exception as e:  # noqa
                    print('ERR', f, e); continue
                g = agg[(mp, who)]
                g['n'] += 1; g['win'] += w if who == 'cand' else 1 - w
                for k in ('dives', 'net', 'bigdeath', 'peat', 'eats', 'jam'): g[k] += M[k]
                g['stub2'] += M['pdeath'][2]; g['stub3'] += M['pdeath'][3]; g['stub4+'] += M['pdeath'][4] + M['pdeath'][5]
                for r in ('r100', 'r200', 'end'): g[r + 'tot'] += M[r]['total']; g[r + 'n'] += M[r]['n']
                g['elim'] += M['end']['n'] == 0
                lines.append(f"{who} d{M['dives']} net{M['net']:+d} pe{M['peat']} jam{M['jam']} big{M['bigdeath']} tot100 {M['r100']['total']} end {M['end']['n']}u/{M['end']['total']}")
            print(f'{mp} {seed} {"swap" if sw else "    "} W={w} last={M["last"]} | ' + ' | '.join(lines), flush=True)
    print('\nmap        who   n  win   dives net/dive peat  jam  stub2 stub3 stub4+ bigD  tot100 tot200 totEnd unitsEnd elim')
    for (mp, who), g in sorted(agg.items()):
        n = g['n']
        print(f"{mp:10s} {who:4s} {int(n):2d} {g['win'] / n:.2f} {g['dives'] / n:6.1f} {g['net'] / max(1, g['dives']):+7.2f} {g['peat'] / n:5.1f} {g['jam'] / n:5.1f}"
              f" {g['stub2'] / n:5.1f} {g['stub3'] / n:5.1f} {g['stub4+'] / n:5.1f} {g['bigdeath'] / n:5.1f} {g['r100tot'] / n:6.1f} {g['r200tot'] / n:6.1f} {g['endtot'] / n:6.1f} {g['endn'] / n:6.1f} {int(g['elim'])}")


if __name__ == '__main__':
    main()
