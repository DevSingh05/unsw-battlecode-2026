# Where does each team's longest dragon (>=10) live from r300 (own frame)? 9x9 bins -> fraction. Also enemy-head distance.
import sys
from common import *
import replay_decode as R
from replay_sim import Map
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
def kingtrack(path, teams, R0=300):
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); res={T:Counter() for T in teams}; ed={T:[] for T in teams}
    for e in o['events']:
        t=e['t']
        if t=='roundStart':
            rnd=e['round']
            if rnd>=R0:
                for T in teams:
                    ds=[i for i in alive if team[i]==T]
                    if not ds: continue
                    k=max(ds,key=lambda i:len(body[i]))
                    if len(body[k])<10: continue
                    h=A(body[k][0],T); res[T][(h[0]//9,h[1]//9)]+=1
                    en=[m.dist(body[k][0],body[j][0]) for j in alive if team[j]!=T]
                    if en: ed[T].append(min(en))
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath': alive.discard(e['id'])
    return res,ed
agg=defaultdict(Counter); eds=defaultdict(list)
if mode=='top':
    for p,gid,win,a,b in top_games():
        r,e=kingtrack(p,[win,'B' if win=='A' else 'A'])
        agg['winner'].update(r[win]); agg['loser'].update(r['B' if win=='A' else 'A']); eds['winner']+=e[win]; eds['loser']+=e['B' if win=='A' else 'A']
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        o='B' if side=='A' else 'A'
        r,e=kingtrack('replays/%s/%d.replay'%(d,gid),[side,o])
        agg['us'].update(r[side]); agg['them'].update(r[o]); eds['us']+=e[side]; eds['them']+=e[o]
for lab,c in agg.items():
    tot=sum(c.values()); print('==',lab,'king-rounds',tot)
    for by in range(3):
        print('  y%2d-%2d '%(by*9,by*9+8)+' '.join('%5.2f'%(c[(bx,by)]/tot) for bx in range(7)))
    import statistics
    E=eds[lab]; print('  enemy-head dist: median',statistics.median(E),'frac<=3 %.3f'%(sum(1 for x in E if x<=3)/len(E)),'frac<=5 %.3f'%(sum(1 for x in E if x<=5)/len(E)))
print('x bins: 0-8 9-17 18-26 27-35 36-44 45-53 54-62')
