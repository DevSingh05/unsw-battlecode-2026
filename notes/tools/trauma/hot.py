import json,sys,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
from collections import Counter,defaultdict
HOT={(35,9),(36,9),(11,10),(36,10),(11,11),(36,11),(11,12),(36,12),(11,13),(36,13),(11,14),(12,14)}
CORA={(11,8),(11,9)}|{h for h in HOT if h[0]<24}
CORB={(36,15),(36,14)}|{h for h in HOT if h[0]>24}
path,T=sys.argv[1],sys.argv[2]
G=simulate(path)
cor=CORA if T=='A' else CORB
ot=CORB if T=='A' else CORA
eats=[e for e in G['eats'] if e['team']==T and e['tile'] in HOT]
print('hot eats',len(eats),'own corridor',sum(e['tile'] in cor for e in eats),'enemy corridor',sum(e['tile'] in ot for e in eats))
byd=Counter(e['id'] for e in eats); print('eaters',byd.most_common(8))
lens=Counter(min(e['len'],12) for e in eats); print('eater len',sorted(lens.items()))
per50=Counter(e['round']//50*50 for e in eats); print('per50',sorted(per50.items()))
d=[x for x in G['deaths'] if x['team']==T and x['head'] in cor|{(12,8),(35,15)}]
print('deaths in corridor',len(d), Counter((x['reason'],min(x['len'],9)) for x in d).most_common(6))
sp=[s for s in G['splits'] if s['team']==T]
# splits whose parent head in corridor
print('splits total',len(sp))
