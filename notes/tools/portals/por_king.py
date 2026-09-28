from por_an import *
from por_geo import cls
import collections
def king_info(g,T):
    # king = longest at each round; count location classes of king head r300-499 and king spawn eats
    R=g['rounds']; kid={r:snap[T]['king'] for r,snap in R}
    loc=collections.Counter(); se=0; ce=0; n=0
    heads={}
    for m in g['moves']:
        if m['team']==T and 300<=m['round']<=499 and kid.get(m['round'])==m['id']:
            loc[cls(m['head'])]+=1; n+=1
    for e in g['eats']:
        if e['team']==T and 300<=e['round']<=499 and kid.get(e['round'])==e['id']:
            if e['corpse'] is None: se+=1
            else: ce+=1
    return {k:round(v/max(n,1),2) for k,v in loc.items()}, se, ce
def rep(S,label):
    L=[];SE=[];CE=[]
    for g,T in S:
        loc,se,ce=king_info(g,T); L.append(loc); SE.append(se); CE.append(ce)
    keys=['main','tube','sock','pocket']
    print('==',label,len(S),'king loc frac',{k:round(med([l.get(k,0) for l in L]),2) for k in keys},'king spawn eats r300+',med(SE),'corpse eats',med(CE))
O=[];Tw=[];Tl=[]
for lab,p,side,win,opp in ours(): O.append((sim(p),side))
for sub,p,win,a,b in tops():
    g=sim(p); Tw.append((g,win)); Tl.append((g,'B' if win=='A' else 'A'))
rep(O,'ours'); rep(Tw,'top winners'); rep(Tl,'top losers')
