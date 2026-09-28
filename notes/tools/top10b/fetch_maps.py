"""Extra peer games on specific maps (default Default+Autarky+PD): top-10 vs opponent 1780-1940. GET only, 1.2 s apart.
Appends to notes/replays/top10b/index.json. Env: MAPIDS='4,19,17' PER=12 PAGES=8 CAPT=3"""
import json, os, sys, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..')); sys.path.insert(0, os.path.join(H, '../../../tools'))
import list_games as L, api
TOP10 = [306, 70, 264, 801, 20, 46, 91, 213, 249, 470]
OUT = os.path.join(H, '../../replays/top10b')
idxf = os.path.join(OUT, 'index.json'); idx = {m['id']: m for m in json.load(open(idxf))}
PER = int(os.environ.get('PER', 12)); PAGES = int(os.environ.get('PAGES', 8)); CAPT = int(os.environ.get('CAPT', 3))
for mid in [int(x) for x in os.environ.get('MAPIDS', '4,19,17').split(',')]:
    have = []; tc = {}
    for p in range(1, PAGES + 1):
        u = f'https://game.battlecode.au/games/__data.json?teams={",".join(map(str, TOP10))}&maps={mid}&page={p}'
        r = L.devalue(json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'research-readonly'}), timeout=30))['nodes'][1]['data'])
        time.sleep(1.2)
        for m in r['matches']:
            if m['status'] != 'completed' or not m['hasReplay']: continue
            for s, o in (('a', 'b'), ('b', 'a')):
                t = m[s]['id']
                if t in TOP10 and m[o]['id'] not in TOP10 and 1780 <= m[o]['elo'] <= 1940:
                    if m['id'] in idx: have.append(m['id']); tc[t] = tc.get(t, 0) + 1; break
                    if tc.get(t, 0) >= CAPT or len(have) >= PER: break
                    tc[t] = tc.get(t, 0) + 1; have.append(m['id'])
                    idx[m['id']] = {k: m.get(k) for k in ('id', 'ranked', 'winner', 'at', 'mapName', 'a', 'b')} | {'kind': 'peer'}
                    break
        if len(have) >= PER: break
    print(mid, len(have), tc, flush=True)
json.dump(list(idx.values()), open(idxf, 'w'), ensure_ascii=False, indent=0)
for gid in idx:
    fn = os.path.join(OUT, f'{gid}.replay')
    if not os.path.exists(fn): api.download_replay(gid, fn); time.sleep(1.2)
print('total', len(idx))
