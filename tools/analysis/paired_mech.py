#!/usr/bin/env python3
"""mech.py <tag> <botdir> <opp1,opp2> <map1,map2,...> <nseeds> : paired sandbox games (seed 2000+i), both sides, 2 at a time.
Writes replays to builder/mech/<tag>/ and rows to builder/mech/<tag>.json"""
import sys, os, subprocess, json, re, itertools
from concurrent.futures import ThreadPoolExecutor
P='/Users/devsingh/Developer/UNSW_Battlecode'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/builder'
sys.path.insert(0, P+'/notes/tools'); import replay_sim as RS
tag, bot, opps, maps, ns = sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4].split(','), int(sys.argv[5])
out = f'{S}/mech/{tag}'; os.makedirs(out, exist_ok=True)
subprocess.run(['touch', bot+'/main.cpp'])
jobs=[]
for mp in maps:
    for oi, opp in enumerate(opps):
        for i in range(ns):
            for side in 'AB':
                jobs.append((mp, opp, 2000+i, side))
def run(j):
    mp, opp, seed, side = j
    name = f"{os.path.basename(mp).replace('.map','')}_{os.path.basename(opp)}_{seed}_{side}"
    rp = f'{out}/{name}.replay'
    a, b = (bot, opp) if side=='A' else (opp, bot)
    env = dict(os.environ)
    if os.environ.get('MECH_TRACE'): env[os.environ['MECH_TRACE']] = f'{out}/{name}.trace'
    r = subprocess.run(['unswbc','run',mp,a,b,'--seed',str(seed),*([] if os.environ.get('MECH_LOGS') else ['--no-logs']),'--sandbox','-o',rp], cwd=P, capture_output=True, text=True, env=env)
    txt = r.stdout + r.stderr
    cpu = re.search(r'team %s points.*max ([0-9.]+)M' % side, txt)
    return name, side, rp, (float(cpu.group(1)) if cpu else None), [l for l in txt.splitlines() if 'wins' in l or 'draw' in l]
# warm the build caches serially
run((maps[0], opps[0], 1, 'A'))
for o in opps[1:]: run((maps[0], o, 1, 'A'))
rows=[]
with ThreadPoolExecutor(2) as ex:
    for name, side, rp, cpu, res in ex.map(run, jobs):
        try:
            g = RS.simulate(rp)
        except Exception as e:
            rows.append({'name': name, 'err': str(e), 'res': res}); continue
        us = side; them = 'B' if us=='A' else 'A'
        uq = 0 if g['team'][0]==us else 1; tq = 1-uq
        d = {x['id']: x for x in g['deaths']}
        row = {'name': name, 'side': side, 'cpu': cpu, 'res': res[0] if res else None, 'result': g['result'],
               'win': g['result'].get('winner')==us}
        def dq(q):
            x = d.get(q)
            if not x: return None
            return {'round': x['round'], 'len': x['len'], 'reason': x['reason'], 'killer_len': x.get('killer_len'), 'killer': x.get('killer'),
                    'victim': x.get('victim'), 'victim_len': x.get('victim_len'), 'hit': x.get('hit'), 'head': x['head'], 'nbrs': x.get('nbrs')}
        row['our_q'] = dq(uq); row['their_q'] = dq(tq)
        # stillborn children: our split children dead within 1 round of birth
        born = {s['child']: s for s in g['splits'] if s['team']==us}
        sb = [(s['round'], s['k'], s['parent']) for c, s in born.items() if c in d and d[c]['round'] - s['round'] <= 1]
        row['stillborn'] = len(sb); row['stillborn100'] = sum(1 for r,k,p in sb if r<=100); row['stillborn_len100'] = sum(k for r,k,p in sb if r<=100)
        row['sb_list'] = sb
        row['splits'] = sum(1 for s in g['splits'] if s['team']==us)
        row['qsplits'] = [(s['round'], s['L'], s['k']) for s in g['splits'] if s['parent']==uq]
        for r, snap in g['rounds']:
            if r in (50, 100, 200, 300, 450, 499):
                row[f'tot{r}'] = snap[us]['total']; row[f'n{r}'] = snap[us]['n']; row[f'max{r}'] = snap[us]['max']
                row[f'etot{r}'] = snap[them]['total']; row[f'en{r}'] = snap[them]['n']
        # head-on rams suffered by our L>=8
        row['ram8'] = [(x['round'], x['len'], x.get('killer_len')) for x in g['deaths'] if x['team']==us and x['reason']=='HitHeadToHead' and x.get('killer') is not None and x['len']>=8]
        row['deaths_us'] = {}
        for x in g['deaths']:
            if x['team']==us: row['deaths_us'][x['reason']] = row['deaths_us'].get(x['reason'],0)+1
        if os.environ.get('MECH_LOGS'):
            import replay_decode as RD
            from collections import Counter
            ev=[e for e in RD.load(rp)['events'] if e['t']=='dragonLog']
            txt=[str(e.get('text') or e.get('message') or e) for e in ev]
            row['r2']=[t for t in txt if 'r2 ' in t]
            row['r2n']=dict(Counter(t.split('r2 ')[1].split()[0] for t in row['r2']))
        rows.append(row)
json.dump(rows, open(f'{S}/mech/{tag}.json','w'), default=str)
if os.environ.get('MECH_LOGS'):
    from collections import Counter
    c=Counter(); g=Counter()
    for r in rows:
        for k,v in r.get('r2n',{}).items(): c[k]+=v; g[k]+=1
    print('r2 events total', dict(c), 'games with', dict(g))
w = sum(1 for r in rows if r.get('win')); print(tag, 'games', len(rows), 'wins', w, 'cpu max', max((r.get('cpu') or 0) for r in rows))
