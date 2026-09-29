#!/usr/bin/env python3
"""Which portal pairs can LEARN_PORTALS learn by walking (both edges come into 7x7 view from tiles reachable
from our spawn with portals treated as kelp)?  usage: python3 notes/unseen/tools/learnable.py maps/*.map"""
import pathlib, sys
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'tools'))
from genmaps import parse
DX=[0,1,0,-1]; DY=[-1,0,1,0]
for path in sys.argv[1:]:
    m=parse(pathlib.Path(path)); w,h,nxt=m['w'],m['h'],m['nxt']; N=w*h
    plain=lambda t,d: ((t//w+DY[d])%h)*w+(t%w+DX[d])%w
    heads=[pts[0][1]*w+pts[0][0] for tm,pts in m['dragons'] if tm==0]
    seen=set(heads); q=deque(heads)
    while q:
        t=q.popleft()
        for d in range(4):
            v=nxt[t*4+d]
            if v!=-1 and v==plain(t,d) and v not in seen: seen.add(v); q.append(v)
    def cheb(a,b):
        dx=abs(a%w-b%w); dy=abs(a//w-b//w); return max(min(dx,w-dx),min(dy,h-dy))
    crossings=[(t,d) for t in range(N) for d in range(4) if nxt[t*4+d]!=-1 and nxt[t*4+d]!=plain(t,d)]
    if not crossings: continue
    # a crossing (t,d)->x: entrance edge visible from a tile within cheb 3 of t; exit edge within cheb 3 of x
    viewable=lambda tile: any(cheb(s,tile)<=3 for s in seen)
    ent_reach=sum(1 for t,d in crossings if t in seen)
    learn=sum(1 for t,d in crossings if t in seen and viewable(nxt[t*4+d]))
    print(f"{pathlib.Path(path).stem:18s} crossings usable from spawn region {ent_reach:3d}/{len(crossings):3d}; "
          f"of those, far end viewable from spawn region {learn:3d} ({100.0*learn/max(1,ent_reach):.0f}%)")
