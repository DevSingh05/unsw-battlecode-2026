"""Per map: our result vs VIB/FTM (v55+v60 and v44b), end reason, queen alive; plus top teams' elimination share per map."""
import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
rows=[r for v in pickle.load(open(S+'rows_top2.pkl','rb')).values() for r in v]
US=('v44b','v55','v60','v49')
T=collections.defaultdict(list)
for r in rows:
    if r['team'] in US and r['opp'] in ('VIB','FTM','SSS'):
        if r['opp']=='VIB' and r['at']>='2026-10-03T17:08:30': continue
        T[r['map']].append(r)
print('map | n | our W | elim W/L | r500 W/L | our q alive | their q alive | by opp(ver)')
for m,R in sorted(T.items()):
    el=[r for r in R if r['reason']!='roundLimit']; r5=[r for r in R if r['reason']=='roundLimit']
    bo=collections.defaultdict(lambda:[0,0])
    for r in R: bo[r['opp']+'/'+r['team']][0]+=r['win']; bo[r['opp']+'/'+r['team']][1]+=1
    print(f"{m} | {len(R)} | {sum(r['win'] for r in R)} | {sum(r['win'] for r in el)}/{len(el)-sum(r['win'] for r in el)} | {sum(r['win'] for r in r5)}/{len(r5)-sum(r['win'] for r in r5)} | {sum(r['qdeath'] is None for r in R)} | {sum(r['eqlen_end']>0 for r in R)} | "+' '.join(f"{k}:{a}/{b}" for k,(a,b) in sorted(bo.items())))
# loss classification
C=collections.Counter()
for m,R in T.items():
    for r in R:
        if r['win']: continue
        if r['reason']!='roundLimit': C[('elim',r['opp'])]+=1
        elif r['qlen_end']!=r['eqlen_end']: C[('queen',r['opp'])]+=1
        else: C[('longest',r['opp'])]+=1
print('loss classes',sorted(C.items()))
