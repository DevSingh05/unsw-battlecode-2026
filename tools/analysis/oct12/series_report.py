#!/usr/bin/env python3
"""series_report.py: per-map and per-opponent record over our latest 200 series (work/oct12/series/*.json).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/series_report.py"""
import collections
import json
import math
import pathlib

W = pathlib.Path(__file__).resolve().parents[3] / "work" / "oct12"
US = 952
NEW14 = {"Athena", "Atlantis", "Caution", "Detention", "Ezam", "Hive", "Maelstrom", "Metro", "Ouroboros",
         "Thermopylae", "Troll Australia", "Trolley Problem", "Whale Song", "Trolley Problem (Buffed)"}
rows = []
for f in sorted((W / "series").glob("*.json")):
    d = json.loads(f.read_text())
    m = d["match"]
    side = "a" if m["teamAId"] == US else "b"
    opp = d["teamBName"] if side == "a" else d["teamAName"]
    oe = d["teamBElo"] if side == "a" else d["teamAElo"]
    ue = d["teamAElo"] if side == "a" else d["teamBElo"]
    ec = m.get("eloChangeA") if side == "a" else m.get("eloChangeB")
    for g in d["games"]:
        if g["status"] != "completed" or g["winner"] not in ("a", "b"):
            continue
        rows.append({"gid": g["id"], "bid": m["id"], "map": g["mapName"], "win": int(g["winner"] == side), "side": side,
                     "opp": opp, "opp_elo": oe, "our_elo": ue, "ranked": m["ranked"], "at": m["startedAt"], "elo_change": ec})
(W / "games_recent.json").write_text(json.dumps(rows))
print(f"{len(rows)} games, {rows[0]['at'][:16]} .. {max(r['at'] for r in rows)[:16]}; "
      f"W-L {sum(r['win'] for r in rows)}-{sum(1 - r['win'] for r in rows)}; ranked {sum(r['ranked'] for r in rows)}")


def exp(r):
    return 1 / (1 + 10 ** ((r["opp_elo"] - r["our_elo"]) / 400))


def tab(key, title, minn=1):
    g = collections.defaultdict(list)
    for r in rows:
        g[key(r)].append(r)
    print(f"\n| {title} | n | W-L | win% | Elo-expected% | diff pp | side A W-L | side B W-L |")
    print("|---|---|---|---|---|---|---|---|")
    out = []
    for k, L in g.items():
        if len(L) < minn:
            continue
        w = sum(r["win"] for r in L)
        e = sum(exp(r) for r in L)
        a = [r for r in L if r["side"] == "a"]
        b = [r for r in L if r["side"] == "b"]
        out.append((100 * (w - e) / len(L), k, len(L), w, e, a, b))
    for d, k, n, w, e, a, b in sorted(out):
        print(f"| {k} | {n} | {w}-{n - w} | {100 * w / n:.0f} | {100 * e / n:.0f} | {d:+.0f} | "
              f"{sum(r['win'] for r in a)}-{len(a) - sum(r['win'] for r in a)} | {sum(r['win'] for r in b)}-{len(b) - sum(r['win'] for r in b)} |")


tab(lambda r: ("NEW " if r["map"] in NEW14 else "old ") + r["map"], "map")
tab(lambda r: "new14" if r["map"] in NEW14 else "old17", "map group")
tab(lambda r: r["opp"], "opponent (n>=10)", 10)
