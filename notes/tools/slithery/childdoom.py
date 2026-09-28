# For trapped deaths of big split-children (L>=12, age<len): doomed at birth (perfect-info DFS over the first
# move options)? Also: doomed by the parent's U-turn vs lost later.
import sys
from common import *
import replay_decode as R
from replay_sim import Map, simulate
from dfslib import dfs
from collections import Counter
sel=sys.argv[1:]; C=Counter()
for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
    if sel and d not in sel: continue
    path='replays/%s/%d.replay'%(d,gid); G=simulate(path)
    born={s['child']:s for s in G['splits'] if s['team']==side and s['k']>=8}
    targ={}
    for x in G['deaths']:
        if x['team']!=side or x['len']<12 or x['id'] not in born or x['age']>=x['len']: continue
        nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
        if free==0: targ[x['id']]=x
    if not targ: continue
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); rnd=0; checked=set()
    for e in o['events']:
        t=e['t']
        if t=='roundStart': rnd=e['round']
        elif t=='turnStart':
            i=e['id']
            if i in targ and i not in checked:
                checked.add(i); b=body[i]; L=len(b); dep=min(L+2,40)
                bl={}
                for j in alive:
                    if j==i: continue
                    for k,p in enumerate(body[j]): bl[p]=max(bl.get(p,0),len(body[j])-k)
                best=max(dfs(m,b,m.step(b[0],dd),dep,bl) for dd in 'NESW')
                c='doomed_at_birth' if best<dep else 'escapable_at_birth'
                C[c]+=1
                print(d,gid,'child',i,'born r%d L%d'%(born[i]['round'],L),'died r%d'%targ[i]['round'],c,'best',best,'/',dep)
        elif t=='dragonUpdate':
            bb=body[e['id']]; bb.insert(0,e['head'])
            while bb and bb[-1]!=e['tail']: bb.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath': alive.discard(e['id'])
print(C)
