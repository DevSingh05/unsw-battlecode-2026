import sys,json,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import list_games as L
TOP={264,91,213,306,842,566,55,952}
CUT='2026-10-02T07:10'
out='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1/games_'+sys.argv[1]+'.json'
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
            if m['a']['id'] in TOP and m['b']['id'] in TOP and 264 in (m['a']['id'],m['b']['id']):
                seen[m['id']]={k:m.get(k) for k in('id','ranked','status','winner','hasReplay','challenge','at','mapName')}|{'a':m['a'],'b':m['b']}
        oldest=min(m['at'] for m in ms)
        if p%20==0:
            print(t,p,oldest,len(seen),flush=True)
            json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
        if oldest<CUT: break
        p+=1; time.sleep(1.1)
    print('done',t,p,n,len(seen),flush=True)
    json.dump(list(seen.values()),open(out,'w'),ensure_ascii=False)
