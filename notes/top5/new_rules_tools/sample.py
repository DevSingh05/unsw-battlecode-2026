import json,collections,random,sys,os,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools'); import api
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top5_new/'
G=[g for g in json.load(open(RD+'games_pairs.json')) if g['status']=='completed' and g['hasReplay'] and g['winner']]
PER=int(sys.argv[1]) if len(sys.argv)>1 else 14
by=collections.defaultdict(list)
for g in G: by[tuple(sorted([g['a']['name'],g['b']['name']]))].append(g)
pick=[]
for k,gs in by.items():
    gs.sort(key=lambda g:g['at'],reverse=True)
    us='Cache me outside' in k
    if us:
        sel=[g for g in gs if g['at']>='2026-10-02T08:08:56'][:28]  # v41 and v43 only
    else:
        # most recent, one per map first, then fill
        seen=set(); sel=[]
        for g in gs:
            if g['mapName'] not in seen: sel.append(g); seen.add(g['mapName'])
        for g in gs:
            if len(sel)>=PER: break
            if g not in sel: sel.append(g)
        sel=sel[:PER]
    pick+=sel
    print(k,len(gs),'->',len(sel))
json.dump(pick,open(RD+'sample.json','w'),ensure_ascii=False,indent=0)
n=0
for g in pick:
    p=RD+f"{g['id']}.replay"
    if os.path.exists(p): continue
    for att in range(4):
        try: api.download_replay(g['id'],p); n+=1; break
        except Exception as e: print('err',g['id'],e); time.sleep(10*(att+1))
    time.sleep(0.6)
print('downloaded',n,'total',len(pick))
