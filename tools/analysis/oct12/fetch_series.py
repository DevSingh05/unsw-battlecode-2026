#!/usr/bin/env python3
"""fetch_series.py: per-game detail for our latest 200 series (GET only, paced 1.1 s, resumable).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/fetch_series.py
Outputs: work/oct12/battles.json (the list), work/oct12/series/<battleId>.json (one per series)."""
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

W = ROOT / "work" / "oct12"
(W / "series").mkdir(parents=True, exist_ok=True)
L = api.get("/api/v1/battles?limit=200")
(W / "battles.json").write_text(json.dumps(L))
n = 0
for b in L:
    p = W / "series" / f"{b['id']}.json"
    if p.exists() or b.get("outcome") == "live":
        continue
    for attempt in range(3):
        try:
            p.write_text(json.dumps(api.get(f"/api/v1/battles/{b['id']}")))
            n += 1
            break
        except Exception as e:  # noqa: BLE001
            print("retry", b["id"], e, file=sys.stderr)
            time.sleep(5)
    time.sleep(1.1)
print(f"fetched {n} new series; {len(list((W / 'series').glob('*.json')))} on disk")
