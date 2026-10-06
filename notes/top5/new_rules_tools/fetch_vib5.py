"""Crawl public listings for Vibing++ (306) back to argv1 (ISO UTC); keep games vs us/FTM/SSS/dev/top teams. Output replays/vib_oct5/games_306.json (Oct 5 study)."""
import sys,json,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import list_games as L
KEEP={952,264,91,545,213,454,55,842,19,507,566,87,946,70,258,112}
CUT=sys.argv[1]
out='/Users/devsingh/Developer/UNSW_Battlecode/replays/vib_oct5/games_306.json'
seen={}; allc=0; p=1
while True:
    for att in range(6):
        try: r=L.fetch(306,p); break
        except Exception as e:
            print('err',p,e,flush=True); time.sleep(30*(att+1))
    ms=r['matches']
    if not ms: break
    for m in ms:
        allc+=1
        o=m['b'] if m['a']['id']==306 else m['a']
        if o['id'] in KEEP:
            seen[m['id']]={k:m.get(k) for k in('id','ranked','status','winner','hasReplay','challenge','at','mapName')}|{'a':m['a'],'b':m['b']}
    oldest=min(m['at'] for m in ms)
    if p%25==0:
        print(p,oldest,allc,len(seen),flush=True)
        json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
    if oldest<CUT: break
    p+=1; time.sleep(1.5)
json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
print('done',p,allc,len(seen),flush=True)
