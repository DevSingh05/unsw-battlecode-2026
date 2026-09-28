# Opening: for each starting dragon (by start slot), rounds of its first split, head at r5/15/30/50, length; team units/max at r25/50/100.
import sys
from common import *
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
SLOT={0:'L7@(8,10)',2:'L4@(18,7)',4:'L25@(3,22)',6:'L2@(15,13)',8:'L5@(33,2)',10:'L2@(26,23)',12:'L2@(20,4)'}
def op(path,T):
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); rnd=0; firstsplit={}; pos=defaultdict(dict); death={}
    out=[]
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            rnd=e['round']
            if rnd>60: break
            for i in list(body)[:14]:
                if i in alive and team[i]==T and rnd in(5,15,30,50): pos[i][rnd]=(A(body[i][0],T),len(body[i]))
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
            if p<14 and p not in firstsplit: firstsplit[p]=(rnd,len(e['parentBody']),len(e['childBody']))
        elif t=='dragonDeath':
            if e['id']<14 and e['id'] not in death: death[e['id']]=rnd
            alive.discard(e['id'])
    for i in range(14):
        if team[i]!=T: continue
        slot=i - (1 if T=='B' else 0)
        out.append('   %-12s split %-14s died %-5s %s'%(SLOT.get(slot,'?'),firstsplit.get(i,'-'),death.get(i,'-'),' '.join('r%d%s L%d'%(r,p,l) for r,(p,l) in sorted(pos[i].items()))))
    return out
mode=sys.argv[1]
if mode=='top':
    for p,gid,win,a,b in top_games():
        name=a if win=='A' else b
        print('== top',gid,'winner',name,'side',win); print('\n'.join(op(p,win)))
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if d not in sys.argv[2:]: continue
        print('== ours',gid,opp,'WIN' if win else 'LOSS'); print('\n'.join(op('replays/%s/%d.replay'%(d,gid),side)))
