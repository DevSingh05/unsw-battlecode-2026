# Detail of our L>=MINL deaths: move, neighbours, king/ally/enemy context. usage: bigdeath.py MINL [gid|dir ...]
import os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
meta=pickle.load(open('notes/tools/slithery/meta.pkl','rb'))
MINL=int(sys.argv[1]); sel=sys.argv[2:]
def A(p,side): return tuple(p) if side=='A' else (62-p[0],26-p[1])
for d,gid,opp,win,side in meta:
    if sel and str(gid) not in sel and d not in sel: continue
    G=simulate('replays/%s/%d.replay'%(d,gid))
    for x in G['deaths']:
        if x['team']!=side or x['len']<MINL: continue
        # was it the team's longest at death?
        lens=sorted([len(G['body'][j]) for j in []])
        print(d,gid,'WIN' if win else 'LOSS','r%d L%d'%(x['round'],x['len']),x['reason'],'head',A(x['head'],side),'move',x.get('move'),'nbrs',x.get('nbrs'),'king(id,L,d)',x.get('king'),'enemy',x.get('enemy_near'),'killer',x.get('killer_len'),x.get('killer_team'))
