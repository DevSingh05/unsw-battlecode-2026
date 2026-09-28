#!/usr/bin/env python3
"""Tiny client for the Battlecode API using the key saved by `unswbc auth set`."""
import json
import pathlib
import sys
import urllib.request

BASE = "https://game.battlecode.au"
UA = {"User-Agent": "unswbc-tools/1.0 (curl-compatible)"}


def key():
    d = json.loads((pathlib.Path.home() / ".unswbc" / "keys.json").read_text())
    v = list(d.values())[0]
    return v if isinstance(v, str) else v.get("key")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key()}", **UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json", **UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def download_replay(game_id, out):
    # public endpoint, redirects to a signed URL; no auth header needed
    with urllib.request.urlopen(urllib.request.Request(f"{BASE}/api/matches/{game_id}/replay", headers=UA), timeout=60) as r:
        pathlib.Path(out).write_bytes(r.read())


if __name__ == "__main__":
    print(json.dumps(get(sys.argv[1]), indent=1)[:20000])
