# Classify our L>=MINL deaths across game sets. usage: deaths.py MINL dirs...
import os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
from collections import Counter
meta=pickle.load(open('notes/tools/slithery/meta.pkl','rb'))
MINL=int(sys.argv[1]); sel=sys.argv[2:]
BOX={(57,13),(58,13),(57,14),(58,14),(4,12),(5,12),(4,13),(5,13)}
def A(p,side): return tuple(p) if side=='A' else (62-p[0],26-p[1])
cls=Counter(); clsW=Counter(); rows=[]
for d,gid,opp,win,side in meta:
    if sel and d not in sel: continue
    G=simulate('replays/%s/%d.replay'%(d,gid))
    for x in G['deaths']:
        if x['team']!=side or x['len']<MINL: continue
        h=A(x['head'],side); nb=x.get('nbrs',{})
        free=sum(1 for v in nb.values() if v in ('free','pearl'))
        kingL=x.get('king',(0,0,99))[1]
        if x['reason']=='HitHeadToHead' and x.get('killer_team') and x['killer_team']!=x['team']: c='rammed_by_enemy'
        elif x['reason']=='HitHeadToHead' and x.get('victim_team') and x['victim_team']!=x['team']: c='rammed_enemy(mover)'
        elif x['reason']=='HitHeadToHead': c='headon_ally'
        elif h in BOX: c='portal_box'
        elif x['reason'] in('HitSelf','NoValidAction','HitWall') and free==0: c='self_trapped'
        elif x['reason']=='HitSelf' and kingL>x['len'] and x.get('king',(0,0,99))[2]<=4: c='merge_into_bigger'
        elif x['reason']=='HitSelf': c='hitself_with_exit'
        elif x['reason']=='HitOtherBody': c='hit_body_'+(x['hit']['team']==x['team'] and 'ally' or 'enemy' if x.get('hit') else '?')
        else: c=x['reason']
        cls[c]+=1
        if not win: clsW[c]+=1
        rows.append((d,gid,'W' if win else 'L',x['round'],x['len'],c,h,kingL))
for r in rows: print(r)
print('all',cls.most_common()); print('in losses',clsW.most_common())
