"""Crawl public game listings for teams (argv1 comma list) back to CUT; keep games where both teams are in TOP. Output replays/top2/games_<arg>.json"""
import sys,json,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import list_games as L
TOP={264,306,91,213,842,566,952,55,258,112}
CUT=sys.argv[2] if len(sys.argv)>2 else '2026-10-02T18:00'
out='/Users/devsingh/Developer/UNSW_Battlecode/replays/top2/games_'+sys.argv[1]+'.json'
seen={}
try: seen={m['id']:m for m in json.load(open(out))}
except Exception: pass
for t in [int(x) for x in sys.argv[1].split(',')]:
    p=1; n=0
    while True:
        for att in range(5):
            try: r=L.fetch(t,p); break
            except Exception as e:
                print('err',t,p,e,flush=True); time.sleep(20*(att+1))
        ms=r['matches']
        if not ms: break
        for m in ms:
            n+=1
            if m['a']['id'] in TOP and m['b']['id'] in TOP:
                seen[m['id']]={k:m.get(k) for k in('id','ranked','status','winner','hasReplay','challenge','at','mapName')}|{'a':m['a'],'b':m['b']}
        oldest=min(m['at'] for m in ms)
        if p%20==0:
            print(t,p,oldest,len(seen),flush=True)
            json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
        if oldest<CUT: break
        p+=1; time.sleep(1.1)
    print('done',t,p,n,len(seen),flush=True)
    json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
