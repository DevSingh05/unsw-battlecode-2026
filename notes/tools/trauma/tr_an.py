import json,glob,os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
from collections import Counter
meta=pickle.load(open('/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/trauma/meta.pkl','rb'))
HOT={(35,9),(36,9),(11,10),(36,10),(11,11),(36,11),(11,12),(36,12),(11,13),(36,13),(11,14),(12,14)}
sel=sys.argv[1:] 
for d,gid,opp,win,side in meta:
    if sel and str(gid) not in sel: continue
    side=side or 'A'
    them='B' if side=='A' else 'A'
    G=simulate('replays/%s/%d.replay'%(d,gid))
    R=dict(G['rounds'])
    line=[]
    for r in [50,100,150,200,250,300,350,400,450,499]:
        s=R.get(r) or R[max(R)]
        line.append('%d:%d/%d|%d/%d'%(r,s[side]['n'],s[them]['n'],s[side]['max'],s[them]['max']))
    he=Counter(e['team'] for e in G['eats'] if e['tile'] in HOT)
    ce=Counter(e['team'] for e in G['eats'] if e['corpse'])
    se=Counter(e['team'] for e in G['eats'] if not e['corpse'])
    big=[(x['round'],x['len'],x['reason'],x['head'],'k' if x.get('killer_team') and x.get('killer_team')!=x['team'] else '', x.get('hit',{}) and x['hit']['team'] if x.get('hit') else '') for x in G['deaths'] if x['team']==side and x['len']>=8]
    bigT=[(x['round'],x['len'],x['reason'],x['head']) for x in G['deaths'] if x['team']==them and x['len']>=8]
    print('==',d,gid,opp,'WIN' if win else 'LOSS','us',side, 'final',G['result'][side],'them',G['result'][them])
    print('  units/max:', ' '.join(line))
    print('  hot eats us/them',he[side],he[them],' spawn eats',se[side],se[them],' corpse eats',ce[side],ce[them])
    print('  our big deaths',big)
    print('  their big deaths',bigT)
    dc=Counter((x['reason']) for x in G['deaths'] if x['team']==side)
    print('  our deaths by reason',dict(dc), 'their',dict(Counter(x['reason'] for x in G['deaths'] if x['team']==them)))
