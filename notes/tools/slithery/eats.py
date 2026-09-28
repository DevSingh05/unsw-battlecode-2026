# Eats by zone (own frame) per team: top games (winner/loser) and our games (us/them). usage: eats.py top|ours [dirs]
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
agg=defaultdict(Counter); n=Counter()
def run(path,labels):
    G=simulate(path)
    for T,lab in labels.items():
        c=Counter()
        for e in G['eats']:
            if e['team']!=T: continue
            if e['corpse']: c['corpse_own' if e['corpse'][1]==T else 'corpse_enemy']+=1
            else: c[zone(A(e['tile'],T))]+=1
        agg[lab].update(c); n[lab]+=1
    return G
if mode=='top':
    for p,gid,win,a,b in top_games():
        run(p,{win:'winner','B' if win=='A' else 'A':'loser'})
else:
    meta=pickle.load(open('notes/tools/slithery/meta.pkl','rb'))
    for d,gid,opp,win,side in meta:
        if sel and d not in sel: continue
        o='B' if side=='A' else 'A'
        run('replays/%s/%d.replay'%(d,gid),{side:'us_'+('W' if win else 'L'),o:'them_'+('L' if win else 'W')})
keys=sorted({k for c in agg.values() for k in c})
print('%-12s'%'zone'+''.join('%12s'%l for l in agg))
for k in keys: print('%-12s'%k+''.join('%12.1f'%(agg[l][k]/n[l]) for l in agg))
print('games',dict(n))
