#!/usr/bin/env python3
"""get_replays.py MAP[,MAP...]: download replays of our recent games on the named maps (public endpoint, paced 1.3 s).
Reuses any replay already under work/ or replays/. Reads work/oct12/games_recent.json (series_report.py writes it).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/get_replays.py "Atlantis,Whale Song"       # 'all' = every map"""
import json
import pathlib
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

W = ROOT / "work" / "oct12"
RP = W / "replays"
RP.mkdir(exist_ok=True)
want = set(sys.argv[1].split(","))
rows = [r for r in json.loads((W / "games_recent.json").read_text()) if "all" in want or r["map"] in want]
have = {}
for base in (ROOT / "work" / "gfloss" / "replays", ROOT / "work" / "gfloss" / "top_replays"):
    for p in base.glob("*.replay"):
        have[p.name] = p
n = c = 0
for r in rows:
    dst = RP / f"{r['gid']}.replay"
    if dst.exists():
        continue
    src = have.get(dst.name)
    if src:
        shutil.copy2(src, dst)
        c += 1
        continue
    for attempt in range(3):
        try:
            api.download_replay(r["gid"], dst)
            n += 1
            break
        except Exception as e:  # noqa: BLE001
            print("retry", r["gid"], e, file=sys.stderr)
            time.sleep(4)
    time.sleep(1.3)
print(f"{len(rows)} games wanted; downloaded {n}, copied {c}; {len(list(RP.glob('*.replay')))} replays on disk")
