import pickle,collections as C
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/horse/'
R=pickle.load(open(S+'prof.pkl','rb'))
def grp(x):
    m=x['meta'];lab=m['lab'];H='A' if lab['A']=='HORSE' else 'B';O='B' if H=='A' else 'A'
    o=lab[O]; post=m['at']>='2026-10-06T18:00'
    g=('US' if o in('b4','kf1','amb','b3') else 'TOP')+('' if post else '_pre')
    return g,H,O
G=C.defaultdict(list)
for gid,x in R.items():
    if not x: continue
    g,H,O=grp(x); G[g].append((gid,x,H,O))
for g,L in sorted(G.items()):
    n=len(L); print('\n==',g,'games',n)
    for side in ('H','O'):
        st=C.Counter(); kills=C.Counter(); kl=C.Counter(); paid=0;nk=0; dr=C.Counter(); mult=0; portal=[];splits=[];qalive=0;qk=0;qdr=[];first=[]
        for gid,x,H,O in L:
            T=H if side=='H' else O; r=x[T]
            for k,v in r['steps'].items(): st[k[1]]+=v
            for k in r['kills']:
                nk+=1; kills[min(k['steps'],5)]+=1; kl['L2' if k['kl']<=2 else 'L3' if k['kl']==3 else 'L4-7' if k['kl']<=7 else 'L8+']+=1; paid+=k['paid']>0; mult+=k['mutual']
            for d in r['deaths']: dr[(d['reason'][:9], 'q' if d['q'] else ('L10+' if d['len']>=10 else 's'))]+=1
            if r['portal'] is not None: portal.append(r['portal'])
            splits.append(sum(1 for s in r['splits'] if s[0]<100))
            if r['q_death'] is None: qalive+=1
            else: qdr.append(r['q_death'][0])
            if r['q_splits']: first.append(r['q_splits'][0][0])
        tot=sum(st.values())
        print(side,'steps%',{k:round(100*v/tot) for k,v in sorted(st.items())},'kills/g',round(nk/n,1),'steps',dict(sorted(kills.items())),'killerL',dict(kl),'paid',paid,'mutual',mult)
        print('  splits<r100/g',round(sum(splits)/n,1),'portal/g',round(sum(portal)/max(1,len(portal)),1),'qalive',qalive,'/',n,'qdeath med',sorted(qdr)[len(qdr)//2] if qdr else None,'q first split med',sorted(first)[len(first)//2] if first else None)
        print('  deaths/g',{k:round(v/n,1) for k,v in sorted(dr.items(),key=lambda t:-t[1])[:9]})
