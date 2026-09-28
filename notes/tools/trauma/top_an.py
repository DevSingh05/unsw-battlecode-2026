import json,sys,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from replay_sim import simulate
from collections import Counter
HOT={(35,9),(36,9),(11,10),(36,10),(11,11),(36,11),(11,12),(36,12),(11,13),(36,13),(11,14),(12,14)}
ix=[g for g in json.load(open('notes/replays/permap/index.json')) if g['mapName']=='Trauma']
seen=set()
for g in ix:
    G=simulate('notes/replays/permap/%d.replay'%g['id'])
    key=(g['a']['name'],g['b']['name'],G['result']['A']['total'])
    if key in seen: continue
    seen.add(key)
    W=G['result']['winner']; L='B' if W=='A' else 'A'
    nm={'A':g['a']['name'],'B':g['b']['name']}
    R=dict(G['rounds'])
    line=[]
    for r in [25,50,100,150,200,250,300,350,400,450,499]:
        s=R.get(r) or R[max(R)]
        line.append('%d:%d/%d|%d/%d'%(r,s[W]['n'],s[L]['n'],s[W]['max'],s[L]['max']))
    he=Counter(e['team'] for e in G['eats'] if e['tile'] in HOT)
    print('==',g['id'],'W',nm[W],W,'vs',nm[L],G['result']['endReason'],G['result'][W],G['result'][L])
    print('  n/max W/L', ' '.join(line))
    print('  hot eats W/L',he[W],he[L])
    for T in (W,L):
        big=[(x['round'],x['len'],x['reason'],x['head']) for x in G['deaths'] if x['team']==T and x['len']>=8]
        print('  big deaths',T,big[:8])
