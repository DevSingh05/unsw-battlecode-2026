import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
out=pickle.load(open(S+'qos.pkl','rb'))
out=[g for g in out if g['src'] in ('v7','ch5','ch6','ch8')]
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
for lab,sel in [('LOSS',lambda g: not g['win']),('WIN',lambda g:g['win'])]:
    gs=[g for g in out if sel(g)]; n=len(gs)
    for T0,T1 in [(0,100),(100,200),(200,500)]:
        E=collections.Counter(); Dd=collections.Counter(); DL=collections.Counter()
        for g in gs:
            G=g['G']; us=g['side']
            for e in G['eats']:
                if not(T0<=e['round']<T1): continue
                who='us' if e['team']==us else 'th'
                z=zone(canon(e['tile'],us)) if who=='us' else zone(canon(e['tile'],'B' if us=='A' else 'A'))
                E[(who,z,'c' if e['corpse'] else 's')]+=1
            for d in G['deaths']:
                if not(T0<=d['round']<T1): continue
                who='us' if d['team']==us else 'th'
                z=zone(canon(d['head'],us)) if who=='us' else zone(canon(d['head'],'B' if us=='A' else 'A'))
                Dd[(who,z)]+=1; DL[(who,z)]+=d['len']
        print(lab,n,T0,T1)
        for who in ('us','th'):
            print('  ',who,'eats', ' '.join('%s/%s:%.1f'%(z,c,E[(who,z,c)]/n) for z in ['ownroom','opproom','owndoor','oppdoor','open'] for c in 'sc' if E[(who,z,c)]))
            print('  ',who,'deaths',' '.join('%s:%.1f(L%.1f)'%(z,Dd[(who,z)]/n,DL[(who,z)]/n) for z in ['ownroom','opproom','owndoor','oppdoor','open'] if Dd[(who,z)]))
