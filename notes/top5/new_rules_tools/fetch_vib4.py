"""Crawl public listings for team argv1 back to argv2 (ISO UTC); keep games vs TOP teams. Output replays/top1_vib/games_<team>.json (Oct 4 study)."""
import sys,json,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import list_games as L
TOP={306,545,264,91,213,952,454,55,842,19,507,566,87,946,70,258,112}
t=int(sys.argv[1]); CUT=sys.argv[2]
out=f'/Users/devsingh/Developer/UNSW_Battlecode/replays/top1_vib/games_{t}.json'
seen={}; allc=0
p=1
while True:
    for att in range(6):
        try: r=L.fetch(t,p); break
        except Exception as e:
            print('err',p,e,flush=True); time.sleep(30*(att+1))
    ms=r['matches']
    if not ms: break
    for m in ms:
        allc+=1
        if m['a']['id'] in TOP and m['b']['id'] in TOP:
            seen[m['id']]={k:m.get(k) for k in('id','ranked','status','winner','hasReplay','challenge','at','mapName')}|{'a':m['a'],'b':m['b']}
    oldest=min(m['at'] for m in ms)
    if p%25==0:
        print(t,p,oldest,allc,len(seen),flush=True)
        json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
    if oldest<CUT: break
    p+=1; time.sleep(1.5)
json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
print('done',t,p,allc,len(seen),flush=True)
