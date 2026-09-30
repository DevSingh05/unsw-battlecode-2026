"""Select + download Cutlery games (GET only, 1.2 s apart). Writes index.json + replays/<id>.replay.
Selection: strong opps (elo>=1900) cap 4/map preferring opponent variety; plus 1 peer (1700-1899) per map."""
import json, os, sys, time
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../../../tools'))
import api
L = json.load(open(os.path.join(H, 'listing.json')))
ok = sorted([m for m in L if m['status'] == 'completed' and m['hasReplay'] and m['a']['id'] != m['b']['id']], key=lambda m: m['at'], reverse=True)
def opp(m): return m['b'] if m['a']['id'] == 306 else m['a']
sel = {}; pm = Counter(); po = Counter()
strong = [m for m in ok if opp(m)['elo'] >= 1900]
for rnd in range(4):
    for m in strong:
        if m['id'] in sel: continue
        o = opp(m)['id']
        if pm[m['mapName']] >= rnd + 1 or po[(o, m['mapName'])] >= 1 + rnd // 2: continue
        if po[o] > 3 + 2 * rnd: continue
        sel[m['id']] = dict(m, kind='strong'); pm[m['mapName']] += 1; po[(o, m['mapName'])] += 1; po[o] += 1
pp = Counter()
for m in ok:
    if 1700 <= opp(m)['elo'] < 1900 and pp[m['mapName']] < 1:
        sel[m['id']] = dict(m, kind='peer'); pp[m['mapName']] += 1
print(len(sel), Counter(m['mapName'] for m in sel.values()), Counter(opp(m)['name'] for m in sel.values()))
json.dump(list(sel.values()), open(os.path.join(H, 'index.json'), 'w'), ensure_ascii=False, indent=0)
os.makedirs(os.path.join(H, 'replays'), exist_ok=True)
for mid in sel:
    fn = os.path.join(H, 'replays', f'{mid}.replay')
    if os.path.exists(fn): continue
    try: api.download_replay(mid, fn)
    except Exception as ex: print('dl fail', mid, ex)
    time.sleep(1.2)
print('done')
