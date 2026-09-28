import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
ours=[g for g in pickle.load(open(S+'qos.pkl','rb')) if g['src'] in ('v7','ch5','ch6','ch8')]
top=pickle.load(open(S+'qos_top.pkl','rb'))
W,H=25,35
FL={'N':'S','S':'N','E':'W','W':'E'}
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def cn(nb,side):
    return nb if side=='A' else {FL[k]:v for k,v in nb.items()}
def lab(v):
    if isinstance(v,(tuple,list)): return v[0]+('H' if v[1] else '')
    return v
def run(items,label,T1=150):
    C=collections.Counter(); n=len(items)
    for G,side in items:
        for d in G['deaths']:
            if d['team']!=side or d['round']>=T1: continue
            p=canon(d['head'],side)
            if p not in [(8,33),(9,33),(3,3),(4,3)]: continue
            nb={k:lab(v) for k,v in cn(d['nbrs'],side).items()}
            neck=[k for k,v in nb.items() if v=='self']
            key=(p,'neck'+''.join(neck), 'N='+nb['N'],'E='+nb['E'],'W='+nb['W'], d['reason'][:8], 'L%d'%d['len'])
            C[key]+=1
    print(label,n)
    for k,v in C.most_common(22): print('  %.2f'%(v/n),k)
run([(g['G'],g['side']) for g in ours],'US all')
run([(g['G'],g['winner']) for g in top],'TOP W')
print('---- (4,3)/(3,3)/(9,33)/(8,33) neck-through-portal HitSelf details (ours)')
cnt=collections.Counter()
for g in ours:
    G=g['G']; side=g['side']
    born_split={s['child']:s for s in G['splits']}
    for d in G['deaths']:
        if d['team']!=side: continue
        p=canon(d['head'],side)
        if p in [(4,3),(3,3)] and d['reason']=='HitSelf':
            nb={k:lab(v) for k,v in cn(d['nbrs'],side).items()}
            if (p==(4,3) and nb['W']=='self') or (p==(3,3) and nb['E']=='self'):
                child = d['id'] in born_split
                cnt[(p,'age%d'%min(d['age'],5),'child' if child else 'orig', 'move='+str(d.get('move')))]+=1
for k,v in cnt.most_common(): print(v,k)
