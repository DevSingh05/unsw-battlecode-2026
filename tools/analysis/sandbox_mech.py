#!/usr/bin/env python3
"""qp11.py <tag> <botdir|BASE> <map[:nseeds],...> [seed0]: sandbox games vs variants/b3. botdir: both sides; BASE: b3 v b3,
one game per seed, both sides counted. Per side-game: L4+ share of unit-turns r100-300, fresh eats by L4+ r100-300,
t100/t200/t300, longest at end, units r100/r200, waste ledger (boxed, stillborn, self r100-399), bulk splits, elim, win."""
import sys, os, subprocess, json, re, statistics as st
from concurrent.futures import ThreadPoolExecutor
P='/Users/devsingh/Developer/UNSW_Battlecode'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r11'
sys.path.insert(0,P+'/notes/tools/midgame'); sys.path.insert(0,P+'/notes/tools'); import sim2
tag,bot,maps=sys.argv[1],sys.argv[2],sys.argv[3].split(','); s0=int(sys.argv[4]) if len(sys.argv)>4 else 4000
B3=P+'/variants/b3'; base=bot=='BASE'
out=f'{S}/mech/{tag}'; os.makedirs(out,exist_ok=True)
def run(j):
    mp,seed,side=j; mname=os.path.basename(mp).replace('.map','')
    rp=f'{out}/{mname}_{seed}_{side}.replay'
    a,b=(B3,B3) if base else ((bot,B3) if side=='A' else (B3,bot))
    if not os.path.exists(rp+'.cpu'):
        r=subprocess.run(['unswbc','run',mp,a,b,'--seed',str(seed),'--sandbox','-o',rp,'--no-logs'],cwd=P,capture_output=True,text=True)
        t=r.stdout+r.stderr
        json.dump({s_:(float(m.group(1)) if (m:=re.search(r'team %s points.*max ([0-9.]+)M'%s_,t)) else None) for s_ in 'AB'},open(rp+'.cpu','w'))
    return mname,seed,side,rp,json.load(open(rp+'.cpu'))
def stats(g,T):
    rd=dict(g['rounds']); last=max(rd); at=lambda k,f: rd[min(k,last)][T][f]
    r={'box':0,'sb':0,'self':0}
    for x in g['deaths']:
        if x['team']!=T or x['id']<=1 or x['reason']=='HitHeadToHead': continue
        if 100<=x['round']<400: r['self']+=x['len']
        nb=x.get('nbrs',{}); free=[d for d,v in nb.items() if v in ('free','pearl')]
        ally=[d for d,v in nb.items() if isinstance(v,tuple) and v[0]=='ally']
        kd=x['king'][2] if x.get('king') else 99
        if x['age']<=1: r['sb']+=x['len']
        elif kd<=3: pass
        elif not free and ally: r['box']+=x['len']
    ut=u4=0
    for k in range(100,301):
        if k in rd:
            for i,L in rd[k][T]['ids'].items(): ut+=1; u4+=L>=4
    fe=0
    for e in g['eats']:
        if e['team']==T and e['corpse'] is None and 100<=e['round']<=300:
            pr=rd.get(e['round']-1,{}).get(T,{}).get('ids',{})
            if pr.get(e['id'],0)>=4: fe+=1
    O='B' if T=='A' else 'A'
    fa=sum(1 for e in g['eats'] if e['team']==T and e['corpse'] is None and 100<=e['round']<=300)
    ce=sum(1 for e in g['eats'] if e['team']==T and e['corpse'] is not None and 100<=e['round']<=300)
    h2h=sum(x['len'] for x in g['deaths'] if x['team']==T and 100<=x['round']<400 and x['reason']=='HitHeadToHead')
    h5=sum(1 for x in g['deaths'] if x['team']==T and 100<=x['round']<400 and x['reason']=='HitHeadToHead' and x['len']>=5)
    r.update(fa=fa,ce=ce,h2h=h2h,h5=h5,o300=at2(300,O) if (at2:=lambda k,TT: rd[min(k,last)][TT]['total']) else 0)
    win=g['result'].get('winner')==T
    r.update(l4=100*u4/max(ut,1),fe4=fe,t100=at(100,'total'),t200=at(200,'total'),t300=at(300,'total'),max500=rd[last][T]['max'],
             n100=at(100,'n'),n200=at(200,'n'),bulk=sum(1 for s in g['splits'] if s['team']==T and s['k']>=s['L']-2 and s['L']>=5),
             elim=int((not win) and last<499 and rd[last][T]['n']==0),win=int(win))
    return r
jobs=[]
for m in maps:
    mp,_,n=m.partition(':'); n=int(n or 1)
    jobs+=[(mp,s0+i,s) for i in range(n) for s in (('A',) if base else ('A','B'))]
rows=[]
with ThreadPoolExecutor(int(os.environ.get('QP_J','4'))) as ex:
    for mname,seed,side,rp,cpu in ex.map(run,jobs):
        try: g=sim2.simulate(rp)
        except Exception as e: print('ERR',rp,e); continue
        for T in (('A','B') if base else (side,)):
            r=stats(g,T); r.update(map=mname,seed=seed,side=T,cpu=cpu.get(T)); rows.append(r)
json.dump(rows,open(f'{S}/mech/{tag}.json','w'))
print('done',tag,len(rows))
