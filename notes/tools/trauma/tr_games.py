import json,glob,os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
games=[]
for g in json.load(open('replays/v7/ledger.json')):
    if g['map']=='Trauma': games.append(('v7',g['game'],g['opp'],g['win'],g['side'],'replays/v7/%d.replay'%g['game']))
for d in ['ch5','ch6','ch7','ch8','ch1','ch2','ch3']:
    for f in glob.glob('replays/%s/*.json'%d):
        s=json.load(open(f))
        if not isinstance(s,list): continue
        for g in s:
            if isinstance(g,dict) and g.get('map')=='Trauma':
                p='replays/%s/%d.replay'%(d,g['id'])
                if not os.path.exists(p): continue
                games.append((d,g['id'],g['opp'],g['win'],g.get('side'),p))
out=[]
for d,gid,opp,win,side,p in games:
    G=simulate(p)
    r=G['result']
    if side is None:
        # match via summary us
        side=None
    out.append((d,gid,opp,win,side,G))
pickle.dump([(a,b,c,dd,e) for a,b,c,dd,e,_ in out],open('/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/trauma/meta.pkl','wb'))
for d,gid,opp,win,side,G in out:
    print(d,gid,opp,win,side,G['result']['winner'],G['result']['endReason'],G['result']['A'],G['result']['B'])
