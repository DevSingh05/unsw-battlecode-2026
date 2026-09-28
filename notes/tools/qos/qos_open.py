import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
res=pickle.load(open(S+'qos_top.pkl','rb')); ours=pickle.load(open(S+'qos.pkl','rb'))
ours=[g for g in ours if g['src'] in ('v7','ch5','ch6','ch8')]
W,H=25,35
def canon(p,side):
    x,y=p
    return (x,y) if side=='A' else (W-1-x,H-1-y)
def z(p):
    x,y=p
    if 6<=x<=11 and 31<=y<=33: return 'R'
    if 13<=x<=18 and 1<=y<=3: return 'X'
    return '.'
def opening(G,side,label):
    # path of initial dragons (ids with team side among 0..3) for first 40 rounds
    ids=sorted(set(m['id'] for m in G['moves'] if m['team']==side and m['id']<4))
    s=label+' '
    for i in ids:
        path=[(m['round'],canon(m['head'],side)) for m in G['moves'] if m['id']==i and m['round']<=40]
        ent=[r for r,p in path if z(p)!='.']
        s+=' id%d: first room r%s %s end %s;'%(i, ent[0] if ent else '-', z(path[ent and 0 or 0][1]) if not ent else z(dict(path)[ent[0]]), path[-1] if path else None)
    # splits first 40 rounds: rounds
    sp=[(s_['round'],s_['L']) for s_ in G['splits'] if s_['team']==side and s_['round']<=40]
    ea=sum(1 for e in G['eats'] if e['team']==side and e['round']<=40)
    s+=' splits<=40: %d eats<=40: %d'%(len(sp),ea)
    print(s)
for g in res[:21]:
    opening(g['G'],g['winner'],'TOPW %d'%g['id'])
for g in ours[:12]:
    opening(g['G'],g['side'],'US%s %d'%('W' if g['win'] else 'L',g['id']))
