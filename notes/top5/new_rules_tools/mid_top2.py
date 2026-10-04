"""Mid-game economy, us vs VIB/FTM/SSS: per 100-round window, per side: fresh / own-corpse / enemy-corpse eats, eats in enemy half,
mass lost by death reason (sum of length), h2h trades by length class, heads in enemy half. Uses rows_top2 for side mapping."""
import sys,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top2.pkl','rb'))
US=('v55','v60','v44b')
OPP=sys.argv[1] if len(sys.argv)>1 else 'VIB'
VER=tuple(sys.argv[2].split(',')) if len(sys.argv)>2 else ('v55','v60')
W=[(0,100),(100,200),(200,300),(300,400),(400,501)]
A=collections.defaultdict(lambda:collections.Counter()); n=0
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in US]; o=[r for r in rs if r['team']==OPP]
    if not u or not o or u[0]['team'] not in VER: continue
    if OPP=='VIB' and u[0]['at']>='2026-10-03T17:08:30': continue
    u=u[0]
    SM={'Autarky','Devil','Queen Of Spades','Tower Defense','Prisoners Dilemma','weakhold','Default','Trophy','Trauma','Schooltime'}
    MC=sys.argv[3] if len(sys.argv)>3 else 'all'
    if MC!='all' and (('small' if u['map'] in SM else 'big')!=MC): continue
    g=sim2.simulate(RD+f'{gid}.replay'); m=g['map']; rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end'] and rd[last][t]['ids'].get(g['team'] and [0,1][0],None) is not None or True]
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    n+=1
    T=T[0]; E='B' if T=='A' else 'A'; side={T:'us',E:OPP}
    q={g['team'][0]:0,g['team'][1]:1}
    sp={T:m.dragons[q[T]][1][0],E:m.dragons[q[E]][1][0]}
    def wi(r):
        for i,(a,b) in enumerate(W):
            if a<=r<b: return i
        return 4
    for e in g['eats']:
        s=side[e['team']]; w=wi(e['round']); en='B' if e['team']=='A' else 'A'
        src='fresh' if not e['corpse'] else ('ownC' if e['corpse'][1]==e['team'] else 'enC')
        A[(s,w)][src]+=1
        if m.dist(e['tile'],sp[en])<m.dist(e['tile'],sp[e['team']]): A[(s,w)]['eat_enhalf']+=1
    for x in g['deaths']:
        s=side[x['team']]; w=wi(x['round'])
        r=x['reason']
        if r=='HitHeadToHead':
            other=x.get('killer_team') or x.get('victim_team')
            r='h2h_en' if other and other!=x['team'] else 'h2h_ally'
        elif r=='HitOtherBody':
            r='body_en' if x['hit'] and x['hit']['team']!=x['team'] else 'body_ally'
        A[(s,w)]['massL_'+r]+=x['len']; A[(s,w)]['n_'+r]+=1
    for rnd,snap in g['rounds']:
        if rnd%10: continue
        w=wi(rnd)
        for j,(h,L,t) in snap['heads'].items():
            en='B' if t=='A' else 'A'
            if m.dist(h,sp[en])<m.dist(h,sp[t]): A[(side[t],w)]['heads_enhalf_x10']+=1
        for t in 'AB': A[(side[t],w)]['snaps']+=1
print(OPP,VER,'games',n)
keys=['fresh','ownC','enC','eat_enhalf','massL_h2h_en','n_h2h_en','massL_HitSelf','massL_NoValidAction','massL_body_en','massL_body_ally','massL_h2h_ally','massL_HitWall','heads_enhalf_x10']
for s in ('us',OPP):
    print(s)
    for w in range(5):
        c=A[(s,w)]; sn=max(1,c['snaps'])
        print(f"  r{W[w][0]}-{W[w][1]}: "+' '.join(f"{k}={round(c[k]/n,1) if k!='heads_enhalf_x10' else round(c[k]/sn,1)}" for k in keys))
