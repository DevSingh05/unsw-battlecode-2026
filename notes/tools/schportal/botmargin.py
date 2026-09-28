#!/usr/bin/env python3
"""Re-run the compiled v22 bot (notes/tools/rams/botview.py) on a random sample of our crossings that a
body-echo rule would forbid but v22 lets through, and print the score margin of the crossing over the best
alternative: the penalty PORTAL_ECHO_BODY_PEN needs to exceed it to redirect the dragon (notes/20 sec 5).
usage (from project root): c++ -std=c++20 -O2 variants/v22/main.cpp -o BIN_DIR/v22
       python3 notes/tools/schportal/botmargin.py BIN_DIR ab_v22_Schooltime 40
"""
import sys, collections, random, pickle
sys.path.insert(0,'notes/tools/rams'); sys.path.insert(0,'notes/tools/schportal')
import botview as BV
from common import *
from rulecost import rule
S=sys.argv[1]; name=sys.argv[2]; N=int(sys.argv[3])
G,m=load(name)
src='ab_v22' if name.startswith('ab_v22') else 'v19plus'
cand=[]
for g in G:
  for r in g['recs']:
    if r['us'] and rule(m,r,mode=3,solo=True) and not rule(m,r):
      cand.append((g['gid'],r))
random.seed(1)
fat=[c for c in cand if fatal(c[1])]; safe=[c for c in cand if not fatal(c[1])]
sample=random.sample(fat,min(N,len(fat)))+random.sample(safe,min(N,len(safe)))
out=[]
for gid,r in sample:
  born=r['round']-r['age']; rf=max(born,r['round']-30)
  mm,turns=BV.capture('replays/%s/%d.replay'%(src,gid), r['id'], rf, r['round'])
  if not turns or turns[-1]['round']!=r['round']: continue
  outs,dbg=BV.run_bot(S+'/v22', r['id'], turns)
  pr=BV.parse_last(dbg, r['round'])
  if not pr or r['dir'] not in pr['cands']: 
    out.append((fatal(r), None, outs[-1] if outs else None, pr['arrow'] if pr else None)); continue
  cs=pr['cands']; sc=cs[r['dir']]['score']
  others=[v['score'] for k,v in cs.items() if k!=r['dir']]
  mg = sc-max(others) if others else 999
  out.append((fatal(r), mg, outs[-1] if outs else None, pr['arrow']))
  print(gid, r['round'], r['L'], 'fatal' if fatal(r) else 'safe', 'real', r['move'], 'bot', outs[-1] if outs else None, 'margin %.1f'%mg, flush=True)
pickle.dump(out, open(S + '/margin_%s.pkl' % name, 'wb'))  
for f in (True,False):
  ms=sorted(x[1] for x in out if x[0]==f and x[1] is not None)
  agree=sum(1 for x in out if x[0]==f and x[1] is not None)
  print('fatal' if f else 'safe', 'n',len(ms), 'margins quantiles', [round(ms[int(q*(len(ms)-1))],1) for q in (0,.25,.5,.75,.9,1)] if ms else None,
        'share <30: %.0f%%, <60: %.0f%%'%(100*sum(x<30 for x in ms)/max(1,len(ms)),100*sum(x<60 for x in ms)/max(1,len(ms))))
