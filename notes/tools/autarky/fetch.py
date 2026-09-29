"""List recent games of the current top-10 and download their Autarky replays (GET only, >=1.2 s apart).
Writes notes/replays/autarky/{listing.json,index.json,<id>.replay}. Env: PAGES (default 4), MAX (default 40)."""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..')); sys.path.insert(0, os.path.join(H, '../../../tools'))
import list_games as L, api
TOP10 = [306, 20, 70, 801, 264, 213, 314, 46, 91, 104]
US = 952
OUT = os.path.join(H, '../../replays/autarky'); os.makedirs(OUT, exist_ok=True)
PAGES = int(os.environ.get('PAGES', 4)); MAX = int(os.environ.get('MAX', 40))
listing = {}
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
json.dump(list(listing.values()), open(os.path.join(OUT, 'listing.json'), 'w'), ensure_ascii=False, indent=0)
sel = [m for m in listing.values() if m['mapName'] == 'Autarky' and m['status'] == 'completed' and m['hasReplay']
       and US not in (m['a']['id'], m['b']['id'])]
sel.sort(key=lambda m: m['at'], reverse=True)
# prefer top-vs-top, then top-vs-(>=1900)
def kind(m):
    a, b = m['a']['id'] in TOP10, m['b']['id'] in TOP10
    return 'toptop' if a and b else 'peer'
sel = [dict(m, kind=kind(m)) for m in sel]
sel = sorted(sel, key=lambda m: (m['kind'] != 'toptop', m['at']), reverse=False)[:MAX]
json.dump(sel, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=0)
print('selected', len(sel), sum(m['kind'] == 'toptop' for m in sel))
for m in sel:
    fn = os.path.join(OUT, f"{m['id']}.replay")
    if os.path.exists(fn): continue
    try:
        api.download_replay(m['id'], fn)
    except Exception as ex:
        print('dl fail', m['id'], ex)
    time.sleep(1.2)
print('done')
