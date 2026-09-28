"""usage: weakmap_report.py "Queen Of Spades" Trauma ...  (reads replays/v7/weakmap.pkl from weakmap_diag.py)"""
import pickle, collections, sys
D=pickle.load(open('/Users/devsingh/Developer/UNSW_Battlecode/replays/v7/weakmap.pkl','rb'))
RS=[25,50,100,150,200,250,300,350,400,450,499]
def mean(xs):
    xs=[x for x in xs if x is not None]; return sum(xs)/len(xs) if xs else float('nan')
CATS=['our_ram','rammed_by_enemy','h2h_friendly','body_ally','body_enemy','body_unknown','self_trap','self_neck','wall','NoValidAction','feed','stub']
for mp in sys.argv[1:]:
    G=[r for r in D.values() if r['map']==mp]
    print('='*20,mp,len(G))
    for r in sorted(G,key=lambda r:r['win']):
        res=r['res']; us=r['us']; th=r['them']
        print(f"{r['id']} {'W' if r['win'] else 'L'} {r['opp'][:14]:14} {r['oppElo']} {'R' if r['ranked'] else 'u'} end={res['endReason'][:8]} r{r['last']} final us n{us['n'][499]} max{us['max'][499]} vs n{th['n'][499]} max{th['max'][499]}")
    for grp,sel in (('LOSS',[r for r in G if not r['win']]),('WIN',[r for r in G if r['win']])):
        print('--',grp,len(sel))
        for k in ('us','them'):
            print(' ',k,'n   ',' '.join(f"{mean([r[k]['n'][x] for r in sel]):5.1f}" for x in RS))
            print(' ',k,'max ',' '.join(f"{mean([r[k]['max'][x] for r in sel]):5.1f}" for x in RS))
            print(' ',k,'2nd ',' '.join(f"{mean([r[k]['second'][x] for r in sel]):5.1f}" for x in RS))
        for k in ('us','them'):
            E=collections.Counter(); C=collections.Counter(); F=collections.Counter(); S=collections.Counter(); DR=collections.Counter()
            for r in sel:
                E.update(r[k]['eats']); C.update(r[k]['cause']); F.update(r[k]['feed']); S.update(r[k].get('splits',{})); DR.update(r[k]['dr'])
            n=len(sel)
            print(f"  {k} eats/g all {E['all']/n:.0f} spawn {E['spawn']/n:.0f} hot {E['hot']/n:.0f} corpse own {E['corpse_own']/n:.0f} enemy {E['corpse_enemy']/n:.0f} kingEats>=250 {E['king_eats_250']/n:.0f} | per dr b0 {E['b0']/max(1,DR[0]):.3f} b1 {E['b1']/max(1,DR[1]):.3f} b2 {E['b2']/max(1,DR[2]):.3f}")
            print(f"  {k} deaths/g "+' '.join(f"{c}={C[c]/n:.1f}" for c in CATS))
            print(f"  {k} lenlost/g "+' '.join(f"{c}={C['len_lost_'+c]/n:.0f}" for c in CATS if C['len_lost_'+c]))
            print(f"  {k} feed/g n={F['n']/n:.1f} dropped={F['dropped']/n:.0f} eaten={F['eaten']/n:.0f} king={F['king']/n:.0f} ally={F['ally']/n:.0f} enemy={F['enemy']/n:.0f} | splits {S['n']/n:.0f} b0 {S['b0']/n:.0f} b1 {S['b1']/n:.0f} b2 {S['b2']/n:.0f} noexit {S['noexit']/n:.0f}")
