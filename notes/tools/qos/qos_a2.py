import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
out=pickle.load(open(S+'qos.pkl','rb'))
out=[g for g in out if g['src'] in ('v7','ch5','ch6','ch8')]
def cls(d,us):
    r=d['reason']
    if r=='HitHeadToHead':
        if 'killer' in d: return 'rammed_by_'+('ally' if d['killer_team']==d['team'] else 'enemy')
        if 'victim' in d: return 'ram_'+('ally' if d['victim_team']==d['team'] else 'enemy')
        return 'h2h?'
    if r=='HitOtherBody':
        h=d.get('hit')
        if h: return 'body_'+('ally' if h['team']==d['team'] else 'enemy')
        return 'body?'
    return r
for lab,sel in [('LOSS',lambda g: not g['win']),('WIN',lambda g:g['win'])]:
    gs=[g for g in out if sel(g)]
    for T0,T1 in [(0,100),(100,200),(200,500)]:
        cu=collections.Counter(); ct=collections.Counter(); lu=collections.Counter(); lt=collections.Counter()
        eu=et=0; su=st=0
        for g in gs:
            G=g['G']; us=g['side']
            for d in G['deaths']:
                if not(T0<=d['round']<T1): continue
                c=cls(d,us)
                if d['team']==us: cu[c]+=1; lu[c]+=d['len']
                else: ct[c]+=1; lt[c]+=d['len']
            for e in G['eats']:
                if T0<=e['round']<T1:
                    if e['team']==us: eu+=1
                    else: et+=1
            for s in G['splits']:
                if T0<=s['round']<T1:
                    if s['team']==us: su+=1
                    else: st+=1
        n=len(gs)
        print(lab,n,'rounds',T0,T1,'eats us %.1f them %.1f splits us %.1f them %.1f'%(eu/n,et/n,su/n,st/n))
        print('  us  :',{k:'%.1f(L%.1f)'%(v/n,lu[k]/n) for k,v in cu.most_common()})
        print('  them:',{k:'%.1f(L%.1f)'%(v/n,lt[k]/n) for k,v in ct.most_common()})
