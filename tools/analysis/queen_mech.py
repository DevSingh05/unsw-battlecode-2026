#!/usr/bin/env python3
"""qp.py <tag> <botdir> <map[:seedround],...> <nseeds> [seed0] : paired sandbox games vs variants/b1 (both sides), QP_J at a time (default 4).
Per map prints us vs b1 (the opponent in the same games): queen alive at seed round / r500, queen len at end, tot100, tot300, longest at end, eliminated."""
import sys, os, subprocess, json, re, statistics as st
from concurrent.futures import ThreadPoolExecutor
P='/Users/devsingh/Developer/UNSW_Battlecode'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r7'
sys.path.insert(0, P+'/notes/tools'); import replay_sim as RS
tag, bot, maps, ns = sys.argv[1], sys.argv[2], sys.argv[3].split(','), int(sys.argv[4])
s0 = int(sys.argv[5]) if len(sys.argv)>5 else 2000
opp = os.environ.get('QP_OPP', P+'/variants/b1')
out=f'{S}/mech/{tag}'; os.makedirs(out, exist_ok=True)
def run(j):
    mp, seedr, seed, side = j
    mname=os.path.basename(mp).replace('.map','')
    name=f'{mname}_{seed}_{side}'; rp=f'{out}/{name}.replay'
    a,b=(bot,opp) if side=='A' else (opp,bot)
    r=subprocess.run(['unswbc','run',mp,a,b,'--seed',str(seed),'--sandbox','-o',rp]+([] if os.environ.get('QP_LOGS') else ['--no-logs']),cwd=P,capture_output=True,text=True)
    txt=r.stdout+r.stderr
    cpu={s_:(float(m.group(1)) if (m:=re.search(r'team %s points.*max ([0-9.]+)M'%s_,txt)) else None) for s_ in 'AB'}
    return mname, seedr, name, side, rp, cpu
jobs=[]
for m in maps:
    mp, _, sr = m.partition(':'); sr=int(sr or 250)
    jobs += [(mp, sr, s0+i, s) for i in range(ns) for s in 'AB']
run((jobs[0][0], 250, 1, 'A'))
rows=[]
with ThreadPoolExecutor(int(os.environ.get('QP_J','4'))) as ex:
    for mname, SEED, name, side, rp, cpu in ex.map(run, jobs):
        try: g=RS.simulate(rp)
        except Exception as e: print('ERR', name, e); continue
        for who,T in (('us',side),('b1','B' if side=='A' else 'A')):
            q=0 if g['team'][0]==T else 1
            rd=dict(g['rounds']); last=g['last_round']
            qd=next((d for d in g['deaths'] if d['id']==q),None)
            win=g['result'].get('winner')==T
            row={'map':mname,'name':name,'who':who,'cpu':cpu[T],'win':win,'end':g['result'].get('endReason'),'last':last,
                 'qdead':(qd['round'],qd['len'],qd['reason'],tuple(qd['head'])) if qd else None,
                 'q_seed': (qd is None or qd['round']>SEED),
                 'q_end': qd is None,
                 'qlen_end': rd[last][T]['ids'].get(q,0) if last in rd else None,
                 'max_end': rd[last][T]['max'] if last in rd else None,
                 'elim': (not win) and last<499 and (last in rd and rd[last][T]['n']==0 or 'lim' in str(g['result'].get('endReason'))),
                 'qsplits': sum(1 for s in g['splits'] if s['parent']==q)}
            # ROUND6: crowned-queen ram after r300 (L>=15, head-on), and runs of >=3 consecutive-round queen SPLIT 2 at L>=12
            row['ram']= bool(qd and qd['round']>300 and qd['len']>=15 and 'HeadToHead' in str(qd['reason']))
            qs=[s for s in g['splits'] if s['parent']==q and s['k']==2 and s['L']>=12]
            runs=[];cur=[]
            for s in qs:
                if cur and s['round']==cur[-1]['round']+1: cur.append(s)
                else:
                    if len(cur)>=3: runs.append(cur)
                    cur=[s]
            if len(cur)>=3: runs.append(cur)
            row['shedruns']=len(runs); row['shedsegs']=sum(2*len(r) for r in runs)
            row['shedinfo']=[(r[0]['round'],r[0]['L'],len(r)) for r in runs]
            for r in (100,300):
                row[f'tot{r}']=rd[r][T]['total'] if r in rd else 0
            for r in (30,50,100,300,400,500):
                rr=min(r,last)
                row[f'ql{r}']=rd[rr][T]['ids'].get(q,0) if rr in rd else 0
                row[f'n{r}']=rd[rr][T]['n'] if rr in rd else 0
                row[f't{r}']=rd[rr][T]['total'] if rr in rd else 0
            qsp=[s for s in g['splits'] if s['parent']==q]
            row['qs1']=qsp[0]['round'] if qsp else None
            row['qs1L']=qsp[0]['L'] if qsp else None
            row['qdr']=qd['round'] if qd else 999
            if os.environ.get('QP_LOGS') and who=='us':
                import replay_decode as RD
                from collections import Counter
                ev=[str(e.get('text') or e.get('message') or e) for e in RD.load(rp)['events'] if e['t']=='dragonLog']
                row['r2n']=dict(Counter(t.split('r2 ')[1].split()[0] for t in ev if 'r2 ' in t and (' id%d '%q) in t))
                print('   r2', name, row['r2n'])
            rows.append(row)
json.dump(rows,open(f'{S}/mech/{tag}.json','w'),default=str)
def mean(xs):
    xs=[x for x in xs if x is not None]; return round(st.mean(xs),1) if xs else None
print('map who n | qAliveSeed qAliveEnd qLenEnd | tot100 tot300 | maxEnd | elim | wins | qsplits | rams shedRuns shedSegs | cpu')
for m in dict.fromkeys(r['map'] for r in rows):
    for who in ('us','b1'):
        R=[r for r in rows if r['who']==who and r['map']==m]
        print(f"{m:16s} {who} {len(R)} | {sum(r['q_seed'] for r in R)} {sum(r['q_end'] for r in R)} {mean([r['qlen_end'] for r in R])} | {mean([r['tot100'] for r in R])} {mean([r['tot300'] for r in R])} | {mean([r['max_end'] for r in R])} | {sum(r['elim'] for r in R)} | {sum(r['win'] for r in R)} | {mean([r['qsplits'] for r in R])} | {sum(r['ram'] for r in R)} {sum(r['shedruns'] for r in R)} {sum(r['shedsegs'] for r in R)} | {max([r['cpu'] or 0 for r in R])}")
    if os.environ.get('QP_V'):
        for r in rows:
            if r['map']==m and r['who']=='us': print('   ',r['name'],'W' if r['win'] else 'L',r['end'],r['last'],'qdead',r['qdead'],'qlenE',r['qlen_end'],'maxE',r['max_end'],'t100',r['tot100'],'t300',r['tot300'],'ram',r['ram'],'shed',r['shedinfo'])

print('EXTRA map who n | qL300 qL400 qL500 | qAlive300 | t100 t300 t500 | qs1 qs1L | n30 n50 t50 t100 | qdead<100 | elim')
for m in dict.fromkeys(r['map'] for r in rows):
    for who in ('us','b1'):
        R=[r for r in rows if r['who']==who and r['map']==m]
        print(f"{m:16s} {who} {len(R)} | {mean([r['ql300'] for r in R])} {mean([r['ql400'] for r in R])} {mean([r['ql500'] for r in R])} | {sum(r['qdr']>300 for r in R)} | {mean([r['t100'] for r in R])} {mean([r['t300'] for r in R])} {mean([r['t500'] for r in R])} | {mean([r['qs1'] for r in R])} {mean([r['qs1L'] for r in R])} | {mean([r['n30'] for r in R])} {mean([r['n50'] for r in R])} {mean([r['t50'] for r in R])} {mean([r['t100'] for r in R])} | {sum(r['qdr']<100 for r in R)} | {sum(r['elim'] for r in R)}")
