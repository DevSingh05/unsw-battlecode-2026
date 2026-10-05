"""Download replays by id list (argv1 = file with one id per line) into replays/devtest/. Paced 1.5 s, 30 s backoff."""
import sys,os,time
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools'); import api
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
ids=[int(x) for x in open(sys.argv[1]).read().split()]
n=0
for gid in ids:
    p=RD+f'{gid}.replay'
    if os.path.exists(p): continue
    for att in range(5):
        try: api.download_replay(gid,p); n+=1; break
        except Exception as e: print('err',gid,e,flush=True); time.sleep(30*(att+1))
    time.sleep(1.5)
print('downloaded',n,'of',len(ids),flush=True)
