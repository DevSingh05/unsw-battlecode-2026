import sys,glob,collections,statistics as st
from por_an import *
def eff(g,T,r0=300):
    R=dict(g['rounds'])
    kid={r:snap[T]['king'] for r,snap in g['rounds']}
    dmass=sum(d['len'] for d in g['deaths'] if d['team']==T and d['round']>=r0)
    ndeath=sum(1 for d in g['deaths'] if d['team']==T and d['round']>=r0)
    drop=sum((d['len']+1)//2 for d in g['deaths'] if d['team']==T and d['round']>=r0)
    ce=[e for e in g['eats'] if e['team']==T and e['round']>=r0 and e['corpse'] is not None]
    ck=sum(1 for e in ce if kid.get(e['round'])==e['id'])
    se=[e for e in g['eats'] if e['team']==T and e['round']>=r0 and e['corpse'] is None]
    sk=sum(1 for e in se if kid.get(e['round'])==e['id'])
    return dict(deaths=ndeath,dmass=dmass,drop=drop,corpse_eaten=len(ce),corpse_by_king=ck,spawn=len(se),spawn_by_king=sk,final=R[max(R)][T]['max'])
def rep(games,label):
    rows=[eff(g,T) for g,T in games]
    print('==',label,len(rows),{k:round(st.mean(r[k] for r in rows),1) for k in rows[0]})
if __name__=='__main__':
    X=[]
    for d in sys.argv[1:]:
        for p in sorted(glob.glob(d+'/*.replay')):
            g=sim(p); xs='A' if p.endswith('xA.replay') else 'B'; X.append((g,xs))
    rep(X,'X')
    sab=[];win=[]
    for sub,p,w_,a,b in tops():
        g=sim(p)
        for T,name in (('A',a),('B',b)):
            if 'Sabotage' in name: sab.append((g,T))
            if T==w_: win.append((g,T))
    rep(sab,'Sabotage'); rep(win,'top winners')
