#!/usr/bin/env python3
"""prun.py NAME BIN_X BIN_Y --seeds N --base B : play portals X vs Y both sides, jobs 6; report per-bot final longest."""
import argparse, subprocess, os, sys, concurrent.futures as cf, statistics as st, math, pickle
SP=os.path.dirname(os.path.abspath(__file__)); ROOT='/Users/devsingh/Developer/UNSW_Battlecode'
sys.path.insert(0,SP)
ap=argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('x'); ap.add_argument('y')
ap.add_argument('--seeds',type=int,default=10); ap.add_argument('--base',type=int,default=5000); ap.add_argument('--map',default='portals')
a=ap.parse_args()
out=f'{SP}/runs/{a.name}'; os.makedirs(out,exist_ok=True)
def play(xa,xb,seed,tag):
    p=f'{out}/{seed}_{tag}.replay'
    if not os.path.exists(p):
        subprocess.run(['unswbc','run',f'{ROOT}/maps/{a.map}.map',xa,xb,'--seed',str(seed),'--no-debug','-o',p],capture_output=True,cwd=ROOT)
    return p
jobs=[]
with cf.ThreadPoolExecutor(6) as ex:
    for s in range(a.base,a.base+a.seeds):
        jobs.append((s,'xA',ex.submit(play,a.x,a.y,s,'xA')))
        jobs.append((s,'xB',ex.submit(play,a.y,a.x,s,'xB')))
    res=[(s,t,f.result()) for s,t,f in jobs]
from por_an import sim, team_stats
X=[];Y=[];wins=0;n=0;rows=[]
for s,t,p in res:
    g=sim(p)
    xs='A' if t=='xA' else 'B'; ys='B' if xs=='A' else 'A'
    sx=team_stats(g,xs); sy=team_stats(g,ys)
    X.append(sx); Y.append(sy)
    fx,fy=sx['final'],sy['final']
    wins+= 1 if fx>fy else 0.5 if fx==fy else 0; n+=1
def m(L,k): return st.mean(x[k] for x in L)
def md(L,k): return st.median(x[k] for x in L)
for lab,L in (('X',X),('Y',Y)):
    print(f"{lab} final mean {m(L,'final'):.1f} med {md(L,'final')} sd {st.pstdev([x['final'] for x in L]):.1f} | hot {m(L,'eat_hot'):.0f} box {m(L,'eat_box'):.0f} corpse {m(L,'eat_corpse'):.0f} deaths {m(L,'deaths'):.0f} big {st.mean(len(x['big']) for x in L):.1f} | total@300/400/499 {st.mean(x['total'][5] for x in L):.0f}/{st.mean(x['total'][7] for x in L):.0f}/{st.mean(x['total'][9] for x in L):.0f} longest@400/450 {st.mean(x['longest'][7] for x in L):.1f}/{st.mean(x['longest'][8] for x in L):.1f} units@100 {st.mean(x['units'][1] for x in L):.0f}")
p=wins/n; print(f'X "wins" (final longest, X vs Y same game) {wins}/{n} = {p:.2f}')
print('X finals',sorted(x['final'] for x in X)); print('Y finals',sorted(x['final'] for x in Y))
