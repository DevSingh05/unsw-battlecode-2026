import sys,glob,statistics as st
from por_an import *
RR=list(range(200,500,25))+[499]
def curve(games,label):
    rows={'long':[], 'n':[], 'tot':[], '2nd':[]}
    for g,T in games:
        R=dict(g['rounds'])
        rows['long'].append([R[r][T]['max'] for r in RR]); rows['n'].append([R[r][T]['n'] for r in RR]); rows['tot'].append([R[r][T]['total'] for r in RR])
        rows['2nd'].append([(R[r][T]['lens'][1] if len(R[r][T]['lens'])>1 else 0) for r in RR])
    print('==',label,len(games),'rounds',RR)
    for k,v in rows.items(): print(f'  {k:5s}',[round(st.mean(c),1) for c in zip(*v)])
if __name__=='__main__':
    for d in sys.argv[1:]:
        X=[];Y=[]
        for p in sorted(glob.glob(d+'/*.replay')):
            g=sim(p); xs='A' if p.endswith('xA.replay') else 'B'
            X.append((g,xs)); Y.append((g,'B' if xs=='A' else 'A'))
        curve(X,d+' X'); curve(Y,d+' Y')
    sab=[];win=[]
    for sub,p,w_,a,b in tops():
        g=sim(p)
        for T,name in (('A',a),('B',b)):
            if 'Sabotage' in name: sab.append((g,T))
            if T==w_: win.append((g,T))
    curve(sab,'Sabotage'); curve(win,'top winners')
