"""Pick and download replays for team T (argv1) from replays/top2/games_306,264,91.json.
argv2 = from-time, argv3 = to-time, argv4 = cap per opponent (us: all). Appends to replays/top2/sample.json."""
import json,collections,sys,os,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools'); import api
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/'
T=int(sys.argv[1]); FR=sys.argv[2]; TO=sys.argv[3]; CAP=int(sys.argv[4])
G=[g for g in json.load(open(RD+'games_306,264,91.json')) if g['status']=='completed' and g['hasReplay'] and g['winner'] and T in (g['a']['id'],g['b']['id']) and FR<=g['at']<TO]
by=collections.defaultdict(list)
for g in G: by[(g['b'] if g['a']['id']==T else g['a'])['id']].append(g)
pick=[]
for o,gs in by.items():
    gs.sort(key=lambda g:g['at'],reverse=True)
    if o==952: sel=gs
    else:
        seen=set(); sel=[]
        for g in gs:
            if g['mapName'] not in seen: sel.append(g); seen.add(g['mapName'])
        for g in gs:
            if len(sel)>=CAP: break
            if g not in sel: sel.append(g)
        sel=sel[:CAP]
    pick+=sel; print(o,len(gs),'->',len(sel))
try: old=json.load(open(RD+'sample.json'))
except Exception: old=[]
ids={g['id'] for g in old}
old+=[g for g in pick if g['id'] not in ids]
json.dump(old,open(RD+'sample.json','w'),ensure_ascii=False,indent=0)
n=0
for g in pick:
    p=RD+f"{g['id']}.replay"
    if os.path.exists(p): continue
    for att in range(4):
        try: api.download_replay(g['id'],p); n+=1; break
        except Exception as e: print('err',g['id'],e); time.sleep(10*(att+1))
    time.sleep(0.7)
print('downloaded',n,'picked',len(pick),'sample total',len(old))
