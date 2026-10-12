#!/usr/bin/env python3
"""build_watch.py SINCE_UTC [--base work/oct12/games_recent.json]: per-map record of every game we played since SINCE
(the live build's upload time), next to the baseline record of the earlier build on the same maps.

GET only (battles list + one detail call per new series, paced 1.1 s, cached in work/oct12/watch/).
Win% and Elo-expected% use the ratings stored with each series. "diff" = win% minus expected%, in points.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/build_watch.py 2026-10-12T19:20:06"""
import argparse
import collections
import json
import math
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

W = ROOT / "work" / "oct12" / "watch"
US = 952


def rows_of(d):
    m = d["match"]
    side = "a" if m["teamAId"] == US else "b"
    oe = d["teamBElo"] if side == "a" else d["teamAElo"]
    ue = d["teamAElo"] if side == "a" else d["teamBElo"]
    out = []
    for g in d["games"]:
        if g["status"] == "completed" and g["winner"] in ("a", "b"):
            out.append({"gid": g["id"], "map": g["mapName"], "win": int(g["winner"] == side), "opp_elo": oe, "our_elo": ue,
                        "ranked": m["ranked"], "at": m["startedAt"] or m["requestedAt"],
                        "opp": d["teamBName"] if side == "a" else d["teamAName"]})
    return out


def table(rows):
    g = collections.defaultdict(list)
    for r in rows:
        g[r["map"]].append(r)
    out = {}
    for mp, L in g.items():
        w = sum(r["win"] for r in L)
        e = sum(1 / (1 + 10 ** ((r["opp_elo"] - r["our_elo"]) / 400)) for r in L)
        out[mp] = (len(L), w, e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("since")
    ap.add_argument("--base", default="work/oct12/games_recent.json")
    ap.add_argument("--maps", default="")
    a = ap.parse_args()
    W.mkdir(parents=True, exist_ok=True)
    rows = []
    pending = 0
    for b in api.get("/api/v1/battles?limit=200"):
        if b["at"][:19] < a.since:
            continue
        if b.get("outcome") in ("live", "queued"):
            pending += 1
            continue
        p = W / f"{b['id']}.json"
        if not p.exists():
            p.write_text(json.dumps(api.get(f"/api/v1/battles/{b['id']}")))
            time.sleep(1.1)
        rows += rows_of(json.loads(p.read_text()))
    base = [r for r in json.loads((ROOT / a.base).read_text()) if r["at"][:19] < a.since]
    T, B = table(rows), table(base)
    want = [x.strip() for x in a.maps.split(",") if x.strip()]
    print(f"{len(rows)} games since {a.since} UTC ({sum(r['ranked'] for r in rows)} ranked); {pending} series still pending")
    print("| map | new n | new W-L | new win% | new expected% | new diff | base n | base win% | base diff | change in diff |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    tn = tw = te = bn = bw = be = 0
    for mp in sorted(T, key=lambda m: (m not in want, m)):
        n, w, e = T[mp]
        n0, w0, e0 = B.get(mp, (0, 0, 0))
        d = 100 * (w - e) / n
        d0 = 100 * (w0 - e0) / n0 if n0 else float("nan")
        mark = "**" if mp in want else ""
        print(f"| {mark}{mp}{mark} | {n} | {w}-{n - w} | {100 * w / n:.0f} | {100 * e / n:.0f} | {d:+.0f} | {n0} | "
              f"{100 * w0 / n0 if n0 else float('nan'):.0f} | {d0:+.0f} | {d - d0:+.0f} |")
        if not want or mp in want:
            tn += n; tw += w; te += e; bn += n0; bw += w0; be += e0
    if tn and bn:
        p1, p0 = tw / tn, bw / bn
        se = math.sqrt(p1 * (1 - p1) / tn + p0 * (1 - p0) / bn)
        print(f"{'listed' if want else 'all'} maps: new {tw}-{tn - tw} ({100 * p1:.0f}%, expected {100 * te / tn:.0f}%) vs base "
              f"{bw}-{bn - bw} ({100 * p0:.0f}%, expected {100 * be / bn:.0f}%); raw win-rate change {100 * (p1 - p0):+.0f} pp "
              f"(+-{196 * se:.0f}); change in diff {100 * ((tw - te) / tn - (bw - be) / bn):+.0f} pp")


if __name__ == "__main__":
    main()
