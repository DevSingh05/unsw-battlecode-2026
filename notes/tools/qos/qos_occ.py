import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
res=pickle.load(open(S+'qos_top.pkl','rb')); ours=pickle.load(open(S+'qos.pkl','rb'))
ours=[g for g in ours if g['src'] in ('v7','ch5','ch6','ch8')]
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def inroom(p): return 6<=p[0]<=11 and 31<=p[1]<=33
def inopp(p): return 13<=p[0]<=18 and 1<=p[1]<=3
def occ(G,side,T0,T1):
    per=collections.defaultdict(set); perL=collections.defaultdict(list); opp=collections.defaultdict(set)
    for m in G['moves']:
        if m['team']!=side or not(T0<=m['round']<T1): continue
        p=canon(m['head'],side)
        if inroom(p): per[m['round']].add(m['id']); perL[m['round']].append(m['len_before'])
        if inopp(p): opp[m['round']].add(m['id'])
    hist=collections.Counter(len(per[r]) for r in range(T0,T1))
    return hist, sum(len(opp[r]) for r in range(T0,T1))/(T1-T0), [l for r in perL for l in perL[r]]
def summ(label,items):
    H_=collections.Counter(); oo=0; Ls=collections.Counter()
    for G,side in items:
        h,o,ls=occ(G,side,0,150); H_.update(h); oo+=o; Ls.update(ls)
    tot=sum(H_.values())
    print(label,len(items),'room occupancy r0-150 (share of rounds with k own heads in own room):',{k:'%.2f'%(v/tot) for k,v in sorted(H_.items())},'mean opp-room heads %.2f'%(oo/len(items)))
    lt=sum(Ls.values()); print('   len of dragons in own room', {k:'%.2f'%(v/lt) for k,v in sorted(Ls.items())})
summ('TOP winners',[(g['G'],g['winner']) for g in res])
summ('TOP losers',[(g['G'],'A' if g['winner']=='B' else 'B') for g in res])
summ('US in losses',[(g['G'],g['side']) for g in ours if not g['win']])
summ('US in wins',[(g['G'],g['side']) for g in ours if g['win']])
summ('THEM when we lose',[(g['G'],'B' if g['side']=='A' else 'A') for g in ours if not g['win']])
