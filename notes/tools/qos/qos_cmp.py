import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
ours=[g for g in pickle.load(open(S+'qos.pkl','rb')) if g['src'] in ('v7','ch5','ch6','ch8')]
top=pickle.load(open(S+'qos_top.pkl','rb'))
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def grid(items,label,T1=150):
    D=collections.Counter(); n=len(items); cause=collections.Counter()
    for G,side in items:
        for d in G['deaths']:
            if d['team']!=side or d['round']>=T1: continue
            p=canon(d['head'],side)
            if 3<=p[0]<=12 and (p[1]>=30 or p[1]<=4): D[p]+=1
    print(label,n)
    for y in list(range(0,5))+list(range(30,35)):
        print('%3d '%y+''.join('%5s'%('%.1f'%(D[(x,y)]/n) if D[(x,y)] else '.') for x in range(3,13)))
grid([(g['G'],g['side']) for g in ours if not g['win']],'US losses (x3..12)')
grid([(g['G'],g['side']) for g in ours if g['win']],'US wins')
grid([(g['G'],g['winner']) for g in top],'TOP W')
