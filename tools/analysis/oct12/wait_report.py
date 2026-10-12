#!/usr/bin/env python3
"""wait_report.py SINCE_UTC MINUTES "Map A,Map B": sleep until MINUTES after SINCE (the live build's upload time), then print
the build watch table, the per-map mechanics and the ladder row. Read-only. Meant to run in the background so the
session is woken when a build has enough server games to judge.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/wait_report.py 2026-10-12T21:20:00 75 "Whale Song,Troll Australia" """
import datetime as dt
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

since, minutes, maps = sys.argv[1], float(sys.argv[2]), sys.argv[3]
t0 = dt.datetime.fromisoformat(since).replace(tzinfo=dt.timezone.utc)
end = t0 + dt.timedelta(minutes=minutes)
while dt.datetime.now(dt.timezone.utc) < end:
    time.sleep(30)
py = sys.executable
print(subprocess.run([py, str(ROOT / "tools/analysis/oct12/build_watch.py"), since, "--maps", maps], capture_output=True, text=True, cwd=ROOT).stdout)
print(subprocess.run([py, str(ROOT / "tools/analysis/oct12/watch_mech.py"), maps, "--since", since], capture_output=True, text=True, cwd=ROOT).stdout[:6000])
L = api.get("/api/v1/leaderboard")
me = [t for t in L if t["id"] == 952][0]
print(f"ladder: #{me['rank']} {me['elo']}")
subs = api.get("/api/v1/submissions")
for x in sorted(subs, key=lambda x: x["uploadedAt"])[-3:]:
    print(" ", x["id"], x["name"], x["status"], x["rating"], x["wins"], x["losses"])
