import collections,glob,sys,os
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
W,H=25,35
FL={'N':'S','S':'N','E':'W','W':'E'}
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def lab(v):
    if isinstance(v,(tuple,list)): return v[0]+('H' if v[1] else '')
    return v
C=collections.Counter(); n=0
for f in sorted(glob.glob(S+sys.argv[1]+'/*.replay')):
    base=os.path.basename(f)
    a,b=base.split('_vs_')
    side='A' if 'qbot' in a else 'B'
    G=simulate(f); n+=1
    for d in G['deaths']:
        if d['team']!=side: continue
        p=canon(d['head'],side)
        if p not in [(4,3),(3,3),(8,33),(9,33),(8,32),(9,32),(3,2)]: continue
        nb={(k if side=='A' else FL[k]):lab(v) for k,v in d['nbrs'].items()}
        neck=''.join(k for k,v in nb.items() if v=='self')
        C[(p,'neck'+neck,'N='+nb['N'],'E='+nb['E'],'S='+nb['S'],'W='+nb['W'],'age0' if d['age']==0 else '')]+=1
for k,v in C.most_common(15): print('%.2f'%(v/n),k)
