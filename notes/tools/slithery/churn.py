# Where/what are small deaths r150-399: by zone (own frame), length, age; top winners vs us
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
Z=defaultdict(Counter); Ln=defaultdict(Counter); Ag=defaultdict(Counter); K=defaultdict(Counter); n=Counter()
def zone2(p):
    z=zone(p)
    if z in('none','rare','g100O','g100E'):
        x,y=p
        return 'open_'+('O' if x<31 else 'E')
    return z
def add(l,G,T):
    n[l]+=1
    for x in G['deaths']:
        if x['team']!=T or not(150<=x['round']<400) or x['len']>6: continue
        h=A(x['head'],T)
        Z[l][(x['reason'][:7],zone2(h))]+=1; Ln[l][x['len']]+=1
        Ag[l][min(x['age'],50)//5*5]+=1
        kd=x.get('king',(0,0,99,99))
        K[l]['kingdist<=4' if kd[1]>=8 and kd[2]<=4 else 'far']+=1
if mode=='top':
    for p,gid,win,a,b in top_games(): add('winner',simulate(p),win)
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        add('us',simulate('replays/%s/%d.replay'%(d,gid)),side)
for l in Z:
    print('==',l,n[l],'games; small(<=6) deaths r150-399 per game')
    for k,v in Z[l].most_common(22): print('   %-30s %6.1f'%(k,v/n[l]))
    print('  len',{k:round(v/n[l],1) for k,v in sorted(Ln[l].items())})
    print('  age',{k:round(v/n[l],1) for k,v in sorted(Ag[l].items())})
    print('  king',{k:round(v/n[l],1) for k,v in K[l].items()})
