"""Crawl public listing for team 842 (horse) back to argv1 (ISO UTC). Paced 1.5 s, backoff."""
import sys,json,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import list_games as L
t=842; CUT=sys.argv[1]
out='/Users/devsingh/Developer/UNSW_Battlecode/replays/top4_horse/games_842.json'
seen={}; p=1
while True:
    for att in range(6):
        try: r=L.fetch(t,p); break
        except Exception as e:
            print('err',p,e,flush=True); time.sleep(30*(att+1))
    ms=r['matches']
    if not ms: break
    for m in ms:
        seen[m['id']]={k:m.get(k) for k in('id','ranked','status','winner','hasReplay','challenge','tournament','at','mapName')}|{'a':{k:m['a'].get(k) for k in ('id','name','elo')},'b':{k:m['b'].get(k) for k in ('id','name','elo')}}
    oldest=min(m['at'] for m in ms)
    if p%20==0:
        print(p,oldest,len(seen),flush=True)
        json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
    if oldest<CUT: break
    p+=1; time.sleep(1.5)
json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
print('done',p,len(seen),flush=True)
