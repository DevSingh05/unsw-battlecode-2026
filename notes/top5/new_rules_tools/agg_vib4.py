import pickle,sys,statistics as st,collections,math
US=('v61','v69','c1','m1','m2','b1','q1','amb')
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/vib4/'
rows=[r for v in pickle.load(open(S+'rows_vib4.pkl','rb')).values() for r in v]
def lab(r):
    t=r['team']; o=r['opp']
    if t in ('VIB','DEV'):
        if o in US: return t+'vUS'
        return t+'vTOP'
    if t in US and o in ('VIB','DEV'):
        g='new' if t in ('m1','m2','b1','q1') else 'old' if t in ('v61','v69','c1') else None
        return g and ('US'+g+'v'+o)
    return None
for r in rows: r['team0']=r['team']; r['team']=lab(r)
rows=[r for r in rows if r['team']]
for r in rows:
    if r['end']>=499:
        r['qlen'][500]=r['qlen_end']; r['units'][500]=r['units_end']; r['tot'][500]=r['tot_end']; r['longest'][500]=r['king_end']
TEAMS=sys.argv[1].split(',') if len(sys.argv)>1 else ['VIBvUS','VIBvTOP','DEVvUS','DEVvTOP','USnewvVIB','USoldvVIB','USnewvDEV','USoldvDEV']
_X=['VIBvUS','VIBvTOP','VIBvOTH','Cutlery(2Oct)','FTMvUS','FTMvTOP','FTMoldvUS','FTMoldvTOP','SSSvUS','SSSvTOP','SSS(2Oct)','v55vVIB','v55vFTM','v60vVIB','v60vFTM','v55vSSS','v60vSSS','v44bvFTM','v44bvVIB']
def med(a):
    a=[x for x in a if x is not None]; return round(st.median(a),1) if a else '-'
def mean(a):
    a=[x for x in a if x is not None]; return round(sum(a)/len(a),2) if a else '-'
def pct(a): 
    a=list(a); return f"{round(100*sum(a)/len(a))}%" if a else '-'
print('games per team',collections.Counter(r['team'] for r in rows))
for T in TEAMS:
    R=[r for r in rows if r['team']==T]
    if not R: continue
    n=len(R); r5=[r for r in R if r['reason']=='roundLimit']; el=[r for r in R if r['reason']!='roundLimit']
    print(f"\n===== {T}  n={n} win={pct(r['win'] for r in R)}  r500 games {len(r5)} (win {pct(r['win'] for r in r5)}), elim games {len(el)} (win {pct(r['win'] for r in el)})")
    qa=[r['qdeath'] is None for r in R]
    print(' queen alive at end',pct(qa),' r500 games:',pct(r['qdeath'] is None for r in r5),' enemy queen alive (r500):',pct(r['eqlen_end']>0 for r in r5))
    dr=[r['qdeath'][0] for r in R if r['qdeath']]
    print(' queen death round median',med(dr),' quartiles',sorted(dr)[len(dr)//4] if dr else '-',sorted(dr)[3*len(dr)//4] if dr else '-')
    print(' queen death cause',collections.Counter((r['qdeath'][1][:7],r['qdeath'][2]) for r in R if r['qdeath']).most_common(6))
    print(' queen death len',collections.Counter(min(r['qdeath'][3],10) for r in R if r['qdeath']).most_common())
    for k in (25,100,200,300,400,500): print(f"  qlen r{k}: med(all) {med([r['qlen'][k] or 0 for r in R if r['end']>=k])} med(alive) {med([r['qlen'][k] for r in R if r['qlen'][k]])}",end='')
    print()
    print(' qmax med',med([r['qmax'] for r in R]),' king_is_q at end',pct(r['king_is_q'] for r in R), ' qeats med',med([r['qeats'] for r in R]),' own-corpse share',round(sum(r['qeats_ownc'] for r in R)/max(1,sum(r['qeats'] for r in R)),2),' late q eats med',med([r['qeats_late'] for r in R]))
    fs=[r['q_firstsplit'] for r in R]
    print(' queen first split: r0-1',pct(x is not None and x<=1 for x in fs),' never',pct(x is None for x in fs),' med',med(fs),' nsplits med',med([len(r['qsplits']) for r in R]),' splits<=1exit',sum(1 for r in R for s in r['qsplits'] if s[3]<=1 and s[0]>1),'/',sum(len(r['qsplits']) for r in R))
    print(' queen pos: spawnd',mean([r['q_spawnd'] for r in R]),'max',med([r['q_spawnmax'] for r in R]),' enemyd',mean([r['q_enemyd'] for r in R]),' still',mean([r['q_still'] for r in R]),' kelpadj',mean([r['q_kelpadj'] for r in R]),' allies4',mean([r['q_allies4'] for r in R]),' en4',mean([r['q_en4'] for r in R]))
    for key,lab in (('units','units'),('tot','total'),('longest','longest')):
        print(f'  {lab:7}',' '.join(f"r{k}:{med([r[key][k] for r in R if r[key][k] is not None])}" for k in (25,50,100,200,300,400,450,500)),' | end',med([r[{'units':'units_end','tot':'tot_end','longest':'king_end'}[key]] for r in R]))
    print('  opp total',' '.join(f"r{k}:{med([r['etot'][k] for r in R if r['etot'][k] is not None])}" for k in (25,50,100,200,300)))
    agg={b:[0,0,0] for b in ('2-4','5-8','9-16','17+','Q5+')}
    for r in R:
        for b,v in r['ms'].items():
            for i in range(3): agg[b][i]+=v[i]
    print(' multi-step share',{b:(f"{round(100*v[0]/v[2])}% paid{round(100*v[1]/v[2],1)}%" if v[2] else '-') for b,v in agg.items()})
    print(' paid/game',mean([r['paid'] for r in R]),' paid eat',round(sum(r['paid_eat'] for r in R)/max(1,sum(r['paid'] for r in R)),2),' paid kill',round(sum(r['paid_kill'] for r in R)/max(1,sum(r['paid'] for r in R)),2))
    pr=[r for r in R if r['has_portal']]
    print(' portal maps',len(pr),' crossings/game',mean([r['portal'] for r in pr]),' med',med([r['portal'] for r in pr]))
    ks=collections.Counter()
    for r in R: ks.update(r['kill_steps'])
    tk=sum(ks.values())
    print(' h2h kills/game',mean([r['h2h_kills'] for r in R]),' big kills',mean([r['kills_big'] for r in R]),' lost big h2h',mean([r['lost_h2h_big'] for r in R]),' body kills',mean([r['body_kills'] for r in R]),' kill steps',{k:round(v/tk,2) for k,v in sorted(ks.items())} if tk else '-')
    print(' enemy queen killed by us',pct(r['eq_killed'] for r in R),' enemy q death med round',med([r['eq_death'][0] for r in R if r['eq_death']]),' hunt ratio q/o',mean([r['hunt_q'] for r in R]),'/',mean([r['hunt_o'] for r in R]))
    od=collections.Counter()
    for r in R: od.update(r['own_deaths'])
    print(' own deaths/game',{k:round(v/n,1) for k,v in od.most_common()})
    lb=collections.Counter()
    for r in R: lb.update(r['late_big_deaths'])
    print(' r300+ L>=5 non-queen deaths/game',round(sum(r['late_big_n'] for r in R)/n,1),{k:round(v/n,1) for k,v in lb.most_common()},' near king',round(sum(r['late_near_king'] for r in R)/max(1,sum(r['late_big_n'] for r in R)),2),' near queen',round(sum(r['late_near_q'] for r in R)/max(1,sum(r['late_big_n'] for r in R)),2),' own deaths near q r200+/game',mean([r['deaths_nearq_r200'] for r in R]))
    print(' splits/game',mean([r['splits'] for r in R]),' by r50',mean([r['splits_r50'] for r in R]),' eats r100',med([r['eats_r100'] for r in R]),' eats',med([r['eats'] for r in R]))
    if 'eat_own_r50' in R[0]:
        for lim in (50,100,200):
            o=sum(r[f'eat_own_r{lim}'] for r in R); e=sum(r[f'eat_en_r{lim}'] for r in R); t=sum(r[f'eat_r{lim}'] for r in R)
            print(f'  eats by r{lim}: per game {round(t/n,1)}  own half {round(o/n,1)}  enemy half {round(e/n,1)} ({round(100*e/max(1,t))}%)',end='')
        print(); print('  corpse eats/game: enemy corpses',mean([r['eat_corpse_en'] for r in R]),' own corpses',mean([r['eat_corpse_own'] for r in R]))
    # tiebreak breakdown of r500 games
    tb=collections.Counter()
    for r in r5:
        qa,eqa=r['qlen_end'],r['eqlen_end']
        if qa!=eqa: tb['queen '+('W' if r['win'] else 'L')+(' (ours alive)' if qa>eqa else ' (theirs alive)')]+=1
        else: tb['longest '+('W' if r['win'] else 'L')]+=1
    print(' r500 decided by',dict(tb))

    # ---- extras
    print(' OPENING: splits r60',mean([r['splits_r60'] for r in R]),' eat60',mean([r['eat60'] for r in R]),' eat60 in enemy half',mean([r['eat60_en'] for r in R]),' stillborn r100',mean([r['stillborn_r100'] for r in R]),'/ splits r100',mean([r['splits_r100'] for r in R]))
    for k in (10,20,30,45,60):
        o=[r['open'][k] for r in R if k in r['open']]
        print(f'   r{k}: units {med([x["n"] for x in o])} tot {med([x["tot"] for x in o])} heads own/en {mean([x["own"] for x in o])}/{mean([x["en"] for x in o])} qlen {med([x["ql"] for x in o])} q dist spawn {mean([x["qd"] for x in o if x["qd"] is not None])}')
    print(' KING: first round max>=',{th:med([r[f"max{th}"] for r in R if r[f"max{th}"]]) for th in (8,10,15,20,30,40)}, ' share reaching 20/40',pct(r['max20'] is not None for r in R),pct(r['max40'] is not None for r in R))
    print('  queen is king at r200/300/400/450',[pct(r['qking'][k] for r in R if r['qking'][k] is not None) for k in (200,300,400,450)])
    ke=collections.Counter()
    for r in R: ke.update(r['king_eats_late'])
    print('  final king eats r250+ per game',{k:round(v/n,1) for k,v in ke.items()})
    fd=collections.Counter()
    for r in R: fd.update(r['feed'])
    print('  non-queen deaths by reason x century per game',{f"{k[0][:6]}{k[1]}":round(v/n,1) for k,v in sorted(fd.items())})
    kc=collections.Counter()
    for r in R: kc.update(r['killcat'])
    print(' KILLS/game',{k:round(v/n,2) for k,v in sorted(kc.items())})
    print('  queen kills',[r.get('qkill') for r in R if r.get('qkill')][:12])
    bl=[x for r in R for x in r['big_lost']]
    print('  our L>=10 lost head-on per game',round(len(bl)/n,2),' killer steps',collections.Counter(x[3] for x in bl),' killer len med',med([x[2] for x in bl]))
