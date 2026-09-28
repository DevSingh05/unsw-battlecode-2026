# Deliberate suicides (death with >=1 free/pearl neighbour, reason HitSelf/NoValidAction) per 25-round window, with dist to team longest
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
S=defaultdict(Counter); D=defaultdict(Counter); n=Counter(); U=defaultdict(Counter)
def add(l,G,T):
    n[l]+=1
    for x in G['deaths']:
        if x['team']!=T or x['round']<150: continue
        nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
        if x['reason'] in('HitSelf','NoValidAction') and free>=1:
            w=x['round']//25*25; S[l][w]+=1
            kd=x.get('king',(0,0,99))[2]
            D[l]['d<=4' if kd<=4 else 'd5-10' if kd<=10 else 'd>10']+=1
    for r,s in G['rounds']:
        if r%25==0 and r>=150: U[l][r]+=s[T]['n']
if mode=='top':
    for p,gid,win,a,b in top_games(): add('winner',simulate(p),win)
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        add('us',simulate('replays/%s/%d.replay'%(d,gid)),side)
for l in S:
    print('==',l,'deliberate suicides per 25 rounds (units at window start)')
    print('  '+' '.join('%d:%.1f(%d)'%(w,S[l][w]/n[l],U[l][w]/n[l]) for w in range(150,500,25)))
    print('  dist to longest',{k:round(v/n[l],1) for k,v in D[l].items()})
