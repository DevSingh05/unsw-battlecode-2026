import pickle,collections,statistics as st
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
rows=[r for v in pickle.load(open(S+'rows.pkl','rb')).values() for r in v]
TEAMS=['Cutlery','horse','Sponge','SSS','BFS','v41','v43']
def med(a):
    a=[x for x in a if x is not None]; return round(st.median(a),1) if a else '-'
print('== r500 outcome classes (team perspective)')
for T in TEAMS:
    R=[r for r in rows if r['team']==T and r['reason']=='roundLimit']
    c=collections.Counter()
    for r in R:
        q,e=r['qlen_end'],r['eqlen_end']
        if q and e: cls='both alive, '+('ours longer' if q>e else 'theirs longer' if e>q else 'equal')
        elif q: cls='only ours alive'
        elif e: cls='only theirs alive'
        else: cls='both dead'
        c[(cls,'W' if r['win'] else 'L')]+=1
    print(T,len(R),sorted(c.items()))
print('== losses by end type')
for T in TEAMS:
    R=[r for r in rows if r['team']==T and not r['win']]
    print(T,len(R),collections.Counter('elim' if r['reason']!='roundLimit' else ('queenTB' if r['qlen_end']!=r['eqlen_end'] else 'longest') for r in R))
print('== enemy-queen survivors: profile of the ENEMY queen when it lived to r500 in games vs us (by opp)')
for T in ['v41','v43']:
    R=[r for r in rows if r['team']==T]
    for O in ['Cutlery','horse','Sponge','SSS','BFS']:
        RO=[r for r in R if r['opp']==O]
        mirror=[x for x in rows if x['opp']==T and x['team']==O]
        if not RO: continue
        alive=[x for x in mirror if x['qdeath'] is None and x['reason']=='roundLimit']
        print(f" {T} v {O}: n={len(RO)} W={sum(r['win'] for r in RO)} ourQ alive end {sum(r['qdeath'] is None for r in RO)} theirQ alive end {sum(x['qdeath'] is None for x in mirror)}; their surviving queens: len {[x['qlen_end'] for x in alive]} still {[x['q_still'] for x in alive]} allies4 {[x['q_allies4'] for x in alive]} enemyd {[x['q_enemyd'] for x in alive]}")
print('== our queen deaths detail')
for T in ['v41','v43']:
    R=[r for r in rows if r['team']==T and r['qdeath']]
    print(T,'by round bucket',sorted(collections.Counter(min(r['qdeath'][0]//50*50,450) for r in R).items()))
    print(T,'by cause x len',collections.Counter((r['qdeath'][1][:8],r['qdeath'][2],r['qdeath'][3]) for r in R).most_common(12))
    print(T,'by map',collections.Counter(r['map'] for r in R).most_common(), ' games by map',collections.Counter(r['map'] for r in rows if r['team']==T).most_common())
print('== who killed enemy queens: killer len, steps (from eq_death)')
for T in TEAMS:
    R=[r for r in rows if r['team']==T and r['eq_killed'] and r['eq_death']]
    print(T,len(R),'killerL',collections.Counter(min(r['eq_death'][3] or 0,10) for r in R).most_common(5),'eq len',collections.Counter(min(r['eq_death'][2],10) for r in R).most_common(5),'round med',med([r['eq_death'][0] for r in R]))
print('== per-map win rate (all opponents in sample)')
maps=sorted(set(r['map'] for r in rows))
print(f"{'map':18}"+''.join(f'{t:>9}' for t in TEAMS))
for mp in maps:
    s=f'{mp[:18]:18}'
    for T in TEAMS:
        R=[r for r in rows if r['team']==T and r['map']==mp]
        s+=f"{sum(r['win'] for r in R):>4}/{len(R):<4}" if R else '        -'
    print(s)
print('== per-map queen alive at end')
for mp in maps:
    s=f'{mp[:18]:18}'
    for T in TEAMS:
        R=[r for r in rows if r['team']==T and r['map']==mp]
        s+=f"{sum(r['qdeath'] is None for r in R):>4}/{len(R):<4}" if R else '        -'
    print(s)
print('== openings: units r25 / total r25 / splits r10 / queen first split, per map (median)')
for mp in maps:
    s=f'{mp[:18]:18}'
    for T in TEAMS:
        R=[r for r in rows if r['team']==T and r['map']==mp]
        s+=f" {med([r['units'][25] for r in R])}/{med([r['tot'][50] for r in R])}/{med([r['q_firstsplit'] for r in R])}" if R else ' -'
    print(s)
