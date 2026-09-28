import collections,glob,sys,os
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
T={((4,3),(8,33)):'in1',((3,3),(9,33)):'in2',((8,33),(4,3)):'out1',((9,33),(3,3)):'out2'}
C=collections.defaultdict(collections.Counter); N=collections.Counter()
for f in sorted(glob.glob(S+sys.argv[1]+'/*.replay')):
    base=os.path.basename(f)[:-7]
    a,b=base.split('_vs_'); a=a.split('_',3)[-1] if False else a
    nameA='cand' if 'qbot' in a else 'opp'; nameB='cand' if 'qbot' in b else 'opp'
    if 'qbot' not in base: nameA,nameB='A','B'
    G=simulate(f)
    for side,nm in (('A',nameA),('B',nameB)):
        N[nm]+=1
        last={}
        for m in G['moves']:
            if m['round']>=150 or m['team']!=side: continue
            p=canon(m['head'],side); i=m['id']
            if i in last and (last[i],p) in T: C[nm][T[(last[i],p)]]+=1
            last[i]=p
        for d in G['deaths']:
            if d['team']!=side: continue
            p=canon(d['head'],d['team'])
            if p in [(4,3),(3,3),(8,33),(9,33)]: C[nm]['door_death_all']+=1
            if d['round']<150:
                C[nm]['death<150']+=1
                if 6<=p[0]<=11 and 31<=p[1]<=33: C[nm]['room_death<150']+=1
        for rr,s in G['rounds']:
            if rr==100: C[nm]['units@100']+=s[side]['n']
            if rr==200: C[nm]['units@200']+=s[side]['n']
        for e in G['eats']:
            if e['team']==side and e['round']<150 and not e['corpse']: C[nm]['spawn_eats<150']+=1
for nm in C:
    print(nm,N[nm],{k:'%.1f'%(v/N[nm]) for k,v in sorted(C[nm].items())})
