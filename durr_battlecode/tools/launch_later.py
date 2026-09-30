#!/usr/bin/env python3
"""Retry challenges that hit the hourly cap, then collect every game in the file.

usage: launch_later.py challenges.json template.json OUTDIR
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import api  # noqa: E402

import os
MAPS = [int(x) for x in os.environ.get("CH_MAPS", "9,20,21,11,17,7,4,19,13,15").split(",")]


def main():
    path, template, out = pathlib.Path(sys.argv[1]), json.loads(pathlib.Path(sys.argv[2]).read_text()), sys.argv[3]
    log = json.loads(path.read_text())
    done = {c["teamId"] for c in log}
    todo = [t for t in template if t["teamId"] not in done]
    while todo:
        t = todo[0]
        try:
            r = api.post("/api/v1/battles", {"teamId": t["teamId"], "ranked": False, "mapIds": MAPS})
            log.append({**t, "resp": r})
            path.write_text(json.dumps(log, indent=1))
            print("launched", t["team"], flush=True)
            todo.pop(0)
        except Exception as e:  # noqa: BLE001
            print("waiting:", e, flush=True)
            time.sleep(120)
    subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("collect.py")), str(path), out])


if __name__ == "__main__":
    main()
