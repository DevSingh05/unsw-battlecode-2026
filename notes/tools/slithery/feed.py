# Feeding: small (<=6) own deaths within dist<=4 of the team's longest (>=8) from r200, per 50-round window;
# pearls dropped by them and share eaten by the longest (any time) / by anyone else of team / by enemy / never.
import sys
from common import *
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
def track(path,T):
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); actor=None; kid=None; drop={}; nfeed=Counter(); fate=Counter(); unitsw={}
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            rnd=e['round']; ds=[i for i in alive if team[i]==T]
            kid=max(ds,key=lambda i:len(body[i])) if ds else None
            if rnd%50==0: unitsw[rnd]=len(ds)
        elif t=='turnStart': actor=e['id']
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath':
            i=e['id']; alive.discard(i)
            if team[i]==T and rnd>=200 and len(body[i])<=6 and kid is not None and kid!=i and len(body[kid])>=8 and m.dist(body[i][0],body[kid][0])<=4:
                nfeed[rnd//50*50]+=1
                for s in body[i][::2]: drop[tuple(s)]=rnd
        elif t=='tileChange' and not e['hasPearl']:
            tl=tuple(e['tile'])
            if tl in drop:
                drop.pop(tl)
                fate['king' if actor==kid else ('ally' if team.get(actor)==T else 'enemy')]+=1
    fate['never']+=len(drop)
    return nfeed,fate,unitsw
agg=defaultdict(lambda: defaultdict(list))
def add(l,r):
    nf,fa,u=r
    for w in range(200,500,50): agg[l]['feeders%d'%w].append(nf[w])
    for w in range(250,500,50): agg[l]['units%d'%w].append(u.get(w,0))
    tot=sum(fa.values()) or 1
    for k in ['king','ally','enemy','never']: agg[l]['fate_'+k].append(fa[k]/tot)
    agg[l]['dropped'].append(tot)
if mode=='top':
    for p,gid,win,a,b in top_games():
        add('winner',track(p,win)); add('loser',track(p,'B' if win=='A' else 'A'))
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        o='B' if side=='A' else 'A'; p='replays/%s/%d.replay'%(d,gid)
        add('us_'+('W' if win else 'L'),track(p,side)); add('them_'+('L' if win else 'W'),track(p,o))
import statistics
labs=list(agg)
print('%-14s'%''+''.join('%10s'%l for l in labs))
for k in agg[labs[0]]: print('%-14s'%k+''.join('%10.2f'%statistics.mean(agg[l][k]) for l in labs))
