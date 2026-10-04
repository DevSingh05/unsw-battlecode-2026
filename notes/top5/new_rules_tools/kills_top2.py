"""Kill moves by (killer length class, steps, paid, ate on path) and victim length; for VIB/FTM/SSS and us (v55/v60) in their mutual games."""
import sys,pickle,collections,math
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top2.pkl','rb'))
C=collections.defaultdict(collections.Counter); N=collections.Counter()
for gid,rs in D.items():
    if len(rs)!=2: continue
    labs={r['team'] for r in rs}
    if not labs & {'v55','v60'} or not labs & {'VIB','FTM','SSS'}: continue
    if 'VIB' in labs and rs[0]['at']>='2026-10-03T17:08:30': continue
    g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    nm={}
    for r in rs:
        T=[t for t in 'AB' if rd[last][t]['total']==r['tot_end'] and rd[last][t]['n']==r['units_end']]
        if len(T)==1: nm[T[0]]=('us' if r['team'] in ('v55','v60') else r['team'])
    if len(nm)!=2: continue
    for t in nm.values(): N[t]+=1
    for a in g['moves']:
        if 'move' not in a['act']: continue
        who=nm[a['team']]; L=a['len_before']; F=math.ceil(L/4); paid=max(0,a['steps']-F)
        kills=[k for k in a['killed'] if k[1]!=a['team']]
        lc='L2' if L==2 else 'L3' if L==3 else 'L4-6' if L<=6 else 'L7+'
        if a['steps']>=3: C[who]['moves3+_'+lc]+=1
        if paid>0 and not kills: C[who]['paid_nokill_'+('eat' if a['ate'] else 'noeat')]+=1
        for k in kills:
            C[who][f"kill_{lc}_s{min(a['steps'],4)}{'_ate' if a['ate'] else ''}"]+=1
            C[who]['kill_n']+=1
            if a['steps']>=3: C[who]['kill3+_victimL%s'%('2-3' if k[2]<=3 else '4-9' if k[2]<10 else '10+')]+=1
for t,c in C.items():
    n=N[t]; print(t,'games',n,'kills/game',round(c['kill_n']/n,1))
    print('  ',{k:round(v/n,2) for k,v in sorted(c.items()) if k!='kill_n'})
