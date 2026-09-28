# For each of our L>=12 self-trap deaths: in the K rounds before death, would a deep (L+2, cap 40) survival DFS
# have rejected the chosen move while an alternative passed? (others' segments free after (len-idx) moves; no eating)
import sys
from common import *
import replay_decode as R
from replay_sim import Map, simulate
sel=sys.argv[1:]
K=12
def dfs(m, body, first, depth, blocked_until):
    # body: list head-first. simulate moving; own tail frees each step.
    L=len(body)
    occ={p:i for i,p in enumerate(body)}  # index from head
    path=[first]; nodes=[0]
    def ok(p,t):
        if p is None: return False
        if p in own and own[p] > -1: pass
        return True
    # own body time: segment at index i frees after L-i moves
    ownfree={p:L-i for i,p in enumerate(body)}
    seen={}
    def rec(p,t,visited):
        nodes[0]+=1
        if nodes[0]>200000: return depth  # give up: assume ok
        if t>=depth: return t
        best=t
        for d in 'NESW':
            q=m.step(p,d)
            if q is None or q in visited: continue
            if ownfree.get(q,0)>t+1: continue  # still own body at time t+1
            if blocked_until.get(q,0)>t+1: continue
            visited.add(q)
            r=rec(q,t+1,visited)
            visited.discard(q)
            best=max(best,r)
            if best>=depth: return best
        return best
    if first is None or ownfree.get(first,0)>1 or blocked_until.get(first,0)>1: return 0
    return rec(first,1,{first})
def own_is_ok(): pass
sys.setrecursionlimit(10000)
for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
    if sel and d not in sel: continue
    path='replays/%s/%d.replay'%(d,gid)
    G=simulate(path)
    targets=[]
    for x in G['deaths']:
        if x['team']!=side or x['len']<12: continue
        nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
        if x['reason'] in('HitSelf','NoValidAction','HitWall','HitOtherBody') and free==0: targets.append((x['round'],x['id'],x['len']))
    if not targets: continue
    o=R.load(path); m=Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}
    alive=set(body); rnd=0; tset={(r,i) for r,i,l in targets}; want={i:(r,l) for r,i,l in targets}
    res={i:[] for r,i,l in targets}
    for e in o['events']:
        t=e['t']
        if t=='roundStart': rnd=e['round']
        elif t=='dragonAction':
            i=e['id']
            if i in want and want[i][0]-K<=rnd<=want[i][0] and e['action'] and 'move' in e['action'] and len(e['action']['move'])==1:
                b=body[i]; L=len(b); dep=min(L+2,40)
                bl={}
                for j in alive:
                    if j==i: continue
                    bj=body[j]
                    for k,p in enumerate(bj): bl[p]=max(bl.get(p,0),len(bj)-k)
                own={}
                chosen=e['action']['move'][0]
                sc={}
                for dd in 'NESW':
                    q=m.step(b[0],dd)
                    sc[dd]=dfs(m,b,q,dep,bl)
                res[i].append((rnd,L,chosen,sc[chosen],dep,max(sc.values())))
        elif t=='dragonUpdate':
            bb=body[e['id']]; bb.insert(0,e['head'])
            while bb and bb[-1]!=e['tail']: bb.pop()
        elif t=='dragonSplit':
            p=e['parent'];c=e['child'];body[p]=list(e['parentBody']);body[c]=list(e['childBody']);team[c]=e['team'];alive.add(c)
        elif t=='dragonDeath': alive.discard(e['id'])
    for i,rows in res.items():
        r,l=want[i]
        first_bad=[x for x in rows if x[3]<x[4] and x[5]>=x[4]]
        first_doom=[x for x in rows if x[5]<x[4]]
        print(d,gid,'W' if win else 'L','death r%d L%d'%(r,l),'| avoidable-with-deep-DFS at',[(x[0],x[2],x[3]) for x in first_bad][:3],'| doomed-from', first_doom[0][0] if first_doom else '-', '| shallow(12) ok at those:', [x[3]>=12 for x in first_bad][:3])
