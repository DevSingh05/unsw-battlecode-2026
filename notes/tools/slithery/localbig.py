# big-death classes for candidate vs opponent over an arena replay dir
import sys,glob,os
from common import *
from replay_sim import simulate
from collections import Counter
d=sys.argv[1]; key=sys.argv[2] if len(sys.argv)>2 else 'proto'
C={'cand':Counter(),'opp':Counter()}; n=0
for p in sorted(glob.glob(d+'/*.replay')):
    b=os.path.basename(p); first=b.split('_vs_')[0]
    T='A' if key in first else 'B'; o='B' if T=='A' else 'A'
    G=simulate(p); n+=1
    bigborn={s['child'] for s in G['splits'] if s['k']>=8}
    for x in G['deaths']:
        if x['len']<12: continue
        lab='cand' if x['team']==T else 'opp'
        nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
        c='rammed' if x['reason']=='HitHeadToHead' and x.get('killer_team') not in (None,x['team']) else ('trapped' if free==0 else 'exit')
        if c=='trapped': c+=('_splitchild' if x['id'] in bigborn and x['age']<x['len'] else '_normal')
        C[lab][c]+=1
print(d.split('/')[-1],n,{k:dict(v) for k,v in C.items()})
