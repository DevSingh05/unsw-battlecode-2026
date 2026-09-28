import sys,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
import replay_decode as R
from replay_sim import Map
path,r0,r1,x0,x1,y0,y1=sys.argv[1],*map(int,sys.argv[2:8])
o=R.load(path); m=Map(o['map'])
body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
rnd=0;actor=None
def inb(p): return x0<=p[0]<=x1 and y0<=p[1]<=y1
for e in o['events']:
    t=e['t']
    if t=='roundStart': rnd=e['round']
    elif t=='turnStart': actor=e['id']
    elif t=='dragonUpdate':
        b=body[e['id']]; b.insert(0,e['head'])
        while b and b[-1]!=e['tail']: b.pop()
    elif t=='dragonSplit':
        p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team']
        if r0<=rnd<=r1 and (inb(body[p][0]) or inb(body[c][0])): print(rnd,'SPLIT',p,'->',body[p],'child',c,body[c])
    if r0<=rnd<=r1:
        if t=='dragonAction':
            i=e['id']
            if inb(body[i][0]): print(rnd,'ACT',i,team[i],'len',len(body[i]),'head',body[i][0],'body',body[i][:8],e['action'])
        elif t=='dragonDeath':
            i=e['id']
            if inb(body[i][0]): print(rnd,'DEATH',i,team[i],len(body[i]),e['reason'],body[i])
        elif t=='tileChange' and inb(tuple(e['tile'])) :
            print(rnd,'TILE',e['tile'],'pearl' if e['hasPearl'] else 'eaten/cleared by',actor)
    if rnd>r1: break
