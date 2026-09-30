"""Select + download Stockfish games (GET only, 1.2s apart).
strong: opp elo>=1940 (not us), <=5 per map, round-robin over opponents. mid: opp 1700-1939, 1 per map.
vsus: games vs Cache me outside (952) not already in replays/auto or replays/ab_*. -> index.json"""
import json, os, sys, time, glob, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(H, '../../..')
sys.path.insert(0, os.path.join(ROOT, 'tools')); import api
L = json.load(open(os.path.join(H, 'listing.json')))
have_local = {os.path.basename(p).split('.')[0] for p in glob.glob(ROOT + '/replays/auto/games/*.replay') + glob.glob(ROOT + '/replays/ab_*/*.replay')}
ok = [m for m in L if m['status'] == 'completed' and m['hasReplay'] and m['winner'] in ('a', 'b', 'draw')]
def sides(m):
    s = 'a' if m['a']['id'] == 206 else 'b'; return s, 'b' if s == 'a' else 'a'
sel = {}
bymap = collections.defaultdict(list)
for m in sorted(ok, key=lambda m: m['at'], reverse=True):
    s, o = sides(m)
    if m[o]['id'] == 952:
        if str(m['id']) not in have_local: sel[m['id']] = dict(m, kind='vsus', sf=s)
        continue
    if m[o]['elo'] >= 1940: bymap[m['mapName']].append((m, 'strong'))
for mp, lst in bymap.items():
    oc = collections.Counter(); n = 0
    for rnd in range(3):
        for m, k in lst:
            if n >= 5: break
            s, o = sides(m)
            if m['id'] in sel or oc[m[o]['id']] > rnd: continue
            oc[m[o]['id']] += 1; n += 1; sel[m['id']] = dict(m, kind=k, sf=s)
json.dump(list(sel.values()), open(os.path.join(H, 'index.json'), 'w'), ensure_ascii=False, indent=0)
print(len(sel), collections.Counter((m['kind'], m['mapName']) for m in sel.values()))
for mid, m in sel.items():
    fn = os.path.join(H, 'replays', f'{mid}.replay')
    if os.path.exists(fn): continue
    try: api.download_replay(mid, fn)
    except Exception as ex: print('dl fail', mid, ex)
    time.sleep(1.2)
print('done')
