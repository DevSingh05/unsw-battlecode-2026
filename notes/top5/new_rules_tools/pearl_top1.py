"""Fresh-pearl latency: rounds between a non-corpse pearl appearing and being eaten, by eater team; share of pearls eaten within 0/1/3 rounds.
Also unclaimed share. Small vs big maps, us vs FTM (games vs us)."""
import sys,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top1.pkl','rb'))
SM={'Autarky','Devil','Queen Of Spades','Tower Defense','Prisoners Dilemma','weakhold','Default','Trophy','Trauma','Schooltime'}
R=collections.defaultdict(list)
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team']!='FTM'][0]
    if u['team'] not in ('v44','v49','v43'): continue
    g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]; cls='small' if u['map'] in SM else 'big'
    spawn={}
    for rnd,tile,isc in g['appears']:
        if not isc: spawn[tile]=rnd
    for e in g['eats']:
        if e['corpse'] or e['round']>200: continue
        s=spawn.get(e['tile'])
        if s is None or s>e['round']: continue
        R[(cls,'us' if e['team']==T else 'FTM')].append(e['round']-s)
for k,v in sorted(R.items()):
    print(k,len(v),'median wait',st.median(v),' <=1:',round(sum(x<=1 for x in v)/len(v),2),' <=3:',round(sum(x<=3 for x in v)/len(v),2))
