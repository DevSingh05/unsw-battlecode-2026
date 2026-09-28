import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
res=pickle.load(open(S+'qos_top.pkl','rb')); ours=pickle.load(open(S+'qos.pkl','rb'))
ours=[g for g in ours if g['src'] in ('v7','ch5','ch6','ch8')]
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
T={((4,3),(8,33)):'in1',((3,3),(9,33)):'in2',((8,33),(4,3)):'out1',((9,33),(3,3)):'out2'}
def doors(items,label,T1=150):
    C=collections.Counter(); n=len(items)
    for G,side in items:
        last={}
        for m in G['moves']:
            if m['round']>=T1: continue
            p=canon(m['head'],side) if m['team']==side else None
            if p is None: continue
            i=m['id']
            if i in last:
                k=T.get((last[i],p))
                if k: C[k]+=1
            last[i]=p
    print(label,n,{k:'%.1f'%(v/n) for k,v in sorted(C.items())})
doors([(g['G'],g['winner']) for g in res],'TOPW')
doors([(g['G'],'A' if g['winner']=='B' else 'B') for g in res],'TOPL')
doors([(g['G'],g['side']) for g in ours if not g['win']],'US-L')
doors([(g['G'],g['side']) for g in ours if g['win']],'US-W')
