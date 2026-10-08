#!/usr/bin/env python3
"""qp8.py <tag> <botdir|BASE> <map,...> <nseeds> [seed0] : paired sandbox games vs variants/f1 with a waste ledger.
botdir: plays both sides vs f1 (2 games per seed). BASE: f1 vs f1, one game per seed, both sides counted.
Ledger per side-game (selfcause_dev5 classes): boxed-by-ally n/len, stillborn n/len, self-inflicted loss r100-399
(non-queen, non head-on), units r50/r100, total r100/r300, longest at end, wins. QP_J parallel games (default 4)."""
import sys, os, subprocess, json, re, statistics as st
from concurrent.futures import ThreadPoolExecutor
P = '/Users/devsingh/Developer/UNSW_Battlecode'
S = '/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r8'
sys.path.insert(0, P + '/notes/tools/midgame'); sys.path.insert(0, P + '/notes/tools')
import sim2
tag, bot, maps, ns = sys.argv[1], sys.argv[2], sys.argv[3].split(','), int(sys.argv[4])
s0 = int(sys.argv[5]) if len(sys.argv) > 5 else 3000
F1 = P + '/variants/f1'
base = bot == 'BASE'
out = f'{S}/mech/{tag}'; os.makedirs(out, exist_ok=True)

def run(j):
    mp, seed, side = j
    mname = os.path.basename(mp).replace('.map', '')
    rp = f'{out}/{mname}_{seed}_{side}.replay'
    a, b = (F1, F1) if base else ((bot, F1) if side == 'A' else (F1, bot))
    if not os.path.exists(rp):
        r = subprocess.run(['unswbc', 'run', mp, a, b, '--seed', str(seed), '--sandbox', '-o', rp, '--no-logs'], cwd=P, capture_output=True, text=True)
        txt = r.stdout + r.stderr
        cpu = {s_: (float(m.group(1)) if (m := re.search(r'team %s points.*max ([0-9.]+)M' % s_, txt)) else None) for s_ in 'AB'}
        json.dump(cpu, open(rp + '.cpu', 'w'))
    cpu = json.load(open(rp + '.cpu'))
    return mname, side, rp, cpu

def ledger(g, T):
    rd = dict(g['rounds']); last = max(rd)
    r = {'box_n': 0, 'box_len': 0, 'sb_n': 0, 'sb_len': 0, 'self_r100_399': 0}
    for x in g['deaths']:
        if x['team'] != T or x['id'] <= 1 or x['reason'] == 'HitHeadToHead': continue
        if 100 <= x['round'] < 400: r['self_r100_399'] += x['len']
        nb = x.get('nbrs', {})
        free = [d for d, v in nb.items() if v in ('free', 'pearl')]
        ally = [d for d, v in nb.items() if isinstance(v, tuple) and v[0] == 'ally']
        kingd = x['king'][2] if x.get('king') else 99
        if x['age'] <= 1: r['sb_n'] += 1; r['sb_len'] += x['len']
        elif kingd <= 3: pass
        elif not free and ally: r['box_n'] += 1; r['box_len'] += x['len']
    at = lambda k, f: rd[min(k, last)][T][f]
    r.update(n50=at(50, 'n'), n100=at(100, 'n'), t100=at(100, 'total'), t300=at(300, 'total'), max500=rd[last][T]['max'],
             win=int(g['result'].get('winner') == T), bulk=sum(1 for s in g['splits'] if s['team'] == T and s['k'] >= s['L'] - 2 and s['L'] >= 5))
    return r

jobs = [(m, s0 + i, s) for m in maps for i in range(ns) for s in (('A',) if base else ('A', 'B'))]
rows = []
with ThreadPoolExecutor(int(os.environ.get('QP_J', '4'))) as ex:
    for mname, side, rp, cpu in ex.map(run, jobs):
        try: g = sim2.simulate(rp)
        except Exception as e: print('ERR', rp, e); continue
        for T in (('A', 'B') if base else (side,)):
            r = ledger(g, T); r.update(map=mname, cpu=cpu.get(T)); rows.append(r)
json.dump(rows, open(f'{S}/mech/{tag}.json', 'w'))
K = ['box_n', 'box_len', 'sb_n', 'sb_len', 'self_r100_399', 'n50', 'n100', 't100', 't300', 'max500', 'bulk', 'win']
print(tag, 'per side-game means |', ' '.join(K), '| cpu')
for m in list(dict.fromkeys(r['map'] for r in rows)) + ['ALL']:
    R = [r for r in rows if m == 'ALL' or r['map'] == m]
    print(f'{m:16s} n={len(R):2d} |', ' '.join(f'{st.mean(r[k] for r in R):.1f}' for k in K), '|', max(r['cpu'] or 0 for r in R))
