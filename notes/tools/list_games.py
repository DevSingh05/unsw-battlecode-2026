"""List public games for teams via /games/__data.json (SvelteKit devalue). Read-only, polite (1.2s between requests).
Usage: python3 list_games.py 470,801,213,46,280 pages > games.json"""
import json,sys,time,urllib.request
def devalue(data):
    cache={}
    def h(i):
        if i==-1: return None
        if i in cache: return cache[i]
        v=data[i]
        if isinstance(v,dict): r={k:h(x) for k,x in v.items()}
        elif isinstance(v,list):
            if v and isinstance(v[0],str) and v[0] in('Date',): r=v[1]
            else: r=[h(x) for x in v]
        else: r=v
        cache[i]=r; return r
    return h(0)
def fetch(team,page):
    u=f'https://game.battlecode.au/games/__data.json?teams={team}&page={page}'
    req=urllib.request.Request(u,headers={'User-Agent':'research-readonly'})
    d=json.load(urllib.request.urlopen(req,timeout=30))
    return devalue(d['nodes'][1]['data'])
if __name__=='__main__':
    teams=[int(x) for x in sys.argv[1].split(',')]; pages=int(sys.argv[2])
    seen={}
    for t in teams:
        for p in range(1,pages+1):
            r=fetch(t,p); time.sleep(1.2)
            for m in r['matches']:
                seen[m['id']]={k:m[k] for k in('id','ranked','status','winner','hasReplay','challenge','at','mapName')}|{'a':m['a'],'b':m['b']}
    json.dump(list(seen.values()),sys.stdout,ensure_ascii=False,indent=0)
