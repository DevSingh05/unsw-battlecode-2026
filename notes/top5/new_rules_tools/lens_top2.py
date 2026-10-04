"""Unit length distribution at r100/150/200/250/300 (us vs OPP), and how many units sit idle (no eat in last 20 rounds)."""
import sys,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top2.pkl','rb'))
US=('v55','v60'); OPP=sys.argv[1]
A=collections.defaultdict(list)
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in US]; o=[r for r in rs if r['team']==OPP]
    if not u or not o: continue
    if OPP=='VIB' and u[0]['at']>='2026-10-03T17:08:30': continue
    u=u[0]; g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]; E='B' if T=='A' else 'A'
    lastEat={}
    ev=sorted(g['eats'],key=lambda e:e['round'])
    for k in (100,150,200,250,300):
        if k not in rd: continue
        le={}
        for e in ev:
            if e['round']>k: break
            le[e['id']]=e['round']
        for t,s in ((T,'us'),(E,OPP)):
            ls=rd[k][t]['lens']; ids=rd[k][t]['ids']
            A[(s,k,'n')].append(len(ls)); A[(s,k,'L2-3')].append(sum(1 for x in ls if x<=3)); A[(s,k,'L4-7')].append(sum(1 for x in ls if 4<=x<=7)); A[(s,k,'L8+')].append(sum(1 for x in ls if x>=8))
            A[(s,k,'top3')].append(sum(ls[:3]))
            A[(s,k,'idle20')].append(sum(1 for j in ids if k-le.get(j,-999)>20))
for s in ('us',OPP):
    for k in (100,150,200,250,300):
        print(s,k,' '.join(f"{c}={round(st.mean(A[(s,k,c)]),1)}" for c in ('n','L2-3','L4-7','L8+','top3','idle20') if A[(s,k,c)]))
