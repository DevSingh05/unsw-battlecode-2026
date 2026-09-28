"""List + download recent games of the current top-10 teams (all 10 ranked maps).
Read-only GETs, >=1.2 s apart. Writes notes/replays/top10b/listing.json, index.json and <id>.replay.
Selection: (a) 'peer' games: top-10 team vs an opponent rated 1780-1940 (around us, ~1850);
           (b) 'vs952': any top-10 game vs Cache me outside (id 952).
Env: PAGES (per team, default 6), PER (peer games per map, default 7), CAPT (max per top team per map, default 2)."""
import json, os, sys, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..')); sys.path.insert(0, os.path.join(H, '../../../tools'))
import list_games as L, api
TOP10 = [306, 70, 264, 801, 20, 46, 91, 213, 249, 470]
US = 952
OUT = os.path.join(H, '../../replays/top10b'); os.makedirs(OUT, exist_ok=True)
PAGES = int(os.environ.get('PAGES', 6)); PER = int(os.environ.get('PER', 7)); CAPT = int(os.environ.get('CAPT', 2))
LO, HI = 1780, 1940
lf = os.path.join(OUT, 'listing.json')
listing = {m['id']: m for m in json.load(open(lf))} if os.path.exists(lf) else {}
if not os.environ.get('SKIPLIST'):
    for t in TOP10:
        for p in range(1, PAGES + 1):
            try:
                r = L.fetch(t, p)
            except Exception as ex:
                print('fail', t, p, ex); time.sleep(2); continue
            time.sleep(1.2)
            for m in r['matches']:
                listing[m['id']] = {k: m.get(k) for k in ('id', 'ranked', 'status', 'winner', 'hasReplay', 'challenge', 'at', 'mapName')} | {'a': m['a'], 'b': m['b']}
            if not r['matches']: break
        print('listed', t, len(listing), flush=True)
    json.dump(list(listing.values()), open(lf, 'w'), ensure_ascii=False, indent=0)

ok = [m for m in listing.values() if m['status'] == 'completed' and m['hasReplay'] and m['winner'] in ('a', 'b', 'draw', None)]
sel = {}
# (b) vs us
for m in ok:
    ids = {m['a']['id'], m['b']['id']}
    if US in ids and ids & set(TOP10):
        sel[m['id']] = dict(m, kind='vs952')
# (a) peers
bymap = {}
for m in sorted(ok, key=lambda m: m['at'], reverse=True):
    if m['id'] in sel: continue
    for s, o in (('a', 'b'), ('b', 'a')):
        if m[s]['id'] in TOP10 and m[o]['id'] not in TOP10 and m[o]['id'] != US and LO <= m[o]['elo'] <= HI:
            bymap.setdefault(m['mapName'], []).append((m, m[s]['id']))
for mp, lst in bymap.items():
    tc = {}; n = 0
    for m, t in lst:
        if n >= PER: break
        if tc.get(t, 0) >= CAPT: continue
        tc[t] = tc.get(t, 0) + 1; n += 1
        sel[m['id']] = dict(m, kind='peer')
json.dump(list(sel.values()), open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=0)
print('selected', len(sel), {k: sum(1 for m in sel.values() if m['kind'] == k) for k in ('peer', 'vs952')})
for mid, m in sel.items():
    fn = os.path.join(OUT, f'{mid}.replay')
    if os.path.exists(fn): continue
    try:
        api.download_replay(mid, fn)
    except Exception as ex:
        print('dl fail', mid, ex)
    time.sleep(1.2)
print('done')
