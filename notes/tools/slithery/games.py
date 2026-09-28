# Our Slithery Fight games -> pickle (dir,gid,opp,win,side). Side from ledger or by matching summary 'us' to replay result.
import json,glob,os,sys,pickle
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
import replay_decode as R
MAP='Slithery Fight'
games=[]
for g in json.load(open('replays/v7/ledger.json')):
    if g['map']==MAP: games.append(('v7',g['game'],g['opp'],g['win'],g['side']))
for d in ['ch1','ch2','ch3','ch5','ch6','ch7','ch8']:
    for g in json.load(open('replays/%s/summary.json'%d)):
        if g.get('map')!=MAP: continue
        p='replays/%s/%d.replay'%(d,g['id'])
        if not os.path.exists(p): continue
        side=g.get('side')
        if not side:
            res=R.load(p)['result']
            for s in 'AB':
                r=res[s]
                if r.get('longest')==g['us']['longest'] and r.get('dragonCount')==g['us']['dragonCount']: side=s
        games.append((d,g['id'],g['opp'],g['win'],side))
pickle.dump(games,open('notes/tools/slithery/meta.pkl','wb'))
for x in games: print(x)
