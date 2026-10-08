"""cand vs opponents on maps, both sides. Per game: result, elim, units/total at r25/50/100, fresh-pearl eats r<=100
by half, own-corpse eats r<=150. Writes JSONL to rp54_TAG/games.jsonl and prints an aggregate.
usage: mw54.py CAND --opps a,b --maps m1,m2 --seeds 2 --seed-base N --jobs 3 --tag X"""
import argparse, sys, pathlib, collections, concurrent.futures as cf, subprocess, re, json
ROOT = pathlib.Path('/Users/devsingh/Developer/UNSW_Battlecode'); sys.path.insert(0, str(ROOT/'tools')); sys.path.insert(0, str(ROOT/'notes/tools'))
from arena import build
import replay_sim as S
SPD = pathlib.Path('/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad')
RS = (25, 50, 100)


def stats(rp, us):
    g = S.simulate(str(rp)); m = g['map']
    th = 'B' if us == 'A' else 'A'
    st = {T: [p[0] for t, p in m.dragons if 'AB'[t] == T] for T in 'AB'}
    def side(t):  # 0 = our half, 1 = their half, 2 = equal
        du = min(m.dist(t, p) for p in st[us]); dt = min(m.dist(t, p) for p in st[th])
        return 0 if du < dt else 1 if dt < du else 2
    snap = {r: s for r, s in g['rounds']}
    d = {}
    for r in RS:
        s = snap.get(r)
        d[f'u{r}'] = s[us]['n'] if s else 0; d[f'o{r}'] = s[th]['n'] if s else 0
        d[f'L{r}'] = s[us]['total'] if s else 0; d[f'M{r}'] = s[th]['total'] if s else 0
    E = [0, 0, 0, 0]; C = [0, 0]
    for e in g['eats']:
        T = e['team']
        if T is None: continue
        if e['corpse'] is None:
            if e['round'] <= 100:
                sd = side(tuple(e['tile']))
                if sd < 2: E[(0 if T == us else 2) + sd] += 1
        elif e['round'] <= 150 and e['corpse'][1] == T:
            C[0 if T == us else 1] += 1
    d['E'] = E; d['C'] = C
    # heads in the other half at r50/r100 is costly to compute here; skip
    sui = [0, 0]
    for mv in g['moves']:
        if mv.get('suicide') and mv['round'] <= 150: sui[0 if mv['team'] == us else 1] += 1
    d['sui'] = sui
    return d


def one(oname, ob, c, mp, seed, sw, out):
    A, B = (ob, c) if sw else (c, ob)
    rp = out/f"{pathlib.Path(oname).name}_{mp.replace('/','_')}_{seed}_{sw}.replay"
    t = subprocess.run(['unswbc', 'run', str(ROOT/'maps'/f'{mp}.map'), A, B, '--seed', str(seed), '--no-debug', '-o', str(rp)], capture_output=True, text=True, cwd=ROOT)
    t = t.stdout+t.stderr; mm = re.search(r"team ([AB]) wins after (\d+) rounds \(([^)]*)\)", t)
    us = 'B' if sw else 'A'; res = 0.5 if not mm else float(mm.group(1) == us); why = mm.group(3) if mm else 'draw'
    el = ('elim' in why) if mm else False
    try: d = stats(rp, us)
    except Exception as ex: d = {'err': str(ex)}
    d.update(opp=pathlib.Path(oname).name, map=mp, seed=seed, sw=sw, res=res, why=why, elim=el, rounds=int(mm.group(2)) if mm else 500)
    return d


def agg(rows, label):
    n = len(rows)
    if not n: return
    g = lambda k: sum(r.get(k, 0) for r in rows)/n
    el_l = sum(1 for r in rows if r['elim'] and r['res'] == 0); el_w = sum(1 for r in rows if r['elim'] and r['res'] == 1)
    E = [sum(r.get('E', [0]*4)[i] for r in rows)/n for i in range(4)]; C = [sum(r.get('C', [0, 0])[i] for r in rows)/n for i in range(2)]
    su = [sum(r.get('sui', [0, 0])[i] for r in rows)/n for i in range(2)]
    print(f"{label:18s} {sum(r['res'] for r in rows):5.1f}/{n}={sum(r['res'] for r in rows)/n:.3f} elimL {el_l} elimW {el_w} | "
          f"units {g('u25'):.1f}/{g('u50'):.1f}/{g('u100'):.1f} v {g('o25'):.1f}/{g('o50'):.1f}/{g('o100'):.1f} | "
          f"len {g('L25'):.0f}/{g('L50'):.0f}/{g('L100'):.0f} v {g('M25'):.0f}/{g('M50'):.0f}/{g('M100'):.0f} | "
          f"fresh<=100 us own/their {E[0]:.1f}/{E[1]:.1f} them our/own {E[2]:.1f}/{E[3]:.1f} | owncorpse<=150 {C[0]:.1f} v {C[1]:.1f} | sui {su[0]:.1f} v {su[1]:.1f}")


def report(rows):
    agg(rows, 'ALL')
    for k in sorted({r['opp'] for r in rows}): agg([r for r in rows if r['opp'] == k], k)
    for k in sorted({r['map'] for r in rows}): agg([r for r in rows if r['map'] == k], k)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('--opps', default='variants/v51')
    ap.add_argument('--maps', default='autarky,devil,queen_of_spades,sprint/tower_defense,sprint/australia,sprint/maze,dilemma')
    ap.add_argument('--seeds', type=int, default=2); ap.add_argument('--seed-base', type=int, default=54000); ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--tag', default='x'); ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    out = SPD/f'rp54_{a.tag}'; out.mkdir(exist_ok=True)
    if a.report:
        report([json.loads(l) for l in open(out/'games.jsonl')]); sys.exit()
    c = build(a.cand); opps = [(o, build(o)) for o in a.opps.split(',')]
    jobs = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for on, ob in opps:
            for mp in a.maps.split(','):
                for s in range(a.seeds):
                    for sw in (0, 1): jobs.append(ex.submit(one, on, ob, c, mp, a.seed_base+s, sw, out))
        rows = [j.result() for j in jobs]
    with open(out/'games.jsonl', 'w') as f:
        for r in rows: f.write(json.dumps(r)+'\n')
    report(rows)
