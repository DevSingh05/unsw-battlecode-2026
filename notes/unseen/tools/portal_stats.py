#!/usr/bin/env python3
"""Static portal statistics over .map files (read-only).

usage (from project root):
  python3 notes/unseen/tools/portal_stats.py maps/*.map
  python3 notes/unseen/tools/portal_stats.py --summary maps/gen/*.map

Per map: portal pairs, mouth-tile share, exit-in-view share, partner==mirror share,
exit dead-end share, territory lost / pearl-rate lost when portals are treated as kelp
(what v24 does on unknown maps), and mean spawn->pearl walking distance with/without portals.
"""
import pathlib
import sys
from collections import deque

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from genmaps import parse  # noqa: E402

DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]


def analyse(path):
    m = parse(pathlib.Path(path))
    w, h, nxt, sym = m["w"], m["h"], m["nxt"], m["sym"]
    N = w * h

    def plain(t, d):
        return ((t // w + DY[d]) % h) * w + (t % w + DX[d]) % w

    portal = [(t, d) for t in range(N) for d in range(4) if nxt[t * 4 + d] != -1 and nxt[t * 4 + d] != plain(t, d)]
    # crossings whose destination equals the plain tile are invisible to this test; count raw portal edges too
    mouths = {t for t, _ in portal}

    def cheb(a, b):
        ax, ay, bx, by = a % w, a // w, b % w, b // w
        dx = min(abs(ax - bx), w - abs(ax - bx))
        dy = min(abs(ay - by), h - abs(ay - by))
        return max(dx, dy)

    def mirror_t(t):
        x, y = t % w, t // w
        if sym == "x":
            return (h - 1 - y) * w + x
        if sym == "y":
            return y * w + (w - 1 - x)
        if sym == "xy":
            return (h - 1 - y) * w + (w - 1 - x)
        return -1

    def mirror_d(d):
        if sym == "x" and d in (0, 2):
            return d ^ 2
        if sym == "y" and d in (1, 3):
            return d ^ 2
        if sym == "xy":
            return d ^ 2
        return d

    in_view = 0
    partner_mirror = 0
    dead_exit = 0
    kelp_ahead = 0
    exit_on_mouth = 0
    for t, d in portal:
        x = nxt[t * 4 + d]
        if cheb(t, x) <= 3:
            in_view += 1
        # partner edge == mirror of this edge?  crossing (t,d) -> x; the partner edge is the edge between
        # plain(x, d^2) and x.  mirror of edge (t,d) is edge (mirror(t), mirror_d(d)).
        if sym in ("x", "y", "xy"):
            pt, pd = plain(x, d ^ 2), d
            mt, md = mirror_t(t), mirror_d(d)
            same = (pt == mt and pd == md) or (plain(pt, pd) == mt and (pd ^ 2) == md)
            if same:
                partner_mirror += 1
        fwd = [dd for dd in range(4) if dd != (d ^ 2) and nxt[x * 4 + dd] != -1]
        if not fwd:
            dead_exit += 1
        if nxt[x * 4 + d] == -1:
            kelp_ahead += 1
        if x in mouths:
            exit_on_mouth += 1

    # territory with portals as kelp vs real
    heads = [pts[0][1] * w + pts[0][0] for team, pts in m["dragons"] if team == 0]
    rate = [0.0] * N
    for t in range(N):
        mn, mx = m["gmin"][t], m["gmax"][t]
        rate[t] = 0.0 if mx == 0 else 2.0 / (mn + mx)

    def bfs(src, use_portals):
        dist = [-1] * N
        q = deque()
        for s in src:
            dist[s] = 0
            q.append(s)
        while q:
            t = q.popleft()
            for d in range(4):
                v = nxt[t * 4 + d]
                if v == -1:
                    continue
                if not use_portals and v != plain(t, d):
                    continue
                if dist[v] < 0:
                    dist[v] = dist[t] + 1
                    q.append(v)
        return dist

    full = bfs(heads, True)
    blind = bfs(heads, False)
    reach_full = sum(1 for t in range(N) if full[t] >= 0)
    reach_blind = sum(1 for t in range(N) if blind[t] >= 0)
    rate_full = sum(rate[t] for t in range(N) if full[t] >= 0)
    rate_blind = sum(rate[t] for t in range(N) if blind[t] >= 0)
    # rate-weighted mean distance over tiles reachable both ways
    num_f = num_b = den = 0.0
    for t in range(N):
        if full[t] >= 0 and blind[t] >= 0 and rate[t] > 0:
            num_f += rate[t] * full[t]
            num_b += rate[t] * blind[t]
            den += rate[t]
    P = len(portal)
    return dict(
        name=pathlib.Path(path).stem, w=w, h=h, sym=sym, pairs=P // 4 if P else 0, cross=P,
        mouth_pct=100.0 * len(mouths) / max(1, reach_full),
        in_view=100.0 * in_view / P if P else 0, pmirror=100.0 * partner_mirror / P if P else 0,
        dead=100.0 * dead_exit / P if P else 0, kelp_ahead=100.0 * kelp_ahead / P if P else 0,
        exit_mouth=100.0 * exit_on_mouth / P if P else 0,
        terr_lost=100.0 * (reach_full - reach_blind) / max(1, reach_full),
        rate_lost=100.0 * (rate_full - rate_blind) / max(1e-9, rate_full),
        dist_f=num_f / den if den else 0, dist_b=num_b / den if den else 0,
    )


def main():
    args = sys.argv[1:]
    summary = False
    if args and args[0] == "--summary":
        summary, args = True, args[1:]
    rows = [analyse(p) for p in args]
    if not summary:
        print(f"{'map':22s} {'size':7s} sym pairs cross mouth% inview% pmirr% dead% kelpAh% exitMouth% terrLost% rateLost% dist(p/np)")
        for r in rows:
            print(f"{r['name']:22s} {r['w']:>3d}x{r['h']:<3d} {r['sym']:3s} {r['pairs']:5d} {r['cross']:5d} {r['mouth_pct']:6.1f} "
                  f"{r['in_view']:7.1f} {r['pmirror']:6.1f} {r['dead']:5.1f} {r['kelp_ahead']:7.1f} "
                  f"{r['exit_mouth']:9.1f} {r['terr_lost']:9.1f} {r['rate_lost']:9.1f} {r['dist_f']:5.1f}/{r['dist_b']:<5.1f}")
    withp = [r for r in rows if r["cross"]]
    n = len(rows)
    print(f"\n{n} maps, {len(withp)} with portals ({100.0 * len(withp) / max(1, n):.0f}%)")
    if withp:
        def avg(k):
            return sum(r[k] for r in withp) / len(withp)
        print(f"among portal maps: pairs {avg('pairs'):.1f}, mouth% {avg('mouth_pct'):.1f}, exit in view {avg('in_view'):.1f}%, "
              f"partner==mirror {avg('pmirror'):.1f}%, dead exit {avg('dead'):.1f}%, kelp ahead {avg('kelp_ahead'):.1f}%, "
              f"territory lost as-kelp {avg('terr_lost'):.1f}%, rate lost {avg('rate_lost'):.1f}%, "
              f"maps losing >5% rate: {sum(1 for r in withp if r['rate_lost'] > 5)}")


if __name__ == "__main__":
    main()
