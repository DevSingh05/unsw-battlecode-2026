"""Extra per-team fields for an_vib4.py (opening, king timing, kill types, endgame)."""
import math,collections
def extra(g,m,T,E,qi,eq,rd,r):
    so=m.dragons[qi][1][0]; se=m.dragons[eq][1][0]
    half=lambda p: 'own' if m.dist(p,so)<m.dist(p,se) else ('en' if m.dist(p,so)>m.dist(p,se) else 'mid')
    op={}
    for k in (10,20,30,45,60):
        s=rd.get(k)
        if not s: continue
        hs=[v for j,v in s['heads'].items() if v[2]==T]
        op[k]={'n':len(hs),'tot':s[T]['total'],'own':sum(1 for v in hs if half(v[0])=='own'),'en':sum(1 for v in hs if half(v[0])=='en'),
               'qd':(m.dist(s['heads'][qi][0],so) if qi in s['heads'] else None),'ql':s[T]['ids'].get(qi,0),
               'lens':sorted([v[1] for v in hs],reverse=True)[:4]}
    r['open']=op
    r['open_splits']=[(x['round'],x['L'],x['k'],x['parent']==qi) for x in g['splits'] if x['team']==T and x['round']<=60][:12]
    r['splits_r60']=sum(1 for x in g['splits'] if x['team']==T and x['round']<=60)
    # eats r<=60 by half
    e60=[e for e in g['eats'] if e['team']==T and e['round']<=60]
    r['eat60']=len(e60); r['eat60_en']=sum(1 for e in e60 if half(e['tile'])=='en')
    # stillborn: children dying within 1 round
    born={x['child']:x['round'] for x in g['splits'] if x['team']==T}
    dd={x['id']:x['round'] for x in g['deaths']}
    r['stillborn_r100']=sum(1 for c,b in born.items() if b<=100 and c in dd and dd[c]-b<=1)
    r['splits_r100']=sum(1 for c,b in born.items() if b<=100)
    # king timing
    for th in (8,10,15,20,30,40):
        r[f'max{th}']=next((k for k,s in g['rounds'] if s[T]['max']>=th),None)
    r['qking']={k:(rd[k][T]['king']==qi if k in rd else None) for k in (200,300,400,450)}
    r['max_curve']={k:(rd[k][T]['max'] if k in rd else None) for k in (150,250,350,450)}
    # feeding: suicides / NoValidAction by bucket
    fd=collections.Counter()
    for x in g['deaths']:
        if x['team']==T and x['reason'] in ('NoValidAction','Suicide','HitSelf','HitOtherBody','HitWall') and x['id']!=qi:
            fd[(x['reason'],min(x['round']//100,4))]+=1
    r['feed']=dict(fd)
    # king eats after r300
    ke=collections.Counter()
    last=g['last_round']; kid=rd[last][T]['king']
    for e in g['eats']:
        if e['team']==T and e['id']==kid and e['round']>=250:
            ke['own' if e['corpse'] and e['corpse'][1]==T else 'en' if e['corpse'] else 'fresh']+=1
    r['king_eats_late']=dict(ke); r['king_final_id']=kid
    # kill categories
    kc=collections.Counter()
    for a in g['moves']:
        if a['team']!=T or 'move' not in a['act']: continue
        L=a['len_before']; F=math.ceil(L/4); paid=max(0,a['steps']-F)
        kills=[k for k in a['killed'] if k[1]!=T]
        lc='L2' if L==2 else 'L3' if L==3 else 'L4-6' if L<=6 else 'L7-12' if L<=12 else 'L13+'
        if paid>0 and not kills: kc['paid_nokill_'+('eat' if a['ate'] else 'noeat')]+=1
        for k in kills:
            kc['n']+=1; kc[f's{min(a["steps"],4)}']+=1; kc['lc_'+lc]+=1
            if paid: kc['paid']+=1
            if paid and a['ate']: kc['paid_ate']+=1
            if a['steps']>=3: kc['s3_victim'+('2-3' if k[2]<=3 else '4-9' if k[2]<10 else '10+')]+=1
            if k[0]==eq: kc['queen']+=1; r['qkill']=(a['round'],L,a['steps'],k[2],a['id']==rd.get(a['round'],rd[last])[T]['king'] if a['round'] in rd else None)
    r['killcat']=dict(kc)
    # big own losses: our L>=10 dragons killed head-on, steps of killer
    bl=[]
    for x in g['deaths']:
        if x['team']==T and x['reason']=='HitHeadToHead' and x['len']>=10 and 'killer' in x:
            mv=[a for a in g['moves'] if a['id']==x['killer'] and a['round']==x['round']]
            bl.append((x['round'],x['len'],x.get('killer_len'),mv[0]['steps'] if mv else None,x['id']==qi))
    r['big_lost']=bl
    # tiebreak trajectory every 25 rounds from 300
    tr={}
    for k in range(300,501,25):
        s=rd.get(k)
        if s: tr[k]=(s[T]['ids'].get(qi,0),s[E]['ids'].get(eq,0),s[T]['max'],s[E]['max'],s[T]['total'],s[E]['total'])
    r['tb_traj']=tr
