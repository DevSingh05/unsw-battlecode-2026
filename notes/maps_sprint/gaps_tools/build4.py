import sys,json,collections,math
import numpy as np
sys.path.insert(0,'/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps')
from est import samples, mir
FILES={'Australia':'australia','Islands':'islands','Maze':'maze','Stripes':'stripes','Tower Defense':'tower_defense','Around UNSW':'around_unsw','weakhold':'weakhold'}
L=512; K=4; EPS=0.01
MGRID=list(range(1,201))+list(range(205,601,5))+list(range(625,1501,25))+list(range(1600,5001,100))
_cache={}
def pmfs(lo,M):
    key=(lo,M)
    if key in _cache: return _cache[key]
    base=np.zeros(L); 
    if lo<L: base[lo:min(M,L-1)+1]=1.0/(M-lo+1)
    out=[base]; cur=base
    for k in range(1,K):
        cur=np.convolve(cur,base)[:L]; out.append(cur)
    P=np.array(out)                     # K x L pmf (truncated)
    S1=np.array([max(0.0,(M-max(c,lo-1))/(M-lo+1)) if c<M else 0.0 for c in range(L)])  # P(g>c) single draw
    _cache[key]=(P,S1); return P,S1
def loglik(s,c,lo,M):
    P,S1=pmfs(lo,M)
    vals=np.array([min(x,L-1) for x in s]); 
    A=P[:,vals]                          # K x n
    w=np.array([0.85,0.1,0.04,0.01])
    flo=EPS/L
    for _ in range(15):
        num=w[:,None]*A; tot=num.sum(0)+flo
        w=(num/tot).sum(1)+1e-9; w/=w.sum()
    ll=np.log((w[:,None]*A).sum(0)*(1-EPS)+flo).sum()
    # censored lower bounds (first draw or residual gap) -> single-draw survival, floor
    for ci in c: ll+=math.log(max(S1[min(ci,L-1)] if ci<L else (max(0,(M-ci))/(M-lo+1)),1e-6))
    return ll,w
def fit(s,c):
    best=None
    los=[1]+([min(s)] if min(s)>1 and len(s)>=8 else [])
    for lo in los:
        for M in MGRID:
            if M<lo: continue
            ll,w=loglik(s,c,lo,M)
            if lo>1: ll-=0.5*math.log(len(s))+2   # complexity penalty for min>1
            if best is None or ll>best[0]: best=(ll,lo,M,w)
    return best
def estimate(name):
    W,H,sym,S,C,cnt=samples(name)
    est={}; info={}
    for k,s in S.items():
        ll,lo,M,w=fit(s,C[k]); est[k]=(lo,M); info[k]=(lo,M,len(s),[round(x,2) for x in w])
    # pool sparse classes (n<8): cluster by M, refit pooled, test for a min>1 subgroup
    sparse=sorted([k for k in S if len(S[k])<8],key=lambda k:est[k][1]); cls=[]
    for k in sparse:
        if cls and est[k][1]<=est[cls[-1][0]][1]*1.3: cls[-1].append(k)
        else: cls.append([k])
    for cl in cls:
        pool=lambda g:([x for k in g for x in S[k]],[x for k in g for x in C[k]])
        s,c=pool(cl); _,lo,M,w=fit(s,c); best=None
        cs=sorted(cl,key=lambda k:min(S[k]))
        for i in range(1,len(cs)-1):
            sb,cb=pool(cs[i:])
            if len(sb)<8: continue
            r=fit(sb,cb)
            if r[1]>1 and (best is None or r[1]>best[1][1]): best=(i,r)
        if best:
            i,r=best; sa,ca=pool(cs[:i]); ra=fit(sa,ca)
            for k in cs[:i]: est[k]=(ra[1],ra[2]); info[k]=info[k]+('pooledA',ra[1],ra[2])
            for k in cs[i:]: est[k]=(r[1],r[2]); info[k]=info[k]+('pooledB',r[1],r[2])
        else:
            for k in cl: est[k]=(lo,M); info[k]=info[k]+('pooled',lo,M)
    for k in cnt:
        if k not in est: est[k]=(1,1000)
    return W,H,sym,est,info
if __name__=='__main__':
    names=sys.argv[2:] or list(FILES)
    for name in names:
        fn=FILES[name]
        W,H,sym,est,info=estimate(name)
        src=open(f'/Users/devsingh/Developer/UNSW_Battlecode/archive/maps_sprint_nogaps/{fn}.map').read().splitlines()
        res=[]
        for l in src:
            p=l.split()
            if p and p[0]=='TILE':
                x,y=int(p[1]),int(p[2]); t=(x,y); k=min(t,mir(t,W,H,sym))
                if k in est: l=f'TILE {x} {y} {est[k][0]} {est[k][1]}'
            res.append(l)
        open(f'{sys.argv[1]}/{fn}.map','w').write('\n'.join(res)+'\n')
        h=collections.Counter(est.values())
        print(name,len(est),'classes;',' '.join(f'{a}-{b}:{v}' for (a,b),v in sorted(h.items(),key=lambda x:x[0][1])))
        json.dump({str(k):v for k,v in info.items()},open(f'{sys.argv[1]}/{fn}.info.json','w'))
