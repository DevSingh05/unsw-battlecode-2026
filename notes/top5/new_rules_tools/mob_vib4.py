"""Mobility/size mix r100-300 per side in our games vs OPP: unit length mix, steps per move, fresh eats per unit-turn, by length class."""
import sys,pickle,collections,math
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1_vib/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/vib4/'
D=pickle.load(open(S+'rows_vib4.pkl','rb'))
OPP=sys.argv[1]; VER=sys.argv[2].split(','); LO,HI=int(sys.argv[3]),int(sys.argv[4])
C=collections.defaultdict(collections.Counter); n=0
cls=lambda L:'L2' if L==2 else 'L3' if L==3 else 'L4' if L==4 else 'L5-8' if L<=8 else 'L9+'
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in VER]; o=[r for r in rs if r['team']==OPP]
    if not u or not o: continue
    u=u[0]
    g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    n+=1; T=T[0]; side=lambda t:'us' if t==T else OPP
    for a in g['moves']:
        if not (LO<=a['round']<HI): continue
        s=side(a['team']); c=cls(a['len_before'])
        C[s]['turns_'+c]+=1; C[s]['turns']+=1
        C[s]['steps_'+c]+=a['steps']
    for e in g['eats']:
        if LO<=e['round']<HI and not e['corpse'] and e['len']:
            C[side(e['team'])]['fresh_'+cls(e['len'])]+=1
print(OPP,VER,LO,HI,'games',n)
for s,c in C.items():
    t=c['turns']
    print(s,'unit-turns/game',round(t/n),' mix',{k:f"{round(100*c['turns_'+k]/t)}%" for k in ('L2','L3','L4','L5-8','L9+')},
          ' steps/turn',{k:round(c['steps_'+k]/max(1,c['turns_'+k]),2) for k in ('L2','L3','L4','L5-8','L9+')},
          ' fresh/100 turns',{k:round(100*c['fresh_'+k]/max(1,c['turns_'+k]),1) for k in ('L2','L3','L4','L5-8','L9+')},' fresh/game',{k:round(c['fresh_'+k]/n,1) for k in ('L2','L3','L4','L5-8','L9+')})
