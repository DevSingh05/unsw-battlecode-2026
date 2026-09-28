"""Find any games between Cache me outside (952) and a current top-10 team; download them. GET only, 1.2 s apart."""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..')); sys.path.insert(0, os.path.join(H, '../../../tools'))
import list_games as L, api
TOP10 = {306, 70, 264, 801, 20, 46, 91, 213, 249, 470}
OUT = os.path.join(H, '../../replays/top10b')
found = []
for p in range(1, int(os.environ.get('PAGES', 25)) + 1):
    r = L.fetch(952, p); time.sleep(1.2)
    if not r['matches']: break
    for m in r['matches']:
        if {m['a']['id'], m['b']['id']} & TOP10 and m['status'] == 'completed' and m['hasReplay']:
            found.append({k: m.get(k) for k in ('id', 'ranked', 'winner', 'at', 'mapName', 'a', 'b')} | {'kind': 'vs952'})
print(len(found), [(m['id'], m['mapName'], m['a']['name'], m['b']['name'], m['winner'], m['at'][:16]) for m in found])
json.dump(found, open(os.path.join(OUT, 'vs952.json'), 'w'), ensure_ascii=False, indent=0)
for m in found:
    fn = os.path.join(OUT, f"{m['id']}.replay")
    if not os.path.exists(fn): api.download_replay(m['id'], fn); time.sleep(1.2)
