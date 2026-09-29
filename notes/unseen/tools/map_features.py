#!/usr/bin/env python3
"""Static features of .map files, split into what a dragon could measure at
runtime (round 0 / early) and whole-map truth. Read-only; no games are run.

Usage (from project root):
  python3 notes/unseen/tools/map_features.py maps/devil.map maps/gen/*.map
  python3 notes/unseen/tools/map_features.py --csv maps/*.map > out.csv
"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from genmaps import parse  # noqa: E402


def feats(path):
    m = parse(pathlib.Path(path))
    w, h = m["w"], m["h"]
    n = w * h
    nxt = m["nxt"]
    gmin, gmax = m["gmin"], m["gmax"]

    def plain(t, d):
        x, y = t % w, t // w
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][d]
        return ((y + dy) % h) * w + (x + dx) % w

    blocked = sum(1 for v in nxt if v < 0)
    portal_sides = sum(1 for t in range(n) for d in range(4) if nxt[t * 4 + d] >= 0 and nxt[t * 4 + d] != plain(t, d))
    deg = [sum(1 for d in range(4) if nxt[t * 4 + d] >= 0) for t in range(n)]
    dead = sum(1 for t in range(n) if deg[t] == 1)
    corridor = sum(1 for t in range(n) if deg[t] == 2)

    spawn = [t for t in range(n) if gmax[t] > 0]
    rate = sum(2.0 / (gmin[t] + gmax[t]) for t in spawn if gmin[t] + gmax[t] > 0)
    hot = [t for t in spawn if gmax[t] <= 10]
    hot_rate = sum(2.0 / (gmin[t] + gmax[t]) for t in hot)
    dead_hot = [t for t in hot if deg[t] <= 2]

    starts = collections.Counter(team for team, _ in m["dragons"])
    lens = collections.defaultdict(list)
    for team, pts in m["dragons"]:
        lens[team].append(len(pts))
    a_heads = [pts[0][1] * w + pts[0][0] for team, pts in m["dragons"] if team == 0]
    b_cells = {y * w + x for team, pts in m["dragons"] if team == 1 for x, y in pts}

    def bfs(src, use_portals=True):
        dist = [-1] * n
        q = collections.deque()
        for s in src:
            dist[s] = 0
            q.append(s)
        while q:
            t = q.popleft()
            for d in range(4):
                v = nxt[t * 4 + d]
                if v < 0:
                    continue
                if not use_portals and v != plain(t, d):
                    continue
                if dist[v] < 0:
                    dist[v] = dist[t] + 1
                    q.append(v)
        return dist

    da = bfs(a_heads)
    sd = min((da[c] for c in b_cells if da[c] >= 0), default=-1)
    reach = sum(1 for v in da if v >= 0)
    da_np = bfs(a_heads, False)
    sd_np = min((da_np[c] for c in b_cells if da_np[c] >= 0), default=-1)

    # round-0 view of team A's dragons (7x7 around each head): what a dragon could measure at once
    seen = set()
    for hd in a_heads:
        hx, hy = hd % w, hd // w
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                seen.add(((hy + dy) % h) * w + (hx + dx) % w)
    v_sp = [t for t in seen if gmax[t] > 0]
    v_rate = sum(2.0 / (gmin[t] + gmax[t]) for t in v_sp if gmin[t] + gmax[t] > 0)
    v_block = sum(1 for t in seen for d in range(4) if nxt[t * 4 + d] < 0) / (4 * len(seen))
    return dict(
        name=m["name"], W=w, H=h, N=n, ul=m["unit_limit"], sym=m["sym"],
        startsA=starts[0], lenA=sum(lens[0]), maxLenA=max(lens[0]) if lens[0] else 0,
        kelp=round(blocked / (4 * n), 3), portals=portal_sides // 2, dead=dead,
        corr=round(corridor / n, 3),
        spawnFrac=round(len(spawn) / n, 3), rate=round(rate, 2), ratePerTile1k=round(1000 * rate / n, 1),
        hot=len(hot), hotShare=round(hot_rate / rate, 2) if rate else 0, deadHot=len(dead_hot),
        startDist=sd, startDistNoPortal=sd_np, reachFrac=round(reach / n, 2),
        tilesPerStart=round(n / max(1, starts[0] + starts[1]), 0),
        v_spawnFrac=round(len(v_sp) / len(seen), 2), v_rate1k=round(1000 * v_rate / len(seen), 1),
        v_kelp=round(v_block, 3),
    )


def main():
    args = sys.argv[1:]
    csv = False
    if args and args[0] == "--csv":
        csv = True
        args = args[1:]
    rows = [feats(p) for p in args]
    keys = list(rows[0].keys())
    if csv:
        print(",".join(keys))
        for r in rows:
            print(",".join(str(r[k]) for k in keys))
        return
    widths = {k: max(len(k), *(len(str(r[k])) for r in rows)) for k in keys}
    print(" ".join(k.rjust(widths[k]) for k in keys))
    for r in rows:
        print(" ".join(str(r[k]).rjust(widths[k]) for k in keys))


if __name__ == "__main__":
    main()
