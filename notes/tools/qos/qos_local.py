import pickle,collections,glob,sys
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def inroom(p): return 6<=p[0]<=11 and 31<=p[1]<=33
T={((4,3),(8,33)):'in1',((3,3),(9,33)):'in2',((8,33),(4,3)):'out1',((9,33),(3,3)):'out2'}
C=collections.Counter(); n=0
for f in sorted(glob.glob(S+'qreps/*.replay')):
    G=simulate(f); n+=2
    for side in 'AB':
        last={}
        for m in G['moves']:
            if m['round']>=150 or m['team']!=side: continue
            p=canon(m['head'],side); i=m['id']
            if i in last and (last[i],p) in T: C[T[(last[i],p)]]+=1
            last[i]=p
        for d in G['deaths']:
            if d['team']==side and d['round']<150:
                C['death_room' if inroom(canon(d['head'],side)) else 'death_else']+=1
        for e in G['eats']:
            if e['team']==side and e['round']<150 and not e['corpse']:
                C['spawn_eat_room' if inroom(canon(e['tile'],side)) else ('spawn_eat_opproom' if inroom(canon(e['tile'],'B' if side=='A' else 'A')) else 'spawn_eat_open')]+=1
print('per team-game r0-150', {k:'%.1f'%(v/n) for k,v in sorted(C.items())})
