"""Extend listing.json with pages A..B of Stockfish games. GET only, 1.2s apart."""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../../tools'))
import list_games as L
f = os.path.join(H, 'listing.json')
out = {m['id']: m for m in json.load(open(f))}
for p in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    try: r = L.fetch(206, p)
    except Exception as ex: print('fail', p, ex); time.sleep(3); continue
    time.sleep(1.2)
    for m in r['matches']:
        out[m['id']] = {k: m.get(k) for k in ('id', 'ranked', 'status', 'winner', 'hasReplay', 'challenge', 'at', 'mapName')} | {'a': m['a'], 'b': m['b']}
    if not r['matches']: break
    print('page', p, len(out), r['matches'][-1]['at'][:16], flush=True)
json.dump(list(out.values()), open(f, 'w'), ensure_ascii=False, indent=0)
