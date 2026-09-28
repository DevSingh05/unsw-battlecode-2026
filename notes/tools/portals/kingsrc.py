import sys
from por_an import *
from por_geo import cls
def lineage_eats(g,T):
    # final longest id, follow parent chain where child took larger part (approx: use parent_of)
    fin=g['rounds'][-1][1][T]; k=fin['king']
    chain=[k]; po=g['parent_of']
    # include ancestors (a reverse split gives body to child)
    while chain[-1] in po: chain.append(po[chain[-1]])
    ids=set(chain)
    src=collections.Counter()
    for e in g['eats']:
        if e['id'] in ids and e['round']>=250:
            c='corpse' if e['corpse'] is not None else cls(e['tile'])
            src[(e['round']//50*50,c)]+=1
    return src
import collections
def rep(games,label):
    agg=collections.Counter()
    for g,T in games:
        for k,v in lineage_eats(g,T).items(): agg[k]+=v
    n=len(games)
    print('==',label,n)
    for r in range(250,500,50):
        print('  ',r,{c:round(agg[(r,c)]/n,1) for c in ('tube','sock','pocket','main','corpse')})
if __name__=='__main__':
    tops_=[];sab=[]
    for sub,p,win,a,b in tops():
        g=sim(p)
        for T,name in (('A',a),('B',b)):
            if T==win: tops_.append((g,T))
            if 'Sabotage' in name: sab.append((g,T))
    rep(tops_,'top winners'); rep(sab,'Sabotage-d')
    import glob
    X=[]; Y=[]
    for p in sorted(glob.glob(sys.argv[1]+'/*.replay')):
        g=sim(p); xs='A' if p.endswith('xA.replay') else 'B'
        X.append((g,xs)); Y.append((g,'B' if xs=='A' else 'A'))
    rep(X,'X'); rep(Y,'Y')
