import sys,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
path,T=sys.argv[1],sys.argv[2]
mir = (T=='B')  # mirror B coords into A frame
o=R.load(path); m=Map(o['map'])
body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
alive=set(body)
rnd=0;actor=None
kpos=defaultdict(Counter); keat=Counter(); ksrc=Counter()
corpse={}
def M(p): return (47-p[0],23-p[1]) if mir else tuple(p)
kinglog=[]
kid=None
for e in o['events']:
    t=e['t']
    if t=='roundStart':
        rnd=e['round']
        ds=[i for i in alive if team[i]==T]
        if ds:
            kid=max(ds,key=lambda i:(len(body[i]),-i))
            h=M(body[kid][0])
            kpos[rnd//50*50][(h[0]//4*4,h[1]//4*4)]+=1
            if rnd%25==0: kinglog.append((rnd,kid,len(body[kid]),h))
    elif t=='turnStart': actor=e['id']
    elif t=='dragonUpdate':
        b=body[e['id']]; b.insert(0,e['head'])
        while b and b[-1]!=e['tail']: b.pop()
    elif t=='dragonSplit':
        p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
    elif t=='dragonDeath':
        i=e['id']
        for s in body[i][::2]: corpse[tuple(s)]=(team[i],len(body[i]))
        alive.discard(i)
    elif t=='tileChange' and not e['hasPearl']:
        src=corpse.pop(tuple(e['tile']),None)
        if actor==kid:
            ksrc['corpse_own' if src and src[0]==T else 'corpse_enemy' if src else 'spawn']+=1
print('king log (A-frame coords):',kinglog)
print('king eat sources',dict(ksrc))
for r in sorted(kpos): print(r,kpos[r].most_common(4))
