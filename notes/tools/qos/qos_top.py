import json,pickle,sys,os
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
res=[]
for d in ['permap','kings']:
    for g in json.load(open('notes/replays/%s/index.json'%d)):
        if g['mapName']!='Queen Of Spades': continue
        p='notes/replays/%s/%d.replay'%(d,g['id'])
        if not os.path.exists(p): print('missing',p); continue
        G=simulate(p); G['map']=None
        res.append(dict(id=g['id'],a=g['a']['name'],b=g['b']['name'],winner=g['winner'].upper(),G=G))
        print(g['id'],g['a']['name'],g['b']['name'],g['winner'],G['result']['endReason'],G['last_round'])
pickle.dump(res,open(S+'qos_top.pkl','wb'))
