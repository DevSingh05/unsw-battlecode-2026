# For our L>=12 deaths: dragon age vs length; born via big (k>=8) split? Trail incomplete if age < len (approx).
import sys
from common import *
from replay_sim import simulate
from collections import Counter
sel=sys.argv[1:]
C=Counter()
for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
    if sel and d not in sel: continue
    G=simulate('replays/%s/%d.replay'%(d,gid))
    bigborn={s['child']:s for s in G['splits'] if s['team']==side and s['k']>=8}
    for x in G['deaths']:
        if x['team']!=side or x['len']<12: continue
        nb=x.get('nbrs',{}); free=sum(1 for v in nb.values() if v in('free','pearl'))
        if x['reason']=='HitHeadToHead': c='ram'
        elif free==0: c='trapped'
        else: c='exit'
        rs=bigborn.get(x['id'])
        inc = rs is not None and x['age'] < x['len']
        C[(c,'bigsplit-child' if rs else 'normal', 'age<len' if inc else '')]+=1
for k,v in sorted(C.items()): print(k,v)
