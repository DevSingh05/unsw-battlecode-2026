import collections,glob,sys
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
C=collections.Counter(); n=0
for f in sorted(glob.glob(S+'qreps/*.replay')):
    G=simulate(f); n+=2
    for d in G['deaths']:
        p=canon(d['head'],d['team'])
        if p in [(4,3),(3,3),(8,33),(9,33)]:
            C[(p,'age0' if d['age']==0 else 'older',d['reason'][:8])]+=1
for k,v in C.most_common(): print('%.2f'%(v/n),k)
