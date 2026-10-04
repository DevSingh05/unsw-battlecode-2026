# for r500 queen-dead losses: how often was their (alive) queen within view (cheb<=3) of one of our heads, after our queen died
import sys,json,pickle,collections
sys.path.insert(0,'notes/tools'); import replay_sim as RS, replay_decode as RD
L2=sys.argv[1]
R=json.load(open(f'{L2}/rows.json'))
S=[r for r in R if r['s']==0 and r['cause'].startswith('r500_queen_dead')]
out=[]
for r in S:
    o=RD.load(f"replays/loss_audit2/{r['id']}.replay"); m=RS.Map(o['map'])
    body={};team={};alive=set()
    for i,(t,pts) in enumerate(m.dragons): body[i]=list(pts); team[i]='AB'[t]; alive.add(i)
    us=r['side']; tq=0 if team[0]!=us else 1
    qdr=r['qd']['round']; rnd=0; seen=0; adj=0; rounds=0; last=-1; mind=99
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            rnd=e['round']
            if rnd>qdr and tq in alive:
                rounds+=1; hx,hy=body[tq][0]; best=99
                for j in alive:
                    if team[j]==us:
                        x,y=body[j][0]; dx=min(abs(x-hx),m.w-abs(x-hx)); dy=min(abs(y-hy),m.h-abs(y-hy))
                        best=min(best,max(dx,dy))
                if best<=3: seen+=1
                if best<=1: adj+=1
                mind=min(mind,best)
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            body[e['parent']]=list(e['parentBody']); body[e['child']]=list(e['childBody']); team[e['child']]=e['team']; alive.add(e['child'])
        elif t=='dragonDeath': alive.discard(e['id'])
    out.append((r['map'],r['top10'],r['tqd']['len'],rounds,seen,adj,r['us_final']['total'],r['th_final']['total']))
    print(f"{r['map'][:10]:10s} top10={int(r['top10'])} tqL{r['tqd']['len']:3d} rounds_after_ourQ {rounds:3d} theirQ_in_view {seen:3d} adj {adj:3d} total {r['us_final']['total']}v{r['th_final']['total']}",flush=True)
small=[x for x in out if x[2]<=6]
print('their queen <=6:',len(small),'seen>=10 rounds:',sum(1 for x in small if x[4]>=10),'never seen:',sum(1 for x in small if x[4]==0))
big=[x for x in out if x[2]>6]
print('their queen >6:',len(big),'seen>=10 rounds:',sum(1 for x in big if x[4]>=10),'never seen:',sum(1 for x in big if x[4]==0))
