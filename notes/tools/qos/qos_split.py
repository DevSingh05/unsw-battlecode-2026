import pickle,collections,sys
sys.path.insert(0,'notes/tools')
import replay_decode as R
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
ours=[g for g in pickle.load(open(S+'qos.pkl','rb')) if g['src'] in ('v7','ch5','ch6','ch8')]
top=pickle.load(open(S+'qos_top.pkl','rb'))
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
# child head tile distribution via split events: need childBody; replay_sim doesn't keep it -> reload events
def splits(path):
    o=R.load(path); res=[]
    for e in o['events']:
        if e['t']=='dragonSplit': res.append((e['child'],tuple(e['childBody'][0]),e['team']))
    return res
def run(items,label):
    C=collections.Counter(); Dd=collections.Counter(); n=len(items); tot=0
    for path,G,side in items:
        dage={d['id']:(d['age'],d['reason']) for d in G['deaths']}
        for c,h,team in splits(path):
            if team!=side: continue
            tot+=1
            p=canon(h,side)
            zone='door' if p in [(4,3),(3,3),(8,33),(9,33)] else 'room' if (6<=p[0]<=11 and 31<=p[1]<=33) else 'other'
            C[zone]+=1
            a=dage.get(c)
            if a and a[0]<=3: Dd[zone]+=1
    print(label,'splits/game %.1f'%(tot/n),'child-head zone/game',{k:'%.1f'%(v/n) for k,v in C.items()},'dead within 3 rounds',{k:'%.1f'%(v/n) for k,v in Dd.items()})
ci=[]
for g in ours:
    ci.append(('replays/%s/%d.replay'%(g['src'],g['id']),g['G'],g['side']))
run(ci,'US')
ti=[]
import os
for g in top:
    p='notes/replays/permap/%d.replay'%g['id']
    if not os.path.exists(p): p='notes/replays/kings/%d.replay'%g['id']
    ti.append((p,g['G'],g['winner']))
run(ti,'TOPW')
