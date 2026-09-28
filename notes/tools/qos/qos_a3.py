import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
out=pickle.load(open(S+'qos.pkl','rb'))
out=[g for g in out if g['src'] in ('v7','ch5','ch6','ch8')]
W,H=25,35
heat=collections.Counter(); age=collections.Counter(); lens=collections.Counter(); nb=collections.Counter()
n=0
for g in out:
    G=g['G']; us=g['side']
    if g['win']: continue
    n+=1
    for d in G['deaths']:
        if d['team']!=us or d['round']>=200: continue
        if d['reason'] not in ('HitSelf','HitOtherBody'): continue
        x,y=d['head']
        # canonicalise to our side A frame: if we're B rotate
        if us=='B': x,y=W-1-x,H-1-y
        heat[(x,y)]+=1
        a=d['age']; age['0-3' if a<=3 else '4-10' if a<=10 else '11-30' if a<=30 else '31+']+=1
        lens[d['len']]+=1
        free=sum(1 for v in d['nbrs'].values() if v in ('free','pearl'))
        nb[free]+=1
print('losses',n,'age',age,'len',sorted(lens.items()),'free nbrs at death',nb)
print('    '+''.join('%3d'%x for x in range(W)))
for y in range(H):
    print('%3d '%y+''.join('%3s'%(heat[(x,y)] or '.') for x in range(W)))
