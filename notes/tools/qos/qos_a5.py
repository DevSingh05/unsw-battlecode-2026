import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
out=pickle.load(open(S+'qos.pkl','rb'))
out=[g for g in out if g['src'] in ('v7','ch5','ch6','ch8')]
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
C=collections.Counter(); ex=[]
for g in out:
    if g['win']: continue
    G=g['G']; us=g['side']
    # split rounds by child id
    sp={s['child']:s for s in G['splits']}
    for d in G['deaths']:
        if d['team']!=us or d['round']>=200: continue
        p=canon(d['head'],us)
        if not(6<=p[0]<=11 and 31<=p[1]<=33): continue
        kind=d['reason']
        if kind=='HitOtherBody' and d.get('hit'): kind+='_'+('ally' if d['hit']['team']==us else 'enemy')+('_self?' if d['hit']['id']==d['id'] else '')
        stub = d['id'] in sp and d['age']<=3
        par = d['id'] in [s['parent'] for s in G['splits'] if d['round']-3<=s['round']<=d['round']]
        C[(p,kind)]+=1
        C[('stub' if stub else 'parent_recent' if par else 'other')]+=1
        C[('len',d['len'])]+=1
        if len(ex)<25 and p in [(8,33),(9,33)]: ex.append((g['id'],d['round'],p,kind,d['len'],d['age'],d.get('move'),d['nbrs'],'stub' if stub else ''))
for k,v in sorted(C.items(),key=lambda kv:-kv[1])[:40]: print(v,k)
for e in ex: print(e)
