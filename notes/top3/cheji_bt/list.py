"""List recent games of cheji bt (id 70). GET only, 1.2 s apart. Writes listing.json"""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../../tools'))
import list_games as L
seen = {}
for p in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 9):
    try: r = L.fetch(70, p)
    except Exception as ex: print('fail', p, ex); time.sleep(2); continue
    time.sleep(1.2)
    for m in r['matches']:
        seen[m['id']] = {k: m.get(k) for k in ('id', 'ranked', 'status', 'winner', 'hasReplay', 'challenge', 'at', 'mapName')} | {'a': m['a'], 'b': m['b']}
    print(p, len(r['matches']), r['matches'][-1]['at'] if r['matches'] else '', flush=True)
    if not r['matches']: break
json.dump(list(seen.values()), open(os.path.join(H, 'listing.json'), 'w'), ensure_ascii=False, indent=0)
