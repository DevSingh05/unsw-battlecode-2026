"""Collect recent strong-vs-strong games (both elos >= MIN_ELO at game time) per ranked map and download replays.
Read-only GETs, >=1.2 s apart. Usage: python3 permap_fetch.py [per_map=10] [min_elo=1850] [only_map_name]
Writes notes/replays/permap/<id>.replay and index.json."""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../tools'))
import list_games as L
import api
MAPS = {'Schooltime': 9, 'Portals': 20, 'Slithery Fight': 21, 'Trophy': 11, 'Prisoners Dilemma': 17,
        'Queen Of Spades': 7, 'Default': 4, 'Autarky': 19, 'Devil': 13, 'Trauma': 15}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/permap')
PER = int(sys.argv[1]) if len(sys.argv) > 1 else 10
MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 1850
TOP = [470, 306, 280, 801, 213, 46, 467, 20, 104, 157, 314, 249, 91, 507, 206, 545, 27, 264, 55, 370, 798, 221, 852, 82, 566]

def page(mid, p):
    u = f'https://game.battlecode.au/games/__data.json?teams={",".join(map(str, TOP))}&maps={mid}&page={p}'
    req = urllib.request.Request(u, headers={'User-Agent': 'research-readonly'})
    return L.devalue(json.load(urllib.request.urlopen(req, timeout=30))['nodes'][1]['data'])

os.makedirs(OUT, exist_ok=True)
idxf = os.path.join(OUT, 'index.json')
idx = {m['id']: m for m in json.load(open(idxf))} if os.path.exists(idxf) else {}
ONLY = sys.argv[3] if len(sys.argv) > 3 else None
for name, mid in MAPS.items():
    if ONLY and name != ONLY: continue
    have = [m for m in idx.values() if m['mapName'] == name]
    p = 1
    while len(have) < PER and p <= 15:
        r = page(mid, p); time.sleep(1.2); p += 1
        for m in r['matches']:
            if m['status'] != 'completed' or not m['hasReplay'] or m['winner'] not in ('a', 'b'): continue
            if m['a']['elo'] < MIN or m['b']['elo'] < MIN or m['a']['id'] == m['b']['id']: continue
            if m['id'] in idx: continue
            idx[m['id']] = {k: m[k] for k in ('id', 'ranked', 'winner', 'at', 'mapName', 'a', 'b')}
            have.append(m)
            if len(have) >= PER: break
    for m in have:
        fn = os.path.join(OUT, f"{m['id']}.replay")
        if not os.path.exists(fn):
            api.download_replay(m['id'], fn); time.sleep(1.2)
    print(name, len(have), flush=True)
    json.dump(list(idx.values()), open(idxf, 'w'), ensure_ascii=False, indent=0)
