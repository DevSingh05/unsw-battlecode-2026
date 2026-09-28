# Local replays: big-death classes + units/max timeline for side T. usage: localcls.py T replay...
import sys
from common import *
from replay_sim import simulate
from collections import Counter
T=sys.argv[1]
tot=Counter()
for p in sys.argv[2:]:
    G=simulate(p); o='B' if T=='A' else 'A'
    Rr=dict(G['rounds'])
    line=' '.join('%d:%d/%d|%d/%d'%(r,(Rr.get(r) or Rr[max(Rr)])[T]['n'],(Rr.get(r) or Rr[max(Rr)])[o]['n'],(Rr.get(r) or Rr[max(Rr)])[T]['max'],(Rr.get(r) or Rr[max(Rr)])[o]['max']) for r in (250,300,350,400,450,499))
    print(p.split('/')[-1],G['result']['winner'],G['result'][T],G['result'][o]); print('  ',line)
    for x in G['deaths']:
        if x['team']==T and x['len']>=12:
            nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
            c='rammed' if x['reason']=='HitHeadToHead' and x.get('killer_team') not in (None,T) else ('trapped' if free==0 else x['reason']+'_exit')
            tot[c]+=1
            print('    r%d L%d %s %s %s king=%s'%(x['round'],x['len'],c,A(x['head'],T),x.get('move'),x.get('king')))
print(tot)
