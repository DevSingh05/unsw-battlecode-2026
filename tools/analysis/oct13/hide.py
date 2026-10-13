#!/usr/bin/env python3
"""hide.py [--top 3] [--emit FILE]: read work/oct13/traffic/ (traffic.py) and report, per map,
  - how often a tile on the home side is inside an enemy lunge range (share of sampled rounds from r30),
  - the same for the area our leash uses (within 8 steps of the queen's start), for where queens actually stood,
    and for where the queens that lived to the end stood,
  - the quietest spots: tiles (2+ exits, at most --maxd plain steps from the queen's start, no portal on the way) whose
    2-step neighbourhood (at least 6 tiles) has the lowest worst-tile share. Shares come from the side that LOST the game
    by default (--field lost): a spot must stay quiet when we are the weaker team.
Also the check that exposure matters: queens grouped by the exposure they lived in, with their survival.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct13/hide.py"""
import argparse
import collections
import json
import pathlib
import re
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes" / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "analysis" / "oct13"))
import replay_sim as RS  # noqa: E402
import traffic as TR  # noqa: E402

T = ROOT / "work" / "oct13" / "traffic"
key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())


def ball(nb, t, r):
    return TR.bfs_from(nb, t, r)


def plain_graph(m):
    """Neighbours by plain steps only (no portal crossings): the graph the queen's leash walks on."""
    idx = lambda p: p[1] * m.w + p[0]
    nb = [[] for _ in range(m.w * m.h)]
    for y in range(m.h):
        for x in range(m.w):
            for d in "NESW":
                q = m.step((x, y), d)
                if q is not None and q == m.wrap(x + RS.DV[d][0], y + RS.DV[d][1]):
                    nb[idx((x, y))].append(idx(q))
    return nb


def block2(nb, t):
    """True when t is a corner of a 2x2 block whose four tiles are joined in a ring (room for a short queen to circle)."""
    for a in nb[t]:
        for b in nb[t]:
            if a < b and any(c != t and c in nb[b] for c in nb[a]):
                return True
    return False


def spots(g, nb, maxd=10 ** 9, top=3, rad=2, field="lost", pnb=None):
    den = {"lunge": g["n"], "lost": g.get("nl", 0), "early": g.get("ne", 0)}[field] or 1
    E = [v / den for v in g[field]]
    ds = TR.bfs_from(pnb or nb, g["spawn"])
    out = []
    for t in range(len(E)):
        if len(nb[t]) < 2 or t not in ds or ds[t] > maxd:
            continue
        B = ball(pnb or nb, t, rad)
        if len(B) < 6 or not block2(pnb or nb, t):
            continue
        out.append((max(E[u] for u in B), ds[t], t))
    out.sort()
    picked = []
    for s, d, t in out:
        if all(TR.bfs_from(nb, t, 6).get(p[2]) is None for p in picked):
            picked.append((s, d, t))
        if len(picked) >= top:
            break
    return picked, E, ds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--emit", default="")
    ap.add_argument("--field", default="lost", help="lost (side that lost the game; default), lunge (all), early (before r200)")
    ap.add_argument("--maxd", type=int, default=30, help="most plain steps from the queen's start")
    a = ap.parse_args()
    maps = {key(p.stem): p for p in (ROOT / "maps" / "server_live31").glob("*.map")}
    Q = json.loads((T / "queens.json").read_text())
    print("== exposure and survival (queens with 10+ sampled rounds; exposure = share of her rounds inside an enemy lunge range)")
    rows = [r for r in Q if r["rounds"] >= 10]
    for lo, hi in ((0, 0.01), (0.01, 0.03), (0.03, 0.06), (0.06, 0.12), (0.12, 0.25), (0.25, 1.01)):
        L = [r for r in rows if lo <= r["lunge"] < hi]
        if L:
            print(f"  exposure {lo:.2f}-{hi:.2f}: {len(L):4d} queens, alive at the end {100 * sum(r['death'] is None for r in L) / len(L):3.0f}%, "
                  f"median steps from start {st.median(r['dist'] for r in L):.0f}")
    emit = {}
    print("\n| map | games | whole home side | leash area (8 steps) | where queens stood | where surviving queens stood | queens alive | quietest spots: exposure @ steps from start (x,y) |")
    print("|---|---|---|---|---|---|---|---|")
    for f in sorted(T.glob("*.json")):
        if f.name == "queens.json":
            continue
        g = json.loads(f.read_text())
        mk = key(f.stem)
        if mk not in maps:
            continue
        m = RS.Map(maps[mk].read_text())
        nb = TR.graph(m)
        pnb = plain_graph(m)
        picked, E, ds = spots(g, nb, maxd=a.maxd, top=a.top, field=a.field, pnb=pnb)
        near10, _, _ = spots(g, nb, maxd=12, top=1, field=a.field, pnb=pnb)
        home = [E[t] for t in ds if ds[t] <= 30]
        leash = [E[t] for t in ds if ds[t] <= 8]
        El = [v / (g["n"] or 1) for v in g["lunge"]]
        Ee = [v / (g.get("ne") or 1) for v in g["early"]]
        qo, qa = g["qocc"], g["qocc_alive"]
        wq = sum(E[t] * qo[t] for t in range(len(E))) / max(1, sum(qo))
        wa = sum(E[t] * qa[t] for t in range(len(E))) / max(1, sum(qa)) if sum(qa) else float("nan")
        mq = [r for r in Q if key(r["map"]) == mk]
        alive = sum(r["death"] is None for r in mq)
        cell = "; ".join(f"{100 * s:.1f}% (all games {100 * El[t]:.1f}%, before r200 {100 * Ee[t]:.1f}%) @{d} ({t % m.w},{t // m.w})" for s, d, t in picked)
        cell += " | within 12: " + "; ".join(f"{100 * s:.1f}% @{d} ({t % m.w},{t // m.w})" for s, d, t in near10)
        print(f"| {m.name or f.stem} | {g['games']} | {100 * st.mean(home):.1f}% | {100 * st.mean(leash):.1f}% | {100 * wq:.1f}% | {100 * wa:.1f}% | {alive}/{len(mq)} | {cell} |")
        sig = TR.symmetry(m)
        emit[m.name or f.stem] = {"w": m.w, "h": m.h, "spawn": [g["spawn"], sig[g["spawn"]]], "leash": st.mean(leash), "stood": wq,
                                  "spots": [{"exp": s, "steps": d, "tile": [t, sig[t]], "xy": [t % m.w, t // m.w]} for s, d, t in picked],
                                  "near": [{"exp": s, "steps": d, "tile": [t, sig[t]], "xy": [t % m.w, t // m.w]} for s, d, t in near10]}
    if a.emit:
        pathlib.Path(a.emit).write_text(json.dumps(emit, indent=1))


if __name__ == "__main__":
    main()
