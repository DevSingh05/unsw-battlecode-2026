import sys,glob,collections
from por_an import *
from por_geo import cls
def cat(games,label):
    C=collections.Counter(); n=len(games); lost=collections.Counter(); ex=[]
    for g,T in games:
        R=dict(g['rounds'])
        for d in g['deaths']:
            if d['team']!=T or d['len']<8: continue
            k=d.get('king')
            wasking = (k is None) or (d['len']>=k[1])
            near = k is not None and k[2]<=4
            c=('KING' if wasking else ('merge<=4' if near else 'far')) + '/' + cls(d['head']) + '/' + d['reason'] + ('/ally' if d.get('hit') and d['hit']['team']==T else '')
            C[c]+=1; lost[c]+=d['len']
            if wasking: ex.append((d['round'],d['len'],d['reason'],d['head'],cls(d['head']),d.get('move'),{kk:(v if isinstance(v,str) else v[0]) for kk,v in d['nbrs'].items()}))
    print('==',label,n)
    for c,v in C.most_common(): print(f'  {c:40s} {v/n:5.2f}/game  len {lost[c]/n:5.1f}/game')
    for e in ex[:25]: print('   KINGDEATH',e)
games=[]
for d in sys.argv[1:]:
    for p in sorted(glob.glob(d+'/*.replay')):
        g=sim(p); xs='A' if p.endswith('xA.replay') else 'B'; games.append((g,xs))
cat(games,'X of '+' '.join(sys.argv[1:]))
