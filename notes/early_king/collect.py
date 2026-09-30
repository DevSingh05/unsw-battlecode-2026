import json, sys, os, glob, time
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'; SP=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT+'/tools'); import api
US="Cache me outside"
TOP={'calc','Stockfish','forgot to mention','cheji bt','Sponge(Albert and Bob)','中国必须人能飞😡','3.14159265','Team SKKU','Sabotage-d','Cutlery','SSS','Peanut Butter','bread first search'}
MAPS={'Schooltime','Portals','Slithery Fight','Queen Of Spades'}
rows={}
for r in json.load(open(ROOT+'/replays/auto/games/ledger.json')):
    rows[r['game']]=dict(game=r['game'],opp=r['opp'],map=r['map'],win=r['win'],side=r['side'],at=r['at'],src='ledger')
for b in api.get('/api/v1/battles?limit=200'):
    if b['outcome'] in ('queued','live') or b['opponent'] not in TOP or b['at']<'2026-09-29T23:40': continue
    d=api.get(f"/api/v1/battles/{b['id']}"); time.sleep(0.3)
    us_a=d['teamAName']==US
    for g in d['games']:
        if g['status']!='completed' or not g['winner']: continue
        rows.setdefault(g['id'], dict(game=g['id'],opp=b['opponent'],map=g['mapName'],win=(g['winner']=='a')==us_a,side='A' if us_a else 'B',at=b['at'],src='api'))
json.dump(list(rows.values()), open(SP+'/allgames.json','w'), ensure_ascii=False)
print(len(rows))
