import sys, json, pickle, os, collections
sys.path.insert(0,'notes/tools')
D='replays/loss_audit2'; P=sys.argv[1]
summ=json.load(open(f'{D}/summary.json'))
def snaps(g):
    return g['rounds']
def snap(g,r):
    best=g['rounds'][0][1]
    for rr,x in g['rounds']:
        if rr<=r: best=x
        else: break
    return best
def qlen(s,q):
    for T in 'AB':
        if q in s[T]['ids']: return s[T]['ids'][q]
    return 0
def dmode(d,T,g):
    r=d['reason']
    if r=='HitHeadToHead':
        if d.get('killer_team') and d.get('killer')!=d['id']:
            sub='H2H_by_'+('ally' if d['killer_team']==T else 'enemy')
        elif d.get('victim_team'):
            sub='H2H_moved_into_'+('ally' if d['victim_team']==T else 'enemy')
        else: sub='H2H_?'
    elif r=='HitOtherBody':
        h=d.get('hit'); sub='Body_'+(('ally' if h['team']==T else 'enemy') if h else '?')
    else: sub=r
    sp=[x for x in g['splits'] if x['parent']==d['id'] and d['round']-4<=x['round']<=d['round']]
    if sp and d['len']<=3: sub+='+trapsplit'
    return sub, [(x['round'],x['L'],x['k'],x['exits']) for x in sp]
out=[]
for s in summ:
    pk=f"{P}/{s['id']}.pkl"
    if not os.path.exists(pk): continue
    g=pickle.load(open(pk,'rb'))
    us=None
    # side: our queen team; find from ab rows? use result winner vs s
    res=g['result']; rw=res.get('winner')
    if s['s']==1: us=rw
    elif s['s']==0: us='B' if rw=='A' else 'A'
    else: continue
    th='B' if us=='A' else 'A'
    uq=0 if g['team'][0]==us else 1; tq=1-uq
    lr=g['last_round']; fin=snap(g,lr)
    qd=next((d for d in g['deaths'] if d['id']==uq),None)
    tqd=next((d for d in g['deaths'] if d['id']==tq),None)
    end=res.get('endReason')
    curve={r:(snap(g,r)[us]['n'],snap(g,r)[us]['total'],snap(g,r)[th]['n'],snap(g,r)[th]['total']) for r in (10,20,30,50,75,100,150,200,300,400) if r<=lr}
    # gap round: first sampled round where their total >= 1.5x ours and +10
    gap=None
    for rr,x in g['rounds']:
        if rr>=5 and x[th]['total']>=1.5*x[us]['total']+10: gap=rr; break
    row=dict(s); row.update(side=us,end=end,last=lr,curve=curve,gap=gap,
        us_final=res.get(us),th_final=res.get(th))
    qinfo={}
    for lab,q,dd,T in (('q',uq,qd,us),('tq',tq,tqd,th)):
        if dd:
            m,sp=dmode(dd,T,g)
            qinfo[lab]=dict(round=dd['round'],len=dd['len'],mode=m,splits=sp,killer_len=dd.get('killer_len'),
                            enemy_near=dd.get('enemy_near'),ally_near=dd.get('ally_near'),nbrs=dd.get('nbrs'),steps=dd.get('steps'))
        else:
            qinfo[lab]=dict(alive=True,len=qlen(fin,q))
    row['qd']=qinfo['q']; row['tqd']=qinfo['tq']
    row['qmax']=max(qlen(x,uq) for _,x in g['rounds']); row['tqmax']=max(qlen(x,tq) for _,x in g['rounds'])
    row['nqsplits']=sum(1 for x in g['splits'] if x['parent']==uq)
    if s['s']==1: cause='WIN'
    elif end!='roundLimit' and fin[us]['n']==0: cause='eliminated'
    else:
        if qd and not tqd: cause='r500_queen_dead:'+qinfo['q']['mode']
        elif not qd and not tqd: cause='r500_queen_shorter'
        elif qd and tqd: cause='r500_both_dead_longest'
        else: cause='r500_weird'
    row['cause']=cause
    out.append(row)
json.dump(out,open(f'{P}/../rows.json','w'),indent=0,default=str)
print(len(out), collections.Counter(r['cause'].split(':')[0] for r in out))
