import sys,glob,os
sys.path.insert(0,'notes/tools'); import replay_sim as RS, replay_decode as RD
def game(f, us):
    o=RD.load(f); m=RS.Map(o['map'])
    body={};team={};alive=set()
    for i,(t,pts) in enumerate(m.dragons): body[i]=[tuple(p) for p in pts]; team[i]='AB'[t]; alive.add(i)
    uq=0 if team[0]==us else 1
    cur=None; d0=None; seen=0; appr=0; adj=0; rnd=0; ex=[]
    def close():
        nonlocal cur,appr,adj
        if cur is not None and cur in alive and uq in alive:
            d1=m.dist(body[cur][0],body[uq][0])
            if d1<=3 and d1<d0: appr+=1; ex.append((rnd,cur,len(body[cur]),d0,d1))
            if d1<=1: adj+=1
        cur=None
    for e in o['events']:
        t=e['t']
        if t=='roundStart': close(); rnd=e['round']
        elif t=='turnStart':
            close()
            i=e['id']
            if team[i]==us and i!=uq and uq in alive and len(body[i])>=8 and m.cheb(body[i][0],body[uq][0])<=3:
                cur=i; d0=m.dist(body[i][0],body[uq][0]); seen+=1
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,tuple(e['head']))
            while b and b[-1]!=tuple(e['tail']): b.pop()
        elif t=='dragonSplit':
            body[e['parent']]=[tuple(p) for p in e['parentBody']]; body[e['child']]=[tuple(p) for p in e['childBody']]; team[e['child']]=e['team']; alive.add(e['child'])
        elif t=='dragonDeath': alive.discard(e['id'])
    return seen,appr,adj,ex
for tag in sys.argv[1:]:
    T=[0,0,0]
    for f in sorted(glob.glob(f'{os.path.dirname(os.path.abspath(__file__))}/mech/{tag}/*.replay')):
        us=f[:-7].split('_')[-1]
        s,a,j,ex=game(f,us); T[0]+=s;T[1]+=a;T[2]+=j
        if os.environ.get('V') and ex: print(os.path.basename(f), ex[:12])
    print(tag,'L>=8 ally turns with our queen in view',T[0],'| moves ending <=3 from her and closer',T[1],'| ending adjacent',T[2])
