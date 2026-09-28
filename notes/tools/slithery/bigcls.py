# Classify L>=12 deaths (per game) for top winners/losers and us/them.
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
C=defaultdict(Counter); n=Counter(); locs=defaultdict(list)
BOX={(57,13),(58,13),(57,14),(58,14),(4,12),(5,12),(4,13),(5,13)}
def cls(x,T):
    nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
    kl=x.get('king',(0,0,99))
    if x['reason']=='HitHeadToHead':
        if (x.get('killer_team') and x['killer_team']!=T): return 'rammed'
        if x.get('victim_team') and x['victim_team']!=T: return 'rammer'
        return 'h2h_ally'
    if A(x['head'],T) in BOX: return 'portalbox'
    if free==0: return 'trapped' + ('_king' if kl[1]<x['len'] else '')
    if kl[1]>x['len'] and kl[2]<=4: return 'merge'
    return x['reason']+'_exit'
def add(l,G,T):
    n[l]+=1
    for x in G['deaths']:
        if x['team']==T and x['len']>=12:
            c=cls(x,T); C[l][c]+=1
            if c in('rammed','trapped_king'): locs[l+'_'+c].append((x['round'],x['len'],A(x['head'],T)))
if mode=='top':
    for p,gid,win,a,b in top_games():
        G=simulate(p); add('winner',G,win); add('loser',G,'B' if win=='A' else 'A')
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        G=simulate('replays/%s/%d.replay'%(d,gid)); add('us',G,side); add('them',G,'B' if side=='A' else 'A')
for l in C: print(l,n[l],{k:round(v/n[l],2) for k,v in C[l].most_common()})
for k,v in locs.items(): print(k,sorted(v))
