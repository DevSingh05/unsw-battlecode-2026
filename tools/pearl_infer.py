#!/usr/bin/env python3
"""Pearl-bed inference for server replays whose map version we do not have (used by tools/decision_replay.py).

Server replays carry the map with every TILE spawn gap zeroed. When the server's pearl layout differs from our
copy of the map (Devil and Schooltime were re-balanced on the server on 5 Oct, Slithery Fight on 4 Oct), the
engine rebuild needs the real beds and gaps. This module emulates the engine's pearl tick (engine pearls.cc:
mt19937 seeded from the match seed, one draw per owner bed at init and per spawn attempt, mirrored beds share a
countdown) against the observed game (pearls and bodies tracked from the replay events), and fits each bed's
(minGap, maxGap) from a candidate list so the emulated spawn events equal the server's.

    python3 tools/pearl_infer.py --auto --base maps/server_live/devil.map     # fit from all cached replays
    python3 tools/pearl_infer.py GAME_ID [...] --base maps/server_live/devil.map --fit -o out.map
    python3 tools/pearl_infer.py GAME_ID [...] --base some.map                # check a layout against games
"""
import argparse
import glob
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import replay_decode as RD  # noqa: E402


class MT19937:
    def __init__(self, seed):
        self.mt = [0] * 624
        self.i = 624
        self.mt[0] = seed & 0xffffffff
        for k in range(1, 624):
            self.mt[k] = (1812433253 * (self.mt[k - 1] ^ (self.mt[k - 1] >> 30)) + k) & 0xffffffff

    @classmethod
    def from_seq(cls, words):
        """std::seed_seq(words) -> generate(624 words) -> mt19937(seq)."""
        n = 624
        s = len(words)
        t = 11  # n >= 623
        p = (n - t) // 2
        q = p + t
        m = max(s + 1, n)
        b = [0x8b8b8b8b] * n
        T = lambda x: x ^ (x >> 27)  # noqa: E731
        for k in range(m):
            r1 = (1664525 * T(b[k % n] ^ b[(k + p) % n] ^ b[(k - 1) % n])) & 0xffffffff
            if k == 0:
                r2 = (r1 + s) & 0xffffffff
            elif k <= s:
                r2 = (r1 + k % n + words[k - 1]) & 0xffffffff
            else:
                r2 = (r1 + k % n) & 0xffffffff
            b[(k + p) % n] = (b[(k + p) % n] + r1) & 0xffffffff
            b[(k + q) % n] = (b[(k + q) % n] + r2) & 0xffffffff
            b[k % n] = r2
        for k in range(m, m + n):
            r3 = (1566083941 * T((b[k % n] + b[(k + p) % n] + b[(k - 1) % n]) & 0xffffffff)) & 0xffffffff
            r4 = (r3 - k % n) & 0xffffffff
            b[(k + p) % n] ^= r3
            b[(k + q) % n] ^= r4
            b[k % n] = r4
        o = cls(0)
        o.mt = b[:]
        # mt19937 seeding from seed_seq: if the top bit pattern is all zero it is fixed up; ignore (prob ~0)
        o.i = 624
        return o

    def __call__(self):
        if self.i >= 624:
            mt = self.mt
            for k in range(624):
                y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7fffffff)
                mt[k] = mt[(k + 397) % 624] ^ (y >> 1) ^ (0x9908b0df if y & 1 else 0)
            self.i = 0
        y = self.mt[self.i]
        self.i += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= y >> 18
        return y & 0xffffffff


class MT64:
    """std::mt19937_64(seed): what the 1.2.x engine draws pearl gaps with (verified against engine output)."""
    M = (1 << 64) - 1

    def __init__(self, seed):
        M = self.M
        self.mt = [0] * 312
        self.mt[0] = seed & M
        for i in range(1, 312):
            self.mt[i] = (6364136223846793005 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 62)) + i) & M
        self.i = 312

    def __call__(self):
        if self.i >= 312:
            mt = self.mt
            for k in range(312):
                y = (mt[k] & 0xFFFFFFFF80000000) | (mt[(k + 1) % 312] & 0x7FFFFFFF)
                mt[k] = mt[(k + 156) % 312] ^ (y >> 1) ^ (0xB5026F5AA96619E9 if y & 1 else 0)
            self.i = 0
        x = self.mt[self.i]
        self.i += 1
        x ^= (x >> 29) & 0x5555555555555555
        x ^= (x << 17) & 0x71D67FFFEDA60000
        x ^= (x << 37) & 0xFFF7EEE000000000
        x ^= x >> 43
        return x & self.M


SEEDERS = {
    "mt64": lambda s: MT64(s),
    "lo32": lambda s: MT19937(s & 0xffffffff),
    "hi32": lambda s: MT19937(s >> 32),
    "seq_lo_hi": lambda s: MT19937.from_seq([s & 0xffffffff, s >> 32]),
    "seq_hi_lo": lambda s: MT19937.from_seq([s >> 32, s & 0xffffffff]),
}


def parse_map(text):
    W = H = 0
    sym = None
    beds = {}
    for ln in text.split("\n"):
        f = ln.split()
        if not f:
            continue
        if f[0] == "MAP":
            W, H = int(f[1]), int(f[2])
        elif f[0] == "SYMMETRY":
            sym = f[1]
        elif f[0] == "TILE" and f[4] != "0":
            beds[(int(f[1]), int(f[2]))] = (int(f[3]), int(f[4]))
    return W, H, sym, beds


def mirror(W, H, sym, p):
    x, y = p
    if sym == "x":
        return (x, H - 1 - y)
    if sym == "y":
        return (W - 1 - x, y)
    if sym == "xy":
        return (W - 1 - x, H - 1 - y)
    return p


def observed(o):
    """Per round: tick spawns (list of tiles in order) and the blocked tiles at tick time (pearl or dragon)."""
    import replay_sim as RS
    m = RS.Map(o["map"])
    body = {i: list(pts) for i, (t, pts) in enumerate(m.dragons)}
    alive = set(body)
    pearls = set()
    rounds = []
    cur = None
    inturns = False
    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            occ = set()
            for i in alive:
                occ.update(body[i])
            cur = {"round": e["round"], "spawns": [], "pearls": set(pearls), "occ": occ}
            rounds.append(cur)
            inturns = False
        elif t == "turnStart":
            inturns = True
        elif t == "tileChange":
            if e["hasPearl"]:
                pearls.add(e["tile"])
                if not inturns and cur is not None:
                    cur["spawns"].append(e["tile"])
            else:
                pearls.discard(e["tile"])
        elif t == "dragonUpdate":
            b = body.setdefault(e["id"], [])
            b.insert(0, e["head"])
            while b and b[-1] != e["tail"]:
                b.pop()
        elif t == "dragonSplit":
            body[e["parent"]] = list(e["parentBody"])
            body[e["child"]] = list(e["childBody"])
            alive.add(e["child"])
        elif t == "dragonDeath":
            alive.discard(e["id"])
    return rounds


def emulate(W, H, sym, beds, rng, obs, stop_at_mismatch=True):
    """Run the pearl process with the observed board state; return (first mismatch round or None, detail)."""
    owners = []
    for y in range(H):
        for x in range(W):
            p = (x, y)
            if p not in beds:
                continue
            q = mirror(W, H, sym, p)
            if q[1] * W + q[0] >= y * W + x:
                owners.append((p, q))
    cd = {}
    for p, q in owners:
        mn, mx = beds[p]
        g = mn + rng() % (mx - mn + 1)
        cd[p] = g
    for R in obs:
        pearls = set(R["pearls"])
        got = []
        for p, q in owners:
            cd[p] -= 1
            if cd[p] > 0:
                continue
            for t in ((p, q) if q != p else (p,)):
                if t not in pearls and t not in R["occ"]:
                    pearls.add(t)
                    got.append(t)
            mn, mx = beds[p]
            cd[p] = mn + rng() % (mx - mn + 1)
        if got != R["spawns"]:
            return R["round"], (got, R["spawns"])
    return None, None


PAIRS = [(1, 1), (1, 5), (1, 10), (1, 20), (1, 30), (1, 50), (1, 100), (1, 150), (1, 200), (1, 250), (1, 255),
         (1, 300), (1, 385), (1, 500), (1, 600), (1, 750), (1, 769), (1, 1000), (1, 2000), (1, 2559), (1, 3849),
         (5, 30), (8, 20), (8, 30), (10, 30), (20, 50), (20, 80), (20, 200), (40, 200), (100, 500), (150, 250),
         (250, 500), (400, 500), (480, 490)]


GRID = [(mn, mx) for mn in (1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 400)
        for mx in sorted(set(range(5, 1001, 5)) | set(range(1000, 4001, 50)) | {1, 2, 3, 4, 255, 385, 769, 2559, 3849})
        if mx >= mn]


def score(W, H, sym, beds, games):
    """Smallest first-mismatch round over the games (999 = all consistent)."""
    worst = 999
    for seed, obs in games:
        r, _ = emulate(W, H, sym, beds, MT64(seed), obs)
        if r is not None:
            worst = min(worst, r)
    return worst


def fit(W, H, sym, base, games, log=print, max_steps=400, max_nodes=300000):
    """Greedy repair of the pearl beds so the emulated tick spawns equal the observed ones in every game.
    Bed set = tiles seen spawning at a tick (closed under the mirror); pairs start from the base map."""
    seen = set()
    for _, obs in games:
        for R in obs:
            seen.update(R["spawns"])
    seen |= {mirror(W, H, sym, t) for t in seen}
    pairs = sorted(set(PAIRS) | set(base.values()))
    known = set(pairs)
    common = max(set(base.values()), key=list(base.values()).count) if base else (1, 1)
    cand = seen | set(base)
    owners = [t for t in sorted(cand, key=lambda p: (p[1], p[0]))
              if (lambda q: q[1] * W + q[0] >= t[1] * W + t[0])(mirror(W, H, sym, t))]
    # Init draws: kept owner k takes draw k of the stream, so its first attempt round is min + r_k % span - 1;
    # that must equal its first tick spawn, or fall on a round where both tiles were blocked (never spawned:
    # every attempt before r500 blocked). Walk owners in order; a base bed never seen spawning is kept only if
    # its base gaps fit (else it was removed on the server); a seen bed takes the first fitting pair.
    streams = []
    for seed, obs in games:
        rng = MT64(seed)
        streams.append([rng() for _ in range(len(owners) + 1)])
    mins = sorted({1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 40, 50, 100, 150, 250, 400, 480} | {p[0] for p in known})
    infos = {}
    for b in owners:
        q = mirror(W, H, sym, b)
        per = []
        for gi, (seed, obs) in enumerate(games):
            first = next((R["round"] for R in obs if b in R["spawns"] or q in R["spawns"]), None)
            blocked = [(b in R["pearls"] or b in R["occ"]) and (q in R["pearls"] or q in R["occ"]) for R in obs]
            per.append((first, blocked))
        infos[b] = per

    def ok(b, idx, mn, mx):
        sp = mx - mn + 1
        for gi, (first, blocked) in enumerate(infos[b]):
            r = streams[gi][idx]
            a = mn + r % sp - 1
            if first is None:
                if a < len(blocked) and not blocked[a]:
                    return False
            elif a != first and not (a < first and blocked[a]):
                return False
        return True

    def choices(b, idx):
        """Options for owner b at draw idx: list of pair (keep) or None (drop, base-only beds)."""
        out = []
        if b not in seen:
            if ok(b, idx, *base[b]):
                out.append(base[b])
            out.append(None)
            return out
        if b in base and ok(b, idx, *base[b]):
            out.append(base[b])
        out += [c for c in pairs if c not in out and ok(b, idx, *c)]
        if not out:  # gaps never used in our map files: try "round" values
            out = [c for c in GRID if ok(b, idx, *c)][:4]
        return out

    # depth-first over owners (keep before drop, base gaps before others); backtrack when a seen bed fits no pair
    nodes = 0
    stack = [(0, 0, None)]  # (owner index, draw index, chain of (bed, choice, parent))
    best_chain, best_k = None, -1
    while stack and nodes < max_nodes:
        k, idx, chain = stack.pop()
        nodes += 1
        if k > best_k:
            best_k, best_chain = k, chain
        if k == len(owners):
            best_chain = chain
            break
        b = owners[k]
        for c in reversed(choices(b, idx)):
            stack.append((k + 1, idx + (c is not None), (b, c, chain)))
    best_assign = {}
    while best_chain is not None:
        b, c, best_chain = best_chain
        best_assign[b] = c
    beds = {}
    for b in owners:
        c = best_assign.get(b)
        if c is None and b in seen:
            c = base.get(b, common)  # DFS did not reach it: placeholder
        if c is not None:
            beds[b] = beds[mirror(W, H, sym, b)] = c
    log(f"fit: init search {nodes} nodes, assigned {best_k}/{len(owners)} owners")
    owners = [t for t in owners if t in beds]
    cur = score(W, H, sym, beds, games)
    log(f"fit: {len(beds)} beds ({len(set(beds) - set(base))} new, {len(set(base) - set(beds))} dropped, "
        f"{sum(1 for t in beds if t in base and beds[t] != base[t])} re-gapped vs base), start score r{cur}")
    steps = 0
    while cur < 999 and steps < max_steps:
        steps += 1
        # culprits first: beds whose spawn differs at the first mismatch
        diff = set()
        for seed, obs in games:
            r, det = emulate(W, H, sym, beds, MT64(seed), obs)
            if r == cur and det:
                diff |= set(det[0]) ^ set(det[1])
        diff |= {mirror(W, H, sym, t) for t in diff}
        first = [b for b in owners if b in diff]
        best = (cur, None)
        idx_of = {b: k for k, b in enumerate(o for o in owners if o in beds)}
        for gi_, group in enumerate((first, [b for b in owners if b not in diff])):
            for b in group:
                if b not in beds:
                    continue
                old = beds[b]
                opts = list(pairs)
                if gi_ == 0 and b in infos:  # culprits: also off-list gaps that fit the bed's init draw
                    opts += [c for c in GRID if c not in opts and ok(b, idx_of[b], *c)][:12]
                for c in opts:
                    if c == old:
                        continue
                    beds[b] = c
                    q = mirror(W, H, sym, b)
                    beds[q] = c
                    sc = score(W, H, sym, beds, games)
                    beds[b] = beds[q] = old
                    if sc > best[0]:
                        best = (sc, (b, c))
            if best[1] is not None:
                break
        if best[1] is None:
            log(f"fit: stuck at r{cur} (diff tiles {sorted(diff)[:8]})")
            return beds, cur
        b, c = best[1]
        beds[b] = beds[mirror(W, H, sym, b)] = c
        log(f"fit: bed {b} -> {c}: r{cur} -> r{best[0]}")
        cur = best[0]
    return beds, cur


def write_map(base_text, beds):
    out = []
    for ln in base_text.split("\n"):
        f = ln.split()
        if f and f[0] == "TILE":
            t = (int(f[1]), int(f[2]))
            mn, mx = beds.get(t, (0, 0))
            ln = f"TILE {t[0]} {t[1]} {mn} {mx}"
        out.append(ln)
    return "\n".join(out)


def load(gid):
    p = glob.glob(str(ROOT / "replays" / "**" / f"{gid}.replay"), recursive=True)
    return RD.load(p[0])


ALT_DIR = ROOT / "replays" / "decision_replay" / "maps"


def cached_games(map_name, limit=0):
    """(gid, path) of cached server replays of this map (attribution cache replays/ab_server/games.json)."""
    import json
    import os
    gm = json.loads((ROOT / "replays" / "ab_server" / "games.json").read_text())["games"]
    out, seen = [], set()
    for f in sorted(glob.glob(str(ROOT / "replays" / "**" / "*.replay"), recursive=True)):
        gid = os.path.basename(f)[:-7]
        if gid in seen or gid not in gm or gm[gid]["mapName"] != map_name:
            continue
        seen.add(gid)
        out.append((gid, f))
        if limit and len(out) >= limit:
            break
    return out


def auto(base_path, log=print, limit=120, seed_games=4, rounds=4):
    """Fit the server's alternate pearl layout of a map from cached replays that the base layout does not
    explain; add still-unexplained games and refit until every cached game is explained (or `rounds` runs).
    Writes replays/decision_replay/maps/<base>_alt.map."""
    base_text = pathlib.Path(base_path).read_text()
    W, H, sym, base = parse_map(base_text)
    name = next(ln[9:].strip() for ln in base_text.split("\n") if ln.startswith("MAP_NAME "))
    obs = {}
    bad = []
    games = cached_games(name, limit)
    for gid, f in games:
        o = RD.load(f)
        obs[gid] = (o["seed"], observed(o))
        if emulate(W, H, sym, base, MT64(o["seed"]), obs[gid][1])[0] is not None:
            bad.append(gid)
    log(f"{name}: {len(games)} cached games, {len(bad)} not explained by {base_path}")
    if not bad:
        return None
    use = bad[:seed_games]
    fitted = None
    for it in range(rounds):
        fitted, sc = fit(W, H, sym, base, [obs[g] for g in use], log=lambda *a: None)
        left = [g for g in bad if emulate(W, H, sym, fitted, MT64(obs[g][0]), obs[g][1])[0] is not None]
        log(f"  fit {it + 1} on {len(use)} games: {'consistent' if sc == 999 else 'stuck r%d' % sc}; "
            f"explains {len(bad) - len(left)}/{len(bad)}")
        if not left:
            break
        use = use + left[:4]
    ALT_DIR.mkdir(parents=True, exist_ok=True)
    out = ALT_DIR / (pathlib.Path(base_path).stem + "_alt.map")
    out.write_text(write_map(base_text, fitted))
    log(f"  wrote {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games", nargs="*")
    ap.add_argument("--base", required=True)
    ap.add_argument("--auto", action="store_true", help="fit the alternate layout from all cached replays")
    ap.add_argument("--seeder")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("-o")
    a = ap.parse_args()
    if a.auto:
        auto(a.base)
        return
    base_text = pathlib.Path(a.base).read_text()
    W, H, sym, beds = parse_map(base_text)
    if a.fit:
        games = []
        for g in a.games:
            o = load(g)
            games.append((o["seed"], observed(o)))
        fitted, sc = fit(W, H, sym, beds, games)
        print("final", "CONSISTENT in all games" if sc == 999 else f"first mismatch r{sc}")
        if a.o:
            pathlib.Path(a.o).write_text(write_map(base_text, fitted))
            print("wrote", a.o)
        return
    for g in a.games:
        o = load(g)
        obs = observed(o)
        for name, mk in SEEDERS.items():
            if a.seeder and name != a.seeder:
                continue
            r, det = emulate(W, H, sym, beds, mk(o["seed"]), obs)
            print(g, name, "OK" if r is None else f"mismatch r{r} {str(det)[:200]}")


if __name__ == "__main__":
    main()
