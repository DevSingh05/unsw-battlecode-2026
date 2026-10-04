import sys, json, pickle, math, os
from collections import Counter
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
SHORT={'forgot to mention':'FTM','𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿':'glyph','tungtung67':'tung','Cutlery':'Cutlery','Vibing++':'VIB','horse':'horse','Sponge(Albert and Bob)':'Sponge','SSS':'SSS','bread first search':'BFS','Settlers of Battlecode':'Settlers','Computers':'Computers','Cache me outside':'US'}
def usver(at):
    if at>='2026-10-03T15:27:58': return 'v60'
    if at>='2026-10-03T11:42:04': return 'v55'
    if at>='2026-10-03T07:13:27': return 'v44b'
    if at>='2026-10-02T20:11:58': return 'v49'
    return 'v44'
CK=(1,10,25,50,75,100,150,200,250,300,350,400,450,500)
def analyse(gm):
    gid=gm['id']; path=RD+f'{gid}.replay'
    g=sim2.simulate(path); m=g['map']
    an,bn,aw=SHORT.get(gm['a']['name'],gm['a']['name']),SHORT.get(gm['b']['name'],gm['b']['name']),gm['winner']
    if an=='US': an=usver(gm['at'])
    if bn=='US': bn=usver(gm['at'])
    rw=g['result']['winner']
    if rw is None: return []
    name={'A':an,'B':bn} if (rw=='A')==(aw=='a') else {'A':bn,'B':an}
    q={g['team'][0]:0,g['team'][1]:1}
    portal=set(e for e,(k,p) in m.edges.items() if k==2)
    rd={r:s for r,s in g['rounds']}; last=g['last_round']
    occ_kelp=lambda p: sum(1 for d in 'NESW' if m.step(p,d) is None)
    out=[]
    for T in 'AB':
        E='B' if T=='A' else 'A'; qi=q[T]; eq=q[E]
        r={'gid':gid,'at':gm['at'],'ranked':gm['ranked'],'map':m.name,'team':name[T],'opp':name[E],'win':rw==T,'end':last,'reason':g['result']['endReason']}
        qd=[x for x in g['deaths'] if x['id']==qi]
        if qd:
            x=qd[0]; by=None; kl=None
            if x['reason']=='HitHeadToHead':
                by=x.get('killer_team') or x.get('victim_team'); kl=x.get('killer_len') or x.get('victim_len')
            elif x['reason']=='HitOtherBody' and x['hit']: by=x['hit']['team']; kl=x['hit']['len']
            r['qdeath']=(x['round'],x['reason'],'self' if by==T else ('EN' if by==E else '-'),x['len'],kl)
        else: r['qdeath']=None
        r['qlen']={k:(rd[k][T]['ids'].get(qi,0) if k in rd else None) for k in CK}
        r['qlen_end']=rd[last][T]['ids'].get(qi,0)
        r['eqlen_end']=rd[last][E]['ids'].get(eq,0)
        r['qmax']=max(s[T]['ids'].get(qi,0) for _,s in g['rounds'])
        r['qsplits']=[(x['round'],x['L'],x['k'],x['exits']) for x in g['splits'] if x['parent']==qi]
        qe=[e for e in g['eats'] if e['id']==qi]
        r['qeats']=len(qe); r['qeats_ownc']=sum(1 for e in qe if e['corpse'] and e['corpse'][1]==T)
        r['qeats_late']=sum(1 for e in qe if e['round']>=300)
        spawn=m.dragons[qi][1][0]
        ds=[];de=[];stat=0;nr=0;prev=None;kel=[];nal=[];nen=[]
        for rnd,s in g['rounds']:
            if qi not in s['heads']: continue
            h=s['heads'][qi][0]
            if prev is not None:
                nr+=1; stat+= (h==prev)
            prev=h
            if rnd%5==0:
                ds.append(m.dist(h,spawn))
                eh=[m.dist(h,v[0]) for j,v in s['heads'].items() if v[2]==E]
                if eh: de.append(min(eh))
                kel.append(occ_kelp(h))
                nal.append(sum(1 for j,v in s['heads'].items() if v[2]==T and j!=qi and m.dist(h,v[0])<=4))
                nen.append(sum(1 for j,v in s['heads'].items() if v[2]==E and m.dist(h,v[0])<=4))
        av=lambda a: round(sum(a)/len(a),2) if a else None
        r['q_spawnd']=av(ds); r['q_spawnmax']=max(ds) if ds else None; r['q_enemyd']=av(de); r['q_still']=round(stat/nr,2) if nr else None
        r['q_kelpadj']=av(kel); r['q_allies4']=av(nal); r['q_en4']=av(nen)
        # hunting: our heads within 4 of enemy queen vs within 4 of an average other enemy head
        hq=[];ho=[]
        for rnd,s in g['rounds']:
            if rnd%5 or eq not in s['heads']: continue
            ourh=[v[0] for j,v in s['heads'].items() if v[2]==T]
            eqh=s['heads'][eq][0]
            hq.append(sum(1 for p in ourh if m.dist(p,eqh)<=4))
            oth=[v[0] for j,v in s['heads'].items() if v[2]==E and j!=eq and v[1]<=max(3,s['heads'][eq][1])]
            if oth: ho.append(sum(sum(1 for p in ourh if m.dist(p,o)<=4) for o in oth)/len(oth))
        r['hunt_q']=av(hq); r['hunt_o']=av(ho)
        r['units']={k:(rd[k][T]['n'] if k in rd else None) for k in CK}
        r['tot']={k:(rd[k][T]['total'] if k in rd else None) for k in CK}
        r['longest']={k:(rd[k][T]['max'] if k in rd else None) for k in CK}
        r['eunits']={k:(rd[k][E]['n'] if k in rd else None) for k in CK}
        r['etot']={k:(rd[k][E]['total'] if k in rd else None) for k in CK}
        r['elongest']={k:(rd[k][E]['max'] if k in rd else None) for k in CK}
        r['king_is_q']=rd[last][T]['king']==qi
        mv=[a for a in g['moves'] if a['team']==T and 'move' in a['act']]
        def share(lo,hi,q_only=False):
            b=[a for a in mv if lo<=a['len_before']<=hi and (not q_only or a['id']==qi)]
            return (sum(1 for a in b if a['steps']>=2), sum(1 for a in b if a['steps']>math.ceil(a['len_before']/4)), len(b))
        r['ms']={'2-4':share(2,4),'5-8':share(5,8),'9-16':share(9,16),'17+':share(17,999),'Q5+':share(5,999,True)}
        r['steps_hist']=Counter(a['steps'] for a in mv)
        # paid lunges by L<=4
        paid=[a for a in mv if a['steps']>math.ceil(a['len_before']/4)]
        r['paid']=len(paid); r['paid_eat']=sum(1 for a in paid if a['ate']>0); r['paid_kill']=sum(1 for a in paid if a['killed'])
        pc=0;pcr=Counter()
        for a in mv:
            p=a['head']
            for d in a['act']['move']:
                e=m.side_edge(p,d)
                if e in portal: pc+=1; pcr[min(a['round']//100,4)]+=1
                n=m.step(p,d)
                if n is None: break
                p=n
        r['portal']=pc; r['portal_by100']=dict(pcr); r['has_portal']=bool(portal)
        kills=[x for x in g['deaths'] if x['team']==E and x['reason']=='HitHeadToHead' and (x.get('killer_team')==T)]
        kills+= [x for x in g['deaths'] if x['team']==E and x['reason']=='HitHeadToHead' and x.get('victim_team')==T and x['actor']==x['id']]
        r['h2h_kills']=len(kills); r['killed_len']=sum(x['len'] for x in kills)
        r['kills_big']=sum(1 for x in kills if x['len']>=10)
        r['kill_steps']=Counter(a['steps'] for a in mv if a['killed'])
        r['body_kills']=sum(1 for x in g['deaths'] if x['team']==E and x['reason']=='HitOtherBody' and x['hit'] and x['hit']['team']==T)
        own=[x for x in g['deaths'] if x['team']==T]
        r['own_deaths']=dict(Counter(x['reason'] for x in own))
        r['lost_h2h_big']=sum(1 for x in own if x['reason']=='HitHeadToHead' and x['len']>=10)
        r['eq_killed']=any(x['id']==eq and ((x['reason']=='HitHeadToHead' and (x.get('killer_team')==T or x.get('victim_team')==T)) or (x['reason']=='HitOtherBody' and x['hit'] and x['hit']['team']==T)) for x in g['deaths'])
        r['eq_death']=next(((x['round'],x['reason'],x['len'],x.get('killer_len') or x.get('victim_len'),x.get('steps')) for x in g['deaths'] if x['id']==eq),None)
        r['splits']=sum(1 for x in g['splits'] if x['team']==T)
        r['splits_r50']=sum(1 for x in g['splits'] if x['team']==T and x['round']<=50)
        r['eats']=sum(1 for e in g['eats'] if e['team']==T); r['eats_r100']=sum(1 for e in g['eats'] if e['team']==T and e['round']<=100)
        # endgame: own deaths r>=300 with len>=5: reason, near king/queen
        late=[x for x in own if x['round']>=300 and x['len']>=5 and x['id']!=qi]
        r['late_big_deaths']=dict(Counter(x['reason'] for x in late)); r['late_big_n']=len(late)
        r['late_near_king']=sum(1 for x in late if x.get('king') and x['king'][2]<=3)
        r['late_near_q']=sum(1 for x in late if x.get('king') and x['king'][0]==qi and x['king'][2]<=3)
        qh=None
        # deaths near queen (all, r>=200) via heads snapshot
        nq=0
        for x in own:
            if x['round']<200 or x['id']==qi: continue
            s=rd.get(x['round'])
            if s and qi in s['heads'] and m.dist(s['heads'][qi][0],x['head'])<=3: nq+=1
        r['deaths_nearq_r200']=nq
        r['king_end']=rd[last][T]['max']; r['tot_end']=rd[last][T]['total']; r['units_end']=rd[last][T]['n']
        # opening
        r['open_splits_r10']=[(x['round'],x['L'],x['k']) for x in g['splits'] if x['team']==T and x['round']<=10]
        r['q_firstsplit']=r['qsplits'][0][0] if r['qsplits'] else None
        # early pearl control: eats by r50/r100 in own half (closer to own queen spawn) vs enemy half
        sp_own=m.dragons[qi][1][0]; sp_en=m.dragons[eq][1][0]
        for lim in (50,100,200):
            te=[e for e in g['eats'] if e['team']==T and e['round']<=lim]
            r[f'eat_own_r{lim}']=sum(1 for e in te if m.dist(e['tile'],sp_own)<m.dist(e['tile'],sp_en))
            r[f'eat_en_r{lim}']=sum(1 for e in te if m.dist(e['tile'],sp_own)>m.dist(e['tile'],sp_en))
            r[f'eat_r{lim}']=len(te)
        r['eat_corpse_en']=sum(1 for e in g['eats'] if e['team']==T and e['corpse'] and e['corpse'][1]==E)
        r['eat_corpse_own']=sum(1 for e in g['eats'] if e['team']==T and e['corpse'] and e['corpse'][1]==T)
        out.append(r)
    return out
if __name__=='__main__':
    G=json.load(open(RD+'sample.json'))
    cache=S+'rows_top2.pkl'
    rows=pickle.load(open(cache,'rb')) if os.path.exists(cache) else {}
    for gm in G:
        if gm['id'] in rows or not os.path.exists(RD+f"{gm['id']}.replay"): continue
        try: rows[gm['id']]=analyse(gm)
        except Exception as e: print('fail',gm['id'],e); rows[gm['id']]=[]
        pickle.dump(rows,open(cache,'wb'))
    print(len(rows))
