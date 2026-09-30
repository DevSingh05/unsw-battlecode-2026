import json, sys, os, glob, time, collections
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'; SP=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT+'/tools'); import api
TOP={'calc','Stockfish','forgot to mention','cheji bt','Sponge(Albert and Bob)','中国必须人能飞😡','3.14159265','Team SKKU','Sabotage-d','Cutlery','SSS','Peanut Butter','bread first search'}
MAPS={'Schooltime','Portals','Slithery Fight','Queen Of Spades'}
BAD=[('2026-09-30T00:44','2026-09-30T01:02'),('2026-09-30T03:10','2026-09-30T04:33'),('2026-09-30T05:10','2026-09-30T05:45')]
def ver(at):
    if at<'2026-09-30T01:06': return 'v30'
    if at<'2026-09-30T04:33': return 'v31'
    return 'v32'
have={int(os.path.basename(p)[:-7]):p for p in glob.glob(ROOT+'/replays/**/*.replay',recursive=True) if os.path.basename(p)[:-7].isdigit()}
os.makedirs(SP+'/rp',exist_ok=True)
sel=[]
for r in json.load(open(SP+'/allgames.json')):
    at=r['at'][:16]
    if at<'2026-09-29T23:50' or r['opp'] not in TOP or r['map'] not in MAPS or r['win'] is None: continue
    if any(a<=at<b for a,b in BAD): continue
    p=have.get(r['game']) or SP+f"/rp/{r['game']}.replay"
    if not os.path.exists(p):
        api.download_replay(r['game'],p); time.sleep(1.0)
    r['ver']=ver(at); r['path']=p; sel.append(r)
json.dump(sel,open(SP+'/sel.json','w'),ensure_ascii=False)
print(len(sel), collections.Counter((r['map'],r['ver']) for r in sel))
