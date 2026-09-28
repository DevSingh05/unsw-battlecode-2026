import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
ours=[g for g in pickle.load(open(S+'qos.pkl','rb')) if g['src'] in ('v7','ch5','ch6','ch8')]
top=pickle.load(open(S+'qos_top.pkl','rb'))
PK=[(4,20),(5,31),(6,33),(7,33),(10,33),(11,33),(12,3),(12,12),(12,22),(12,31),(13,1),(14,1),(17,1),(18,1),(19,3),(20,14)]
def run(items,label):
    D=collections.Counter(); E=collections.Counter(); DL=0; EE=0; n=len(items)
    for G,side in items:
        for d in G['deaths']:
            if d['team']==side and tuple(d['head']) in PK: D[tuple(d['head'])]+=1; DL+=d['len']
        for e in G['eats']:
            if e['team']==side and tuple(e['tile']) in PK: E[tuple(e['tile'])]+=1
    print(label,'pocket deaths/game %.1f (len %.1f) pocket eats/game %.1f'%(sum(D.values())/n,DL/n,sum(E.values())/n))
    print('   ',{k:'%.1f'%(v/n) for k,v in D.most_common(8)})
run([(g['G'],g['side']) for g in ours],'US all')
run([(g['G'],g['winner']) for g in top],'TOP W')
run([(g['G'],'A' if g['winner']=='B' else 'B') for g in top],'TOP L')
