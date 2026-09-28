# Trace the last N rounds of a dying dragon: head path, length, pearls nearby. usage: trap.py dir gid round len [N]
import os,sys
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
import replay_decode as R
from replay_sim import Map
d,gid,RD,L=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]); N=int(sys.argv[5]) if len(sys.argv)>5 else 12
o=R.load(d if d.endswith('.replay') else 'replays/%s/%d.replay'%(d,gid)); m=Map(o['map'])
body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
alive=set(body); rnd=0; hist={}; actor=None; acts={}
target=None
for e in o['events']:
    t=e['t']
    if t=='roundStart':
        rnd=e['round']
        for i in alive: hist.setdefault(i,[]).append((rnd,tuple(body[i][0]),len(body[i]),tuple(body[i][-1])))
    elif t=='turnStart': actor=e['id']
    elif t=='dragonAction': acts.setdefault(e['id'],[]).append((rnd,e['action']))
    elif t=='dragonUpdate':
        b=body[e['id']]; b.insert(0,e['head'])
        while b and b[-1]!=e['tail']: b.pop()
    elif t=='dragonSplit':
        p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
    elif t=='dragonDeath':
        i=e['id']
        if rnd==RD and len(body[i])==L:
            target=i; fin=list(body[i]); break
        alive.discard(i)
print('dragon',target,'team',team[target],'body at death',fin[:L])
for r,h,l,tl in hist[target][-N:]: print(r,h,l,'tail',tl)
print([a for a in acts.get(target,[]) if a[0]>=RD-N])
# ascii of area around head
hx,hy=fin[0]; occ={}
for j in alive:
    for k,s in enumerate(body[j]): occ[tuple(s)]=('H' if k==0 else ('s' if j==target else ('a' if team[j]==team[target] else 'e')))
for y in range(max(0,hy-6),min(m.h,hy+7)):
    print('%2d '%y+''.join(occ.get((x,y),'.') for x in range(max(0,hx-12),min(m.w,hx+13))), ' x from',max(0,hx-12))
