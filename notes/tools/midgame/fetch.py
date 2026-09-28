"""Fetch recent games involving a current top-10 team on ordinary maps (Default, Autarky, Devil, Trophy, PD, Trauma).
Opponent elo >= MIN. Read-only GETs, 1.2 s apart. Writes notes/replays/midgame/<id>.replay + index.json"""
import json, os, sys, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..')); sys.path.insert(0, os.path.join(H, '../../../tools'))
import list_games as L, api
TOP10 = [306, 70, 801, 264, 20, 470, 249, 91, 46, 507]
MAPS = {'Default': 4, 'Autarky': 19, 'Devil': 13, 'Trophy': 11, 'Prisoners Dilemma': 17, 'Trauma': 15}
OUT = os.path.join(H, '../../replays/midgame'); os.makedirs(OUT, exist_ok=True)
PER = int(os.environ.get("PER", 5)); MIN = 1850; CAPT = int(os.environ.get("CAPT", 2))
if os.environ.get("TEAMS"): TOP10 = [int(x) for x in os.environ["TEAMS"].split(",")]
idxf = os.path.join(OUT, 'index.json')
idx = {m['id']: m for m in json.load(open(idxf))} if os.path.exists(idxf) else {}
for name, mid in MAPS.items():
    have = [m for m in idx.values() if m['mapName'] == name]
    tc = {}
    for m in have:
        for s in 'ab':
            if m[s]['id'] in TOP10: tc[m[s]['id']] = tc.get(m[s]['id'], 0) + 1
    p = 1
    while len(have) < PER and p <= 6:
        u = f'https://game.battlecode.au/games/__data.json?teams={",".join(map(str, TOP10))}&maps={mid}&page={p}'
        r = L.devalue(json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'research-readonly'}), timeout=30))['nodes'][1]['data'])
        time.sleep(1.2); p += 1
        for m in r['matches']:
            if m['status'] != 'completed' or not m['hasReplay'] or m['winner'] not in ('a', 'b'): continue
            if m['id'] in idx or m['a']['id'] == m['b']['id']: continue
            if min(m['a']['elo'], m['b']['elo']) < MIN: continue
            tops = [m[s]['id'] for s in 'ab' if m[s]['id'] in TOP10]
            if any(tc.get(t, 0) >= CAPT for t in tops): continue
            for t in tops: tc[t] = tc.get(t, 0) + 1
            idx[m['id']] = {k: m[k] for k in ('id', 'ranked', 'winner', 'at', 'mapName', 'a', 'b')}
            have.append(idx[m['id']])
            if len(have) >= PER: break
    for m in have:
        fn = os.path.join(OUT, f"{m['id']}.replay")
        if not os.path.exists(fn):
            api.download_replay(m['id'], fn); time.sleep(1.2)
    print(name, [(m['id'], m['a']['name'], m['b']['name'], m['winner'], m['at'][:16]) for m in have], flush=True)
    json.dump(list(idx.values()), open(idxf, 'w'), ensure_ascii=False, indent=0)
