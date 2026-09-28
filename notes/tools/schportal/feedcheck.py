#!/usr/bin/env python3
"""Re-run the compiled v22 bot on every self-hit portal crossing to see which were deliberate feed suicides
(notes/20 sec 2). usage (from project root): python3 notes/tools/schportal/feedcheck.py BIN_DIR
"""
import sys, collections
sys.path.insert(0,'notes/tools/rams'); sys.path.insert(0,'notes/tools/schportal')
import botview as BV
from common import *
S=sys.argv[1]
G,m=load('ab_v22_Schooltime')
res=collections.Counter()
for g in G:
  for r in g['recs']:
    if r['us'] and fatal(r) and hitclass(r)=='self':
      born=r['round']-r['age']
      rf=max(born, r['round']-40)
      mm,turns=BV.capture('replays/ab_v22/%d.replay'%g['gid'], r['id'], rf, r['round'])
      outs,dbg=BV.run_bot(S+'/v22', r['id'], turns)
      last=[l for l in dbg.split('\n') if l.strip().startswith('->')]
      res[last[-1].strip() if last else '?']+=1
      print(g['gid'], r['round'], r['L'], 'real', r['move'], 'bot', outs[-1] if outs else None, last[-1] if last else None, flush=True)
print(res)
