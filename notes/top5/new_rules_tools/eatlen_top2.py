"""r100-300 eats by eater length class and source; us vs OPP."""
import sys,pickle,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top2.pkl','rb'))
US=('v55','v60'); OPP=sys.argv[1]
C=collections.defaultdict(collections.Counter); n=0
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in US]; o=[r for r in rs if r['team']==OPP]
    if not u or not o: continue
    if OPP=='VIB' and u[0]['at']>='2026-10-03T17:08:30': continue
    u=u[0]; g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]; n+=1
    for e in g['eats']:
        if not (100<=e['round']<300) or e['len'] is None: continue
        L=e['len']; lc='L2-3' if L<=3 else 'L4-7' if L<=7 else 'L8-15' if L<=15 else 'L16+'
        if e['id'] in (0,1): lc='Q'+lc
        src='fresh' if not e['corpse'] else ('ownC' if e['corpse'][1]==e['team'] else 'enC')
        C['us' if e['team']==T else OPP][(lc,src)]+=1
print(OPP,'games',n)
for s,c in C.items():
    print(s,{f"{a}/{b}":round(v/n,1) for (a,b),v in sorted(c.items())})
