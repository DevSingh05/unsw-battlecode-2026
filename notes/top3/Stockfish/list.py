"""List Stockfish (206) recent games. GET only, 1.2s apart. -> listing.json"""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../../tools'))
import list_games as L
out = {}
for p in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 6):
    r = L.fetch(206, p); time.sleep(1.2)
    for m in r['matches']:
        out[m['id']] = {k: m.get(k) for k in ('id', 'ranked', 'status', 'winner', 'hasReplay', 'challenge', 'at', 'mapName')} | {'a': m['a'], 'b': m['b']}
    if not r['matches']: break
    print('page', p, len(out), flush=True)
json.dump(list(out.values()), open(os.path.join(H, 'listing.json'), 'w'), ensure_ascii=False, indent=0)
