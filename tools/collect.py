#!/usr/bin/env python3
"""Wait for challenge games to finish, download replays, summarise per opponent and map.

usage: collect.py challenges.json OUTDIR
"""
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "notes" / "tools"))
import api  # noqa: E402
from replay_decode import load  # noqa: E402

US = "Cache me outside"


def main():
    log = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    pending = {gid: c for c in log for gid in c["resp"]["ids"]}
    rows = []
    while pending:
        for gid in list(pending):
            d = api.get(f"/api/v1/battles/{gid}")
            m = d["match"]
            if m["status"] != "completed":
                continue
            c = pending.pop(gid)
            us_a = d["teamAName"] == US
            p = out / f"{gid}.replay"
            try:
                api.download_replay(gid, p)
                r = load(p)["result"]
            except Exception as e:  # noqa: BLE001
                r = {"error": str(e)}
            won = (m["winner"] == "a") == us_a if m["winner"] else None
            us, them = ("A", "B") if us_a else ("B", "A")
            rows.append({"id": gid, "opp": c["team"], "rank": c["rank"], "map": d["mapName"],
                         "win": won, "end": r.get("endReason"), "us": r.get(us), "them": r.get(them)})
            print(gid, c["team"], d["mapName"], "WIN" if won else "LOSS" if won is False else "DRAW",
                  r.get("endReason"), r.get(us), r.get(them), flush=True)
        if pending:
            time.sleep(30)
    (out / "summary.json").write_text(json.dumps(rows, indent=1))
    print("DONE", sum(1 for r in rows if r["win"]), "wins of", len(rows))


if __name__ == "__main__":
    main()
