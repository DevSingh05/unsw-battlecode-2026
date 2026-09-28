import json,os,sys,pickle
sys.path.insert(0,'notes/tools')
from replay_sim import simulate
games=[]
l=json.load(open('replays/v7/ledger.json'))
for g in l:
    if g['map']=='Queen Of Spades': games.append(('v7',g['game'],g['opp'],g['win'],g['side']))
for d in ['ch1','ch2','ch3','ch5','ch6','ch8']:
    for g in json.load(open('replays/%s/summary.json'%d)):
        if g['map']!='Queen Of Spades': continue
        games.append((d,g['id'],g['opp'],g['win'],g.get('side') or ('us',g['us'])))
out=[]
for src,gid,opp,win,side in games:
    p='replays/%s/%d.replay'%(src,gid)
    G=simulate(p)
    if isinstance(side,tuple):
        r=G['result']; us=side[1]
        cand=[s for s in 'AB' if r[s]==us]
        if len(cand)!=1:
            # use winner
            cand=[r['winner'] if win else ('A' if r['winner']=='B' else 'B')]
        side=cand[0]
    G['map']=None
    out.append(dict(src=src,id=gid,opp=opp,win=win,side=side,G=G))
    print(src,gid,opp,win,side,G['result']['endReason'],G['last_round'])
pickle.dump(out,open('/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/qos.pkl','wb'))
