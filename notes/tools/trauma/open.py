import sys,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
import replay_decode as R
from replay_sim import Map
path,T,R1=sys.argv[1],sys.argv[2],int(sys.argv[3])
mir=T=='B'
M=lambda p:(47-p[0],23-p[1]) if mir else tuple(p)
o=R.load(path); m=Map(o['map'])
body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
rnd=0; log={}
for e in o['events']:
    t=e['t']
    if t=='roundStart':
        rnd=e['round']
        if rnd>R1: break
    elif t=='dragonUpdate':
        b=body[e['id']]; b.insert(0,e['head'])
        while b and b[-1]!=e['tail']: b.pop()
        if team[e['id']]==T: log.setdefault(e['id'],[]).append((rnd,M(b[0]),len(b)))
    elif t=='dragonSplit':
        p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team']
        if team[c]==T: print('r',rnd,'split',p,len(body[p]),'child',c,len(body[c]),'at',M(body[p][0]),M(body[c][0]))
    elif t=='dragonDeath' and team[e['id']]==T: print('r',rnd,'death',e['id'],len(body[e['id']]),e['reason'],M(body[e['id']][0]))
for i,l in sorted(log.items()):
    s=' '.join('%d:%d,%d/%d'%(r,p[0],p[1],L) for r,p,L in l[::3])
    print(i,s[:900])
