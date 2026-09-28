from por_an import *
from por_geo import cls, POCKET, TUBE
import collections
print(len(POCKET),len(TUBE))
def run(S,label):
    C=collections.Counter(); CB=collections.Counter(); n=len(S); pk=collections.Counter()
    for g,T in S:
        for d in g['deaths']:
            if d['team']!=T: continue
            k=cls(d['head']); C[(k)]+=1
            if d['len']>=8: CB[(k,d['reason'])]+=1
            if k=='pocket': pk[d['len']]+=1
    print('==',label,n,'deaths/game by loc',{a:round(b/n,1) for a,b in C.items()})
    print('   L>=8 by loc,reason',{a:round(b/n,2) for a,b in CB.most_common(12)})
    print('   pocket death lengths',sorted(pk.items())[:15])
O=[];L=[];Tp=[]
for lab,p,side,win,opp in ours():
    O.append((sim(p),side))
    if lab in ('ch5','ch6','ch8'): L.append((sim(p),side))
for sub,p,win,a,b in tops():
    g=sim(p); Tp+= [(g,'A'),(g,'B')]
run(O,'ours all'); run(L,'ours recent'); run(Tp,'top')
