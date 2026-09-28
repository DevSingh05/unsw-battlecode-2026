# Per-game timeline for our Slithery games. usage: an.py [gid...]
import os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
from collections import Counter
meta=pickle.load(open('notes/tools/slithery/meta.pkl','rb'))
def A(p,side): return tuple(p) if side=='A' else (62-p[0],26-p[1])
sel=sys.argv[1:]
for d,gid,opp,win,side in meta:
    if sel and str(gid) not in sel and d not in sel: continue
    them='B' if side=='A' else 'A'
    G=simulate('replays/%s/%d.replay'%(d,gid)); m=G['map']
    hot={t for t,g in m.tiles.items() if g==(1,1)}
    fast={t for t,g in m.tiles.items() if g[1]<=10}
    Rr=dict(G['rounds'])
    line=[]
    for r in [50,100,150,200,250,300,350,400,450,499]:
        s=Rr.get(r) or Rr[max(Rr)]
        line.append('%d:%d/%d|%d/%d'%(r,s[side]['n'],s[them]['n'],s[side]['max'],s[them]['max']))
    he=Counter(e['team'] for e in G['eats'] if e['tile'] in hot)
    fe=Counter(e['team'] for e in G['eats'] if e['tile'] in fast and not e['corpse'])
    ce=Counter(e['team'] for e in G['eats'] if e['corpse'])
    big=[(x['round'],x['len'],x['reason'][:8],A(x['head'],side),('K%d'%x['killer_len']) if x.get('killer_team') and x['killer_team']!=x['team'] else ('ally%d'%x['killer_len'] if x.get('killer_team') else ''), (x['hit']['team']+str(x['hit']['len'])) if x.get('hit') else '') for x in G['deaths'] if x['team']==side and x['len']>=10]
    bigT=[(x['round'],x['len'],x['reason'][:8],A(x['head'],side)) for x in G['deaths'] if x['team']==them and x['len']>=10]
    print('==',d,gid,opp,'WIN' if win else 'LOSS','side',side,'final us',G['result'][side],'them',G['result'][them])
    print('  n/max:', ' '.join(line))
    print('  hot11 eats us/them',he[side],he[them],' fast(<=10) spawn eats',fe[side],fe[them],' corpse eats',ce[side],ce[them])
    print('  our L>=10 deaths',big)
    print('  their L>=10 deaths',bigT)
