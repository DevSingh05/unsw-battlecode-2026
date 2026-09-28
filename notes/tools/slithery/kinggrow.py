# King (current longest) eats per 50-round window + source; big-dragon (>=10) deaths per window; units. top|ours
import sys
from common import *
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
WIN=[200,250,300,350,400,450,500]
def track(path, T):
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); actor=None; kid=None; corpse={}
    ke=Counter(); ks=Counter(); bd=Counter(); lens={}; rnd=0; mx={}
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            rnd=e['round']
            ds=[i for i in alive if team[i]==T]
            kid=max(ds,key=lambda i:len(body[i])) if ds else None
            if rnd%50==0 and kid is not None: mx[rnd]=len(body[kid])
        elif t=='turnStart': actor=e['id']
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath':
            i=e['id']
            for s in body[i][::2]: corpse[tuple(s)]=team[i]
            if team[i]==T and len(body[i])>=10: bd[rnd//50*50]+=1
            alive.discard(i)
        elif t=='tileChange' and not e['hasPearl']:
            src=corpse.pop(tuple(e['tile']),None)
            if actor==kid and kid is not None:
                ke[rnd//50*50]+=1; ks['own' if src==T else 'enemy' if src else 'spawn']+=1
    return ke,ks,bd,mx
A_=defaultdict(lambda: defaultdict(list))
def add(lab,res):
    ke,ks,bd,mx=res
    for w in WIN[:-1]:
        A_[lab]['keat%d'%w].append(ke[w]); A_[lab]['bigdeath%d'%w].append(bd[w])
    for w in WIN: A_[lab]['max%d'%w].append(mx.get(w,mx.get(499,0)) if w<500 else max(mx.values()) if False else mx.get(w, None) or 0)
    for k,v in ks.items(): A_[lab]['src_'+k].append(v)
if mode=='top':
    for p,gid,win,a,b in top_games():
        add('winner',track(p,win)); add('loser',track(p,'B' if win=='A' else 'A'))
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        o='B' if side=='A' else 'A'
        p='replays/%s/%d.replay'%(d,gid)
        add('us_'+('W' if win else 'L'),track(p,side)); add('them_'+('L' if win else 'W'),track(p,o))
import statistics
labs=list(A_)
keys=sorted(A_[labs[0]].keys(), key=lambda k:(k.rstrip('0123456789'),int(k[len(k.rstrip('0123456789')):] or 0)))
print('%-14s'%''+''.join('%10s'%l for l in labs))
for k in keys: print('%-14s'%k+''.join('%10.1f'%statistics.mean(A_[l][k] or [0]) for l in labs))
