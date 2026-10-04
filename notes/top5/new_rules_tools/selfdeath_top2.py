"""Our self-inflicted deaths r100-300 (HitSelf / HitOtherBody ally) vs VIB's NoValidAction: length, age, nearest ally, king dist, corpse recovery."""
import sys,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top2.pkl','rb'))
US=('v55','v60','v44b'); OPP=sys.argv[1]
C=collections.defaultdict(collections.Counter); n=0
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in US]; o=[r for r in rs if r['team']==OPP]
    if not u or not o: continue
    if OPP=='VIB' and u[0]['at']>='2026-10-03T17:08:30': continue
    u=u[0]; g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    n+=1; T=T[0]
    # corpse tiles -> who ate (team) within 10 rounds
    eatby={}
    for e in g['eats']:
        if e['corpse']: eatby.setdefault((e['corpse'][0],e['tile']),(e['team'],e['round']-e['corpse'][2],e['len']))
    for x in g['deaths']:
        if not (100<=x['round']<300): continue
        who='us' if x['team']==T else OPP
        r=x['reason']
        if r=='HitOtherBody': r='body_'+('ally' if x['hit'] and x['hit']['team']==x['team'] else 'en')
        if r not in ('HitSelf','body_ally','NoValidAction'): continue
        c=C[(who,r)]; c['n']+=1; c['L%d'%min(x['len'],6)]+=1
        c['mass']+=x['len']
        k=x.get('king'); 
        if k: c['kingd<=3']+= k[2]<=3; c['kingLen>=10_and_d<=3']+= (k[2]<=3 and k[1]>=10)
        an=x.get('ally_near')
        if an: c['ally<=2']+= an[2]<=2
        tiles=x['body'][::2]
        for t in tiles:
            c['drops']+=1
            ev=eatby.get((x['id'],t))
            if ev:
                if ev[0]==x['team']: c['rec_own']+=1; c['rec_own_fast']+= ev[1]<=5
                else: c['rec_enemy']+=1
print(OPP,'games',n)
for k,c in sorted(C.items()):
    print(k,{kk:round(v/n,1) for kk,v in sorted(c.items())})
