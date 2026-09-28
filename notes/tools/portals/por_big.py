from por_an import *
import collections
def big_deaths(g,T,minL=8):
    out=[]
    for d in g['deaths']:
        if d['team']!=T or d['len']<minL: continue
        out.append(d)
    return out
def classify(d):
    r=d['reason']
    if r=='HitOtherBody' and d.get('hit'): return 'HitOther:'+('ally' if d['hit']['team']==d['team'] else 'enemy')
    if r=='HitHeadToHead': return 'H2H'
    return r
sets={'ours':[], 'ours_loss':[], 'top':[]}
for lab,p,side,win,opp in ours():
    g=sim(p); sets['ours'].append((g,side,win,os.path.basename(p)[:6]))
    if not win: sets['ours_loss'].append((g,side,win,os.path.basename(p)[:6]))
for sub,p,win,a,b in tops():
    g=sim(p)
    for T in 'AB': sets['top'].append((g,T,T==win,os.path.basename(p)[:6]))
for k,S in sets.items():
    C=collections.Counter(); lensum=0; n=0; perround=collections.Counter(); where=collections.Counter()
    for g,T,win,gid in S:
        for d in big_deaths(g,T):
            C[classify(d)]+=1; lensum+=d['len']; n+=1; perround[d['round']//50*50]+=1
    print('==',k,'games',len(S),'big deaths/game %.1f len/game %.1f'%(n/len(S),lensum/len(S)))
    print('  causes/game',{a:round(b/len(S),2) for a,b in C.most_common()})
    print('  by round',sorted((a,round(b/len(S),2)) for a,b in perround.items()))
# detailed list for our losses and v8+ games
print('--- our big deaths (L>=10) detail, recent ch5/6/8')
for lab,p,side,win,opp in ours():
    if lab not in ('ch5','ch6','ch8'): continue
    g=sim(p)
    for d in big_deaths(g,side,10):
        print(os.path.basename(p)[:6],'W' if win else 'L',d['round'],'L',d['len'],classify(d),'head',d['head'],'move',d.get('move'),'nbrs',{k:(v if isinstance(v,str) else v[0]) for k,v in d['nbrs'].items()},'king',d.get('king'))
