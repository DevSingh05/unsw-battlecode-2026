"""Pick + download replays for team T (argv1) from replays/top1_vib/games_<T>.json.
argv2 from-time, argv3 to-time, argv4 cap per non-us opponent, argv5 (opt) us from-time (all games vs 952 from then).
Appends to replays/top1_vib/sample.json. Paced >=1.5 s, backs off 30 s on errors (429)."""
import json,collections,sys,os,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools'); import api
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1_vib/'
T=int(sys.argv[1]); FR=sys.argv[2]; TO=sys.argv[3]; CAP=int(sys.argv[4]); UFR=sys.argv[5] if len(sys.argv)>5 else FR
G=[g for g in json.load(open(RD+f'games_{T}.json')) if g['status']=='completed' and g['hasReplay'] and g['winner'] and T in (g['a']['id'],g['b']['id'])]
by=collections.defaultdict(list)
for g in G:
    o=(g['b'] if g['a']['id']==T else g['a'])['id']
    if o==952 and UFR<=g['at']<TO: by[o].append(g)
    elif o!=952 and FR<=g['at']<TO: by[o].append(g)
pick=[]
for o,gs in by.items():
    gs.sort(key=lambda g:g['at'],reverse=True)
    if o==952: sel=gs
    else:
        seen=set(); sel=[]
        for g in gs:
            if g['mapName'] not in seen: sel.append(g); seen.add(g['mapName'])
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
    for att in range(5):
        try: api.download_replay(g['id'],p); n+=1; break
        except Exception as e: print('err',g['id'],e,flush=True); time.sleep(30*(att+1))
    time.sleep(1.5)
print('downloaded',n,'picked',len(pick),'sample total',len(old))
