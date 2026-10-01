import pickle,sys,collections,statistics as st
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps'
data=pickle.load(open(S+'/data.pkl','rb'))
def hdr(m):
    W=H=0;sym=None
    for l in m.splitlines():
        p=l.split()
        if p and p[0]=='MAP': W,H=int(p[1]),int(p[2])
        if p and p[0]=='SYMMETRY': sym=p[1]
    return W,H,sym
def mir(t,W,H,sym):
    x,y=t
    return {'y':(W-1-x,y),'x':(x,H-1-y),'xy':(W-1-x,H-1-y),None:(x,y)}[sym]
def classes(name):
    G=data[name]; W,H,sym=hdr(G[0]['map'])
    cls=collections.defaultdict(lambda:[[] for _ in G])
    for gi,g in enumerate(G):
        for r,t in g['spawns']:
            k=min(t,mir(t,W,H,sym))
            if not cls[k][gi] or cls[k][gi][-1]!=r: cls[k][gi].append(r)
    return G,W,H,sym,cls
if __name__=='__main__':
    name=sys.argv[1]; G,W,H,sym,cls=classes(name)
    print(name,W,H,sym,len(cls),'classes')
    rows=[]
    for k,v in sorted(cls.items()):
        firsts=[s[0] for s in v if s]; iv=[b-a for s in v for a,b in zip(s,s[1:])]
        n=sum(len(s) for s in v)
        rows.append((k,n,min(firsts) if firsts else None,max(firsts) if firsts else None,min(iv) if iv else None,(st.median(iv) if iv else None),max(iv) if iv else None))
    for r in rows: print(r)
