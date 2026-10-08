#!/usr/bin/env python3
"""qp10.py <tag> <botdir> <maps,...> <nseeds> [seed0]: paired sandbox games vs variants/b3 (QP_SIDES, default AB), QP_J at a time."""
import sys, os, subprocess, json, re, statistics as st
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
P='/Users/devsingh/Developer/UNSW_Battlecode'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r10'
sys.path.insert(0, P+'/notes/tools'); import replay_sim as RS
tag, bot, maps, ns = sys.argv[1], sys.argv[2], sys.argv[3].split(','), int(sys.argv[4])
s0 = int(sys.argv[5]) if len(sys.argv)>5 else 3000
opp = P+'/variants/b3'; sides=os.environ.get('QP_SIDES','AB')
out=f'{S}/mech/{tag}'; os.makedirs(out, exist_ok=True)
def run(j):
    mp, seed, side = j
    mname=os.path.basename(mp).replace('.map','')
    name=f'{mname}_{seed}_{side}'; rp=f'{out}/{name}.replay'
    a,b=(bot,opp) if side=='A' else (opp,bot)
    r=subprocess.run(['unswbc','run',mp,a,b,'--seed',str(seed),'--sandbox','-o',rp,'--no-logs'],cwd=P,capture_output=True,text=True)
    txt=r.stdout+r.stderr
    cpu={s_:(float(m.group(1)) if (m:=re.search(r'team %s points.*max ([0-9.]+)M'%s_,txt)) else None) for s_ in 'AB'}
    return mname, name, side, rp, cpu
jobs=[(m, s0+i, s) for m in maps for i in range(ns) for s in sides]
run((jobs[0][0], 1, 'A'))  # build once
rows=[]
with ThreadPoolExecutor(int(os.environ.get('QP_J','4'))) as ex:
    for mname, name, side, rp, cpu in ex.map(run, jobs):
        try: g=RS.simulate(rp)
        except Exception as e: print('ERR', name, e); continue
        for who,T in (('us',side),('op','B' if side=='A' else 'A')):
            q=0 if g['team'][0]==T else 1
            rd=dict(g['rounds']); last=g['last_round']
            qd=next((d for d in g['deaths'] if d['id']==q),None)
            win=g['result'].get('winner')==T
            row={'map':mname,'name':name,'who':who,'cpu':cpu[T],'win':win,'last':last,
                 'qdr':qd['round'] if qd else 999,'qdlen':qd['len'] if qd else None,'qdwhy':str(qd['reason']) if qd else None,
                 'elim': (not win) and last<499 and (last in rd and rd[last][T]['n']==0 or 'lim' in str(g['result'].get('endReason')))}
            for r in (30,50,100,150,200,300):
                rr=min(r,last)
                row[f'ql{r}']=rd[rr][T]['ids'].get(q,0) if rr in rd else 0
                row[f'n{r}']=rd[rr][T]['n'] if rr in rd else 0
                row[f't{r}']=rd[rr][T]['total'] if rr in rd else 0
            rows.append(row)
json.dump(rows,open(f'{S}/mech/{tag}.json','w'),default=str)
