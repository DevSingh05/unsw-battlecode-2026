# Ram risk per zone for own dragons L>=12: dragon-rounds in bin vs rammed deaths in bin (own frame). top|ours
import sys
from common import *
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
BX,BY=9,9
def bins(p): return (p[0]//BX,p[1]//BY)
occ=defaultdict(Counter); ram=defaultdict(Counter); trap=defaultdict(Counter)
def run(path,T,l):
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); actor=None
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            for i in alive:
                if team[i]==T and len(body[i])>=12: occ[l][bins(A(body[i][0],T))]+=1
        elif t=='turnStart': actor=e['id']
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath':
            i=e['id']
            if team[i]==T and len(body[i])>=12:
                if e['reason']=='HitHeadToHead' and actor is not None and team.get(actor)!=T: ram[l][bins(A(body[i][0],T))]+=1
                elif e['reason'] in ('HitSelf','NoValidAction','HitWall','HitOtherBody'): trap[l][bins(A(body[i][0],T))]+=1
            alive.discard(i)
if mode=='top':
    for p,gid,win,a,b in top_games(): run(p,win,'winner'); run(p,'B' if win=='A' else 'A','loser')
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        run('replays/%s/%d.replay'%(d,gid),side,'us')
for l in occ:
    tot=sum(occ[l].values())
    print('==',l,'L>=12 dragon-rounds',tot,' cells: share%% / rams / other-deaths per 1000 dragon-rounds')
    for by in range(3):
        print('  y%2d-%2d '%(by*BY,by*BY+BY-1)+' | '.join('%4.1f%% %4.1f %4.1f'%(100*occ[l][(bx,by)]/tot, 1000*ram[l][(bx,by)]/max(1,occ[l][(bx,by)]), 1000*trap[l][(bx,by)]/max(1,occ[l][(bx,by)])) for bx in range(7)))
print('x bins of 9: 0-8 | 9-17 | 18-26 | 27-35 | 36-44 | 45-53 | 54-62')
