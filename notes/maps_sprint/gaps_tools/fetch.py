import sys,json,os
sys.path.insert(0,'tools'); import api
D='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps'
b=json.load(open('notes/sprint_bracket.json'))
# prefer late rounds (strong bots, longer games)
ms=sorted([m for m in b['matches'] if m.get('battleId')],key=lambda m:-m['bracketMatch']['round'])
per={}
for m in ms:
    if all(len(v)>=8 for v in per.values()) and len(per)>=7: break
    try: g=api.get(f"/api/v1/battles/{m['battleId']}")['games']
    except Exception as e: print('err',e); continue
    for x in g:
        n=x['mapName']; per.setdefault(n,[])
        if len(per[n])<8: per[n].append(x['id'])
json.dump(per,open(D+'/games.json','w'),indent=1)
print({k:len(v) for k,v in per.items()})
for n,ids in per.items():
    for i in ids:
        p=f"{D}/{n.replace(' ','_')}_{i}.bin"
        if not os.path.exists(p): api.download_replay(i,p)
