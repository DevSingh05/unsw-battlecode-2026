"""Small maps vs FTM: r<=150 head-on outcomes, where (half), killer/victim lengths, killer steps; FTM unit positions in our half."""
import sys,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top1.pkl','rb'))
SM={'Autarky','Devil','Queen Of Spades','Tower Defense','Prisoners Dilemma','weakhold','Default','Trophy','Trauma','Schooltime'}
C=collections.Counter(); KL=collections.Counter(); inv=collections.defaultdict(list); n=0
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team']!='FTM'][0]; f=[r for r in rs if r['team']=='FTM'][0]
    if u['team'] not in ('v44','v49','v43') or u['map'] not in SM: continue
    g=sim2.simulate(RD+f'{gid}.replay'); m=g['map']; n+=1
    rd=dict(g['rounds']); last=g['last_round']
    # identify our letter by final totals
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]; E='B' if T=='A' else 'A'
    q={g['team'][0]:0,g['team'][1]:1}; so=m.dragons[q[T]][1][0]; se=m.dragons[q[E]][1][0]
    half=lambda p: 'ourhalf' if m.dist(p,so)<m.dist(p,se) else ('theirhalf' if m.dist(p,so)>m.dist(p,se) else 'mid')
    for x in g['deaths']:
        if x['round']>150 or x['reason']!='HitHeadToHead': continue
        # count each kill once from the victim (non-actor) record
        if 'killer' not in x: continue
        side='FTM kills ours' if x['team']==T else 'we kill FTM'
        a=[a for a in g['moves'] if a['id']==x['killer'] and a['round']==x['round']]
        st_=a[0]['steps'] if a else None
        C[(side,half(x['head']))]+=1; KL[(side,x['killer_len'],x['len'],st_)]+=1
    for k in (50,75,100):
        s=rd.get(k)
        if s: inv[k].append((sum(1 for j,v in s['heads'].items() if v[2]==E and half(v[0])=='ourhalf'),sum(1 for j,v in s['heads'].items() if v[2]==T and half(v[0])=='theirhalf')))
print('games',n)
print('r<=150 head-on kills (victim not mover) by side x half:',sorted(C.items()))
print('top (side,killerL,victimL,steps):',KL.most_common(14))
for k,v in inv.items(): print(f'r{k}: FTM heads in our half mean {round(st.mean(a for a,b in v),1)} | our heads in their half {round(st.mean(b for a,b in v),1)}')
# corpse economics r<=150 on small maps
CE=collections.Counter()
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team']!='FTM'][0]
    if u['team'] not in ('v44','v49','v43') or u['map'] not in SM: continue
    g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]
    for e in g['eats']:
        if e['round']>150: continue
        who='us' if e['team']==T else 'FTM'
        src='fresh' if not e['corpse'] else ('own corpse' if e['corpse'][1]==e['team'] else 'enemy corpse')
        CE[(who,src)]+=1
    for x in g['deaths']:
        if x['round']<=150: CE[('us' if x['team']==T else 'FTM','deaths:'+x['reason'][:7])]+=1
print('r<=150 eats/deaths totals over games:',sorted(CE.items()))
