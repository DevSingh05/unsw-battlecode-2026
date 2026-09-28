import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
res=pickle.load(open(S+'qos_top.pkl','rb'))
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def zone(p):
    x,y=p
    if 6<=x<=11 and 31<=y<=33: return 'ownroom'
    if 13<=x<=18 and 1<=y<=3: return 'opproom'
    if (x,y) in [(3,3),(4,3),(3,2),(4,2),(4,4),(5,3)]: return 'owndoor'
    if (x,y) in [(21,31),(20,31),(21,32),(20,30),(20,32),(19,31)]: return 'oppdoor'
    return 'open'
def cls(d):
    r=d['reason']
    if r=='HitHeadToHead':
        if 'killer' in d: return 'rammed_by_'+('ally' if d['killer_team']==d['team'] else 'enemy')
        if 'victim' in d: return 'ram_'+('ally' if d['victim_team']==d['team'] else 'enemy')
        return 'h2h?'
    if r=='HitOtherBody':
        h=d.get('hit')
        if h: return 'body_'+('ally' if h['team']==d['team'] else 'enemy')
    return r
for T0,T1 in [(0,100),(100,200)]:
  for role in ('W','L'):
    E=collections.Counter(); Dd=collections.Counter(); DL=collections.Counter(); C=collections.Counter(); sp=0; stubs=0
    n=len(res)
    for g in res:
        G=g['G']; side=g['winner'] if role=='W' else ('A' if g['winner']=='B' else 'B')
        for e in G['eats']:
            if T0<=e['round']<T1 and e['team']==side:
                E[(zone(canon(e['tile'],side)),'c' if e['corpse'] else 's')]+=1
        for d in G['deaths']:
            if T0<=d['round']<T1 and d['team']==side:
                z=zone(canon(d['head'],side)); Dd[z]+=1; DL[z]+=d['len']; C[cls(d)]+=1
                if d['age']<=3 and d['id'] in G['parent_of']: stubs+=1
        for s in G['splits']:
            if T0<=s['round']<T1 and s['team']==side: sp+=1
    print(role,T0,T1,'splits %.1f stubs %.1f'%(sp/n,stubs/n))
    print('  eats',' '.join('%s/%s:%.1f'%(k[0],k[1],v/n) for k,v in sorted(E.items())))
    print('  deaths',' '.join('%s:%.1f(L%.1f)'%(z,Dd[z]/n,DL[z]/n) for z in Dd))
    print('  causes',' '.join('%s:%.1f'%(k,v/n) for k,v in C.most_common()))
