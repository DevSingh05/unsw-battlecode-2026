# Where do our big dragons (L>=12) reverse-split (k>=L-2, i.e. trapped U-turn)? own-frame head tile. ours|top|dir
import sys,glob,os
from common import *
from replay_sim import simulate
from collections import Counter
mode=sys.argv[1]; sel=sys.argv[2:]
C=Counter(); Z=Counter(); n=0; rows=[]
def add(G,T,tag):
    global n; n+=1
    for s in G['splits']:
        if s['team']==T and s['L']>=12 and s['k']>=s['L']-2:
            # parent head at split = parentBody[0] (parent keeps head part)
            rows.append((tag,s['round'],s['L'],s['exits']))
            C[tag]+=1
if mode=='ours':
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        G=simulate('replays/%s/%d.replay'%(d,gid)); add(G,side,'us')
elif mode=='top':
    for p,gid,win,a,b in top_games(): G=simulate(p); add(G,win,'winner'); add(G,'B' if win=='A' else 'A','loser')
print({k:round(v/ (n/ (2 if mode=='top' else 1)),2) for k,v in C.items()}, 'per game')
