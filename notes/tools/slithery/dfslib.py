import sys
sys.setrecursionlimit(10000)
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
