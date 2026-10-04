# download loss replays (+ win sample) for v55/v61 windows from ab_server --json rows. run from project root.
import sys, json, time, pathlib, collections
sys.path.insert(0,'tools'); import api
out=pathlib.Path('replays/loss_audit2')
rows=json.load(open(out/'ab_rows.json'))
R=[]
for ver,l in rows.items():
    for r in l: r['ver']=ver; R.append(r)
json.dump(R,open(out/'summary.json','w'),indent=0)
dl=[r for r in R if r['s']<1]
bym=collections.defaultdict(list)
for r in R:
    if r['s']==1: bym[(r['map'],r['top10'])].append(r)
for k,l in bym.items(): dl+=sorted(l,key=lambda r:-r['ropp'])[:3]
n=0
for r in dl:
    p=out/f"{r['id']}.replay"
    if p.exists(): continue
    for att in range(4):
        try: api.download_replay(r["id"],p); n+=1; time.sleep(0.8); break
        except Exception as e: print("fail",r['id'],e,flush=True); time.sleep(8*(att+1))
print('rows',len(R),'to dl',len(dl),'downloaded',n)
