# Own hot-pocket eats per 100-round window, per pocket, winners vs us
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
agg=defaultdict(Counter); n=Counter()
def add(l,G,T):
    n[l]+=1
    for e in G['eats']:
        if e['team']==T and not e['corpse']:
            z=zone(A(e['tile'],T))
            if z.startswith('hot') and z!='hotEnemy': agg[l][(z,e['round']//100*100)]+=1
            if z in('comb5O',): agg[l][('comb5O',e['round']//100*100)]+=1
if mode=='top':
    for p,gid,win,a,b in top_games(): add('winner',simulate(p),win)
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        G=simulate('replays/%s/%d.replay'%(d,gid)); add('us',G,side); add('them',G,'B' if side=='A' else 'A')
for l in agg:
    print('==',l,n[l])
    zs=sorted({k[0] for k in agg[l]})
    print('%-8s'%''+''.join('%8s'%z[-6:] for z in zs))
    for w in range(0,500,100): print('%-8d'%w+''.join('%8.1f'%(agg[l][(z,w)]/n[l]) for z in zs))
