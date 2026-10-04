#!/usr/bin/env python3
"""Map-set statistics vs the official maps (notes/newrules/UNSEEN_GENERALISATION.md section 5).

usage: python3 notes/newrules/mapstats.py SET [SET ...]      # per-map rows
       python3 notes/newrules/mapstats.py --summary SET ...  # quartiles per set
SET = a folder under maps/ (gen, genhold, lesson, sprint), 'ranked' (the 10 ranked maps), or a path.
Columns: N tiles, nd dragons/team, qlen queen length, kelp = kelp share of edges, pp portal pairs,
wrap = open share of border edges, spf = spawn-tile share, rate_t = pearls/round/tile, hot = tiles with mean gap <= 5,
dqq / dqq_np = BFS steps queen->enemy queen with / without portals (-1 = unreachable), dqe = queen->nearest enemy head,
ring6 = tiles exactly 6 steps from the queen (low = enclosed spawn), ownfood = food share closer to our queen,
ponly / ponly_food = tile / food share reachable only through portals, sealed = unreachable tiles, deadend = leaf-pruned
tiles, corr = tiles with exactly 2 open neighbours.
"""
import sys, pathlib, collections, statistics as st
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/tools')
from genmaps import parse
R = pathlib.Path('/Users/devsingh/Developer/UNSW_Battlecode/maps')

def bfs(m, srcs, portals=True, maxd=10**9):
    w,h,nxt=m['w'],m['h'],m['nxt']
    D=[-1]*(w*h); q=collections.deque()
    for s in srcs: D[s]=0; q.append(s)
    while q:
        t=q.popleft()
        if D[t]>=maxd: continue
        x,y=t%w,t//w
        for d in range(4):
            v=nxt[t*4+d]
            if v<0: continue
            if not portals:
                dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][d]
                plain=((y+dy)%h)*w+(x+dx)%w
                if v!=plain: continue
            if D[v]<0: D[v]=D[t]+1; q.append(v)
    return D

def stats(path):
    m=parse(path); w,h,nxt=m['w'],m['h'],m['nxt']; N=w*h
    kel=sum(1 for t in range(N) for d in (0,3) if nxt[t*4+d]==-1)/(2*N)
    portal=0
    for t in range(N):
        x,y=t%w,t//w
        for d,(dx,dy) in enumerate([(0,-1),(1,0),(0,1),(-1,0)]):
            v=nxt[t*4+d]
            if v>=0 and v!=((y+dy)%h)*w+(x+dx)%w: portal+=1
    portal_pairs=portal/4  # each pair: 2 edges x 2 directions
    border=[nxt[x*4+0] for x in range(w)]+[nxt[(y*w)*4+3] for y in range(h)]
    wrap=sum(1 for v in border if v>=0)/len(border)
    sp=[t for t in range(N) if m['gmax'][t]>0]
    rate=sum(2.0/(m['gmin'][t]+m['gmax'][t]) for t in sp)
    hot=sum(1 for t in sp if (m['gmin'][t]+m['gmax'][t])/2<=5)
    dr=m['dragons']; heads=[p[1][0][1]*w+p[1][0][0] for p in dr]
    teams=[p[0] for p in dr]
    res=dict(name=path.parent.name+'/'+path.stem,W=w,H=h,N=N,sym=m['sym'],kelp=kel,pp=portal_pairs,wrap=wrap,
             spf=len(sp)/N,rate=rate,rate_t=rate/N,hot=hot,nd=len(dr)//2,
             len0=sum(len(p[1]) for p in dr if p[0]==0),qlen=len(dr[0][1]) if dr else 0)
    if len(dr)>=2:
        q=heads[0]; eq=heads[1]
        Dq=bfs(m,[q]); Dnp=bfs(m,[q],portals=False)
        res['dqq']=Dq[eq]
        en=[heads[i] for i in range(len(dr)) if teams[i]!=teams[0]]
        res['dqe']=min(Dq[e] for e in en if Dq[e]>=0) if any(Dq[e]>=0 for e in en) else -1
        reach=sum(1 for v in Dq if v>=0)
        res['qreach']=reach/N
        res['ball6']=sum(1 for v in Dq if 0<=v<=6)
        res['ring6']=sum(1 for v in Dq if v==6)
        # pearl rate near queen (<=10) vs map
        res['qfood10']=sum(2.0/(m['gmin'][t]+m['gmax'][t]) for t in sp if 0<=Dq[t]<=10)
        # own half food share (closer to queen than enemy queen)
        De=bfs(m,[eq])
        own=sum(2.0/(m['gmin'][t]+m['gmax'][t]) for t in sp if Dq[t]>=0 and (De[t]<0 or Dq[t]<De[t]))
        res['ownfood']=own/rate if rate else 0
        # portal-only area: reachable from any head with portals but not without
        Dall=bfs(m,heads); Dalln=bfs(m,heads,portals=False)
        po=[t for t in range(N) if Dall[t]>=0 and Dalln[t]<0]
        res['ponly']=len(po)/N
        res['ponly_food']=sum(2.0/(m['gmin'][t]+m['gmax'][t]) for t in po if m['gmax'][t]>0)/rate if rate else 0
        res['sealed']=sum(1 for t in range(N) if Dall[t]<0)/N
        res['dqq_np']=Dnp[eq]
    # leaf-prune dead ends
    deg=[0]*N
    for t in range(N):
        deg[t]=len(set(v for v in nxt[t*4:t*4+4] if v>=0 and v!=t))
    alive=[True]*N; q=[t for t in range(N) if deg[t]<=1]
    nb=lambda t:set(v for v in nxt[t*4:t*4+4] if v>=0 and v!=t)
    rev=collections.defaultdict(set)
    for t in range(N):
        for v in nb(t): rev[v].add(t)
    while q:
        t=q.pop()
        if not alive[t]: continue
        alive[t]=False
        for v in nb(t)|rev[t]:
            if alive[v]:
                deg[v]-=1
                if deg[v]==1: q.append(v)
    res['deadend']=sum(1 for a in alive if not a)/N
    # corridor tiles: exactly 2 open neighbours
    res['corr']=sum(1 for t in range(N) if len(nb(t))==2)/N
    return res

RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy", "autarky", "dilemma",
          "slithery_fight", "trauma"]
KEYS = ['name', 'W', 'H', 'N', 'sym', 'nd', 'qlen', 'len0', 'kelp', 'pp', 'wrap', 'spf', 'rate', 'rate_t', 'hot', 'dqq',
        'dqq_np', 'dqe', 'ball6', 'ring6', 'qfood10', 'ownfood', 'ponly', 'ponly_food', 'sealed', 'deadend', 'corr']
SUMK = ['N', 'nd', 'qlen', 'kelp', 'pp', 'wrap', 'spf', 'rate_t', 'hot', 'dqq', 'dqe', 'ring6', 'ponly_food', 'deadend', 'corr']


def files_of(s):
    if s == 'ranked':
        return [R / f'{m}.map' for m in RANKED]
    p = R / s if not s.startswith('/') else pathlib.Path(s)
    return sorted(p.glob('*.map')) if p.is_dir() else [p if str(p).endswith('.map') else pathlib.Path(str(p) + '.map')]


if __name__ == '__main__':
    args = sys.argv[1:]
    summary = '--summary' in args
    args = [a for a in args if a != '--summary']
    for s in args:
        rows = [stats(f) for f in files_of(s)]
        if summary:
            out = f"{s:10s} n={len(rows):2d}"
            for k in SUMK:
                v = sorted(r[k] for r in rows if k in r and r[k] != -1)
                if v:
                    q = lambda p: v[min(len(v) - 1, int(p * len(v)))]
                    out += f"  {k} {q(.25):.3g}/{st.median(v):.3g}/{q(.75):.3g}"
            syms = collections.Counter(r['sym'] for r in rows)
            print(out + f"  sym {dict(syms)}")
            continue
        print(' '.join(f'{k[:7]:>7}' for k in KEYS))
        for r in rows:
            print(' '.join(f'{r.get(k, ""):>7.3f}' if isinstance(r.get(k), float) else
                           (f'{str(r.get(k, ""))[:22]:<22}' if k == 'name' else f'{str(r.get(k, "")):>7}') for k in KEYS))
