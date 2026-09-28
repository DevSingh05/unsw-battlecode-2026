"""Fetch recent games on growth maps won by a CURRENT top-10 team vs an opponent elo>=1860.
Read-only GETs, 1.2 s apart. Writes notes/replays/kings/<id>.replay + index.json"""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools'))
import list_games as L, api
TOP10 = [470, 306, 801, 46, 91, 280, 249, 213, 507, 20]
MAPS = {'Schooltime': 9, 'Portals': 20, 'Slithery Fight': 21, 'Queen Of Spades': 7}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/kings')
PER = 11; MIN = 1860; CAPW = 3
os.makedirs(OUT, exist_ok=True)
idx = {}
for name, mid in MAPS.items():
    have = []; pairs = set(); wcount = {}
    for p in range(1, 9):
        u = f'https://game.battlecode.au/games/__data.json?teams={",".join(map(str, TOP10))}&maps={mid}&page={p}'
        r = L.devalue(json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'research-readonly'}), timeout=30))['nodes'][1]['data'])
        time.sleep(1.2)
        for m in r['matches']:
            if m['status'] != 'completed' or not m['hasReplay'] or m['winner'] not in ('a', 'b'): continue
            w = m[m['winner']]; l = m['b' if m['winner'] == 'a' else 'a']
            if w['id'] not in TOP10 or l['elo'] < MIN or w['id'] == l['id']: continue
            key = (m['a']['id'], m['b']['id'])
            if key in pairs or wcount.get(w['id'], 0) >= CAPW: continue
            pairs.add(key); wcount[w['id']] = wcount.get(w['id'], 0) + 1
            have.append({k: m[k] for k in ('id', 'ranked', 'winner', 'at', 'mapName', 'a', 'b')})
            if len(have) >= PER: break
        if len(have) >= PER: break
    for m in have:
        fn = os.path.join(OUT, f"{m['id']}.replay")
        if not os.path.exists(fn):
            api.download_replay(m['id'], fn); time.sleep(1.2)
        idx[m['id']] = m
    print(name, len(have), [(m['a']['name'], m['b']['name'], m['winner']) for m in have], flush=True)
    json.dump(list(idx.values()), open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=0)
