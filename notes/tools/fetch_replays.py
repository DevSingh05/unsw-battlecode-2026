"""Download replays listed in a games json (from list_games.py). Read-only GETs, 1.2s spacing.
Usage: python3 fetch_replays.py sel.json outdir"""
import json,sys,time,os,urllib.request
g=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
idx=[]
for m in g:
    fn=os.path.join(out,f"{m['id']}.replay")
    idx.append(m)
    if os.path.exists(fn): continue
    req=urllib.request.Request(f"https://game.battlecode.au/api/matches/{m['id']}/replay",headers={'User-Agent':'research-readonly'})
    try:
        data=urllib.request.urlopen(req,timeout=60).read(); open(fn,'wb').write(data); print(m['id'],m['mapName'],len(data),flush=True)
    except Exception as e: print('ERR',m['id'],e,flush=True)
    time.sleep(1.2)
json.dump(idx,open(os.path.join(out,'index.json'),'w'),ensure_ascii=False,indent=0)
