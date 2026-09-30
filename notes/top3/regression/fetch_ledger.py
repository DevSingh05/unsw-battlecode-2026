#!/usr/bin/env python3
"""Rate-limited (<=1 req/s) ledger of our games since a time. GET only.
usage (from project root): python3 notes/top3/regression/fetch_ledger.py 2026-09-29T20:00
writes notes/top3/regression/ledger.json (cached per battle in battles/)"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import api
US = "Cache me outside"
HERE = pathlib.Path(__file__).resolve().parent
since = sys.argv[1]
cache = HERE / 'battles'; cache.mkdir(exist_ok=True)
rows = []
lst = api.get('/api/v1/battles?limit=200'); time.sleep(1.05)
for b in lst:
    if b['at'] < since or b['outcome'] in ('queued', 'live'):
        continue
    cp = cache / f"{b['id']}.json"
    if cp.exists():
        d = json.loads(cp.read_text())
    else:
        d = api.get(f"/api/v1/battles/{b['id']}"); time.sleep(1.05)
        cp.write_text(json.dumps(d))
    us_a = d['teamAName'] == US
    for g in d['games']:
        if g['status'] != 'completed':
            continue
        won = (g['winner'] == 'a') == us_a if g['winner'] else None
        rows.append({'game': g['id'], 'battle': b['id'], 'ranked': b['ranked'], 'opp': b['opponent'],
                     'oppId': b.get('opponentId'), 'oppElo': b['opponentElo'], 'map': g['mapName'], 'win': won,
                     'side': 'A' if us_a else 'B', 'at': b['at']})
(HERE / 'ledger.json').write_text(json.dumps(rows, indent=1))
print(len(rows), 'games')
