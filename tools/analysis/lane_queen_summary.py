#!/usr/bin/env python3
"""sum10.py <tag> [base]: summary; base tag pools both teams (b3 vs b3)."""
import sys, json, statistics as st
from collections import Counter
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r10'
rows=json.load(open(f'{S}/mech/{sys.argv[1]}.json')); pool=len(sys.argv)>2
def mean(xs): xs=[x for x in xs if x is not None]; return round(st.mean(xs),1) if xs else None
for m in dict.fromkeys(r['map'] for r in rows):
    for who in (('us','op') if not pool else ('all',)):
        R=[r for r in rows if r['map']==m and (pool or r['who']==who)]
        why=Counter(f"{r['qdwhy'].split('.')[-1][:10]}" for r in R if r['qdr']<999)
        print(f"{m:15s} {who:3s} n{len(R)} | qA100 {sum(r['qdr']>100 for r in R)} qA200 {sum(r['qdr']>200 for r in R)} qA500 {sum(r['qdr']==999 for r in R)} | qL30/50/100/150 {mean([r['ql30'] for r in R])}/{mean([r['ql50'] for r in R])}/{mean([r['ql100'] for r in R])}/{mean([r['ql150'] for r in R])} | n30 {mean([r['n30'] for r in R])} n50 {mean([r['n50'] for r in R])} | t50 {mean([r['t50'] for r in R])} t100 {mean([r['t100'] for r in R])} t300 {mean([r['t300'] for r in R])} | elim {sum(r['elim'] for r in R)} win {sum(r['win'] for r in R)} | cpu {max([r['cpu'] or 0 for r in R])} | qdeaths {dict(why)} qdlen {mean([r['qdlen'] for r in R])} qdr {mean([r['qdr'] for r in R if r['qdr']<999])}")
