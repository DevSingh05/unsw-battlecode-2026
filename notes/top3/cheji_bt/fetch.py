"""Select + download cheji bt games: (a) vs opponents elo>=1900 (not us), <=4 per map, <=1 per opponent per map;
(b) all listed games vs us (952). GET only, 1.2 s apart. Writes index.json + replays/<id>.replay"""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../../../tools'))
import api
L = json.load(open(os.path.join(H, 'listing.json')))
ok = [m for m in L if m['status'] == 'completed' and m['hasReplay']]
ok.sort(key=lambda m: m['at'], reverse=True)
sel = {}
for m in ok:
    o = m['b'] if m['a']['id'] == 70 else m['a']
    if o['id'] == 952: sel[m['id']] = dict(m, kind='vsus', opp=o['name'], oppElo=o['elo'], side='a' if m['a']['id'] == 70 else 'b')
per = {}
for m in ok:
    o = m['b'] if m['a']['id'] == 70 else m['a']
    if o['id'] == 952 or o['elo'] < 1900: continue
    k = per.setdefault(m['mapName'], [])
    if len(k) >= 4 or o['id'] in k: continue
    k.append(o['id'])
    sel[m['id']] = dict(m, kind='peer', opp=o['name'], oppElo=o['elo'], side='a' if m['a']['id'] == 70 else 'b')
json.dump(list(sel.values()), open(os.path.join(H, 'index.json'), 'w'), ensure_ascii=False, indent=0)
print(len(sel), {k: sum(1 for m in sel.values() if m['kind'] == k) for k in ('peer', 'vsus')})
for mid, m in sel.items():
    fn = os.path.join(H, 'replays', f'{mid}.replay')
    if os.path.exists(fn): continue
    try: api.download_replay(mid, fn)
    except Exception as ex: print('dl fail', mid, ex)
    time.sleep(1.2)
for m in sel.values(): print(m['id'], m['kind'], m['mapName'], m['opp'], m['oppElo'], 'cheji=' + m['side'], 'winner=' + str(m['winner']))
