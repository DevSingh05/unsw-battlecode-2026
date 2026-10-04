#!/usr/bin/env python3
"""Server A/B analyzer: compare our submissions (team 952) on live server games, controlling for opponent strength.

usage (run from the project root):
  python3 tools/ab_server.py v44 v55                       # A=v44 (baseline), B=v55
  python3 tools/ab_server.py v44 v49 v55                   # each later one vs the first
  python3 tools/ab_server.py v44@15096 v49                 # pick one upload of a reused name (id after @)
  python3 tools/ab_server.py v44 v55 --since v55=2026-10-03T12:00 --until v44=2026-10-03T10:00
  options: --ref pooled|self|<number>   our rating used in the Elo expectation (default pooled)
           --min-map 5      min games per map per side for the paired comparison
           --grace 300      seconds skipped after each upload (games already queued for the old version)
           --ends           also fetch per-game scores to split elimination vs round-500 queen tiebreak
                            (1 API call per new game, cached; ~0.55 s apart)
           --maps           print the per-map table (default on; --no-maps to hide)
           --refresh        refetch the games list even if the cache already covers the window

Data:
  * submissions + per-map server ratings: GET /api/v1/submissions (byMap)
  * per-game history with both teams' Elo at game time: public /games/__data.json?teams=952&page=N
    (10 games/page, newest first; the v1 /battles list stops at 200 battles ~ 12 h). Cached in
    replays/ab_server/games.json, so later runs only fetch the new pages.
  * a game belongs to a submission if it was played in [uploadedAt + grace, next upload's uploadedAt)
    (every upload so far was activated on upload). --since/--until NAME=ISO narrow that window.
  * top-10 = current leaderboard top 10 (excluding us); "challenge" = launched via /battles (by us or them),
    "scrim" = server autoscrim.

Performance above expectation (PAE), per game g:
    s_g  = 1 win, 0.5 draw, 0 loss
    E_g  = 1 / (1 + 10 ** ((R_opp,g - R_us) / 400))
    PAE  = sum_g (s_g - E_g); reported as PAE/game (in win-probability units, x100 = percentage points)
  R_opp,g = opponent team Elo stored with that game. R_us: 'pooled' (default) = mean of our team Elo over
  all games of all compared submissions (a fixed reference, so a better bot is not penalised by the higher
  rating it earned); 'self' = our team Elo stored with each game; a number = that fixed value.
Paired comparison: on maps where both sides have >= --min-map games, d_m = PAE/game_B(m) - PAE/game_A(m),
  combined with weights w_m = nA*nB/(nA+nB). 95% CI from a 2000-rep stratified bootstrap (games resampled
  within each map x submission). Sign test over maps (two-sided binomial, p=0.5).
Verdict: CI entirely above 0 -> better, below -> worse, else inconclusive.
"""
import argparse
import collections
import datetime as dt
import json
import math
import pathlib
import random
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import api  # noqa: E402

US_ID = 952
CACHE = ROOT / "replays" / "ab_server"
GAMES_F = CACHE / "games.json"
ENDS_F = CACHE / "ends.json"


def parse_t(s):
    s = s.strip().replace("Z", "+00:00")
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")


# ---------------------------------------------------------------- public games list (devalue decode)
def devalue(data):
    cache = {}

    def h(i):
        if i == -1:
            return None
        if i in cache:
            return cache[i]
        v = data[i]
        if isinstance(v, dict):
            r = {k: h(x) for k, x in v.items()}
        elif isinstance(v, list):
            r = v[1] if (v and isinstance(v[0], str) and v[0] == "Date") else [h(x) for x in v]
        else:
            r = v
        cache[i] = r
        return r
    return h(0)


def fetch_page(p):
    u = f"https://game.battlecode.au/games/__data.json?teams={US_ID}&page={p}"
    for attempt in range(6):
        try:
            req = urllib.request.Request(u, headers=api.UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read())
            return devalue(d["nodes"][1]["data"])["matches"]
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except Exception:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"page {p} failed")


def _keep(games, ms):
    for m in ms:
        games[str(m["id"])] = {k: m.get(k) for k in ("id", "ranked", "status", "winner", "challenge",
                                                     "tournament", "at", "mapName", "a", "b")}
    return min(parse_t(m["at"]) for m in ms)


def _page_back(games, p, stop_at, tag):
    """Fetch pages p, p+1, ... until a page's oldest game is older than stop_at. Returns (oldest, pages)."""
    oldest, n = None, 0
    while True:
        ms = fetch_page(p)
        n += 1
        if not ms:
            break
        o = _keep(games, ms)
        oldest = o if oldest is None else min(oldest, o)
        if n % 25 == 0:
            print(f"  ..{tag} page {p}, back to {iso(oldest)}", file=sys.stderr, flush=True)
        p += 1
        time.sleep(1.2)
        if o < stop_at:
            break
    return oldest, n


def load_games(since, refresh):
    """Return {id: game} covering at least [since, now]. Cache keeps one coverage interval [from, to]."""
    CACHE.mkdir(parents=True, exist_ok=True)
    c = json.loads(GAMES_F.read_text()) if GAMES_F.exists() else {"from": None, "to": None, "games": {}}
    games = c["games"]
    cov_from = parse_t(c["from"]) if c["from"] and not refresh else None
    cov_to = parse_t(c["to"]) if c["to"] and not refresh else None
    start = dt.datetime.now(dt.timezone.utc)
    if not cov_from:
        oldest, n = _page_back(games, 1, since, "full")
        new_from, pages = oldest, n
    else:
        # front pass: new games since the cache (30 min margin for games that were live when cached)
        oldest, pages = _page_back(games, 1, cov_to - dt.timedelta(minutes=30), "new")
        new_from = cov_from
        if since < cov_from:
            # back pass: jump to the page just before the cached region and continue backwards
            newer = sum(1 for g in games.values() if parse_t(g["at"]) >= cov_from)
            p = max(1, newer // 10 - 3)
            while p > 1:
                ms = fetch_page(p)
                time.sleep(1.2)
                if ms and max(parse_t(m["at"]) for m in ms) >= cov_from:
                    break  # overlaps the cached region: safe to continue from here
                p = max(1, p - 10)
            o2, n2 = _page_back(games, p, since, "back")
            pages += n2 + 1
            new_from = min(cov_from, o2) if o2 else cov_from
    GAMES_F.write_text(json.dumps({"from": new_from.isoformat(), "to": start.isoformat(), "games": games}))
    print(f"  fetched {pages} pages; cache {len(games)} games back to {iso(new_from)}", file=sys.stderr)
    return games


def load_ends(ids):
    """Per-game final scores -> 'elim' (loser score 0) or 'r500' (both alive at the round limit)."""
    ends = json.loads(ENDS_F.read_text()) if ENDS_F.exists() else {}
    todo = [i for i in ids if str(i) not in ends]
    if todo:
        print(f"  fetching end type for {len(todo)} games (~{len(todo) * 0.55 / 60:.1f} min)", file=sys.stderr)
    for k, gid in enumerate(todo):
        for attempt in range(5):
            try:
                m = api.get(f"/api/v1/battles/{gid}")["match"]
                a, b = m.get("scoresA"), m.get("scoresB")
                ends[str(gid)] = None if a is None or b is None else ("elim" if min(a, b) == 0 else "r500")
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(15 * (attempt + 1))
                    continue
                ends[str(gid)] = None
                break
        time.sleep(0.55)
        if k % 100 == 99:
            ENDS_F.write_text(json.dumps(ends))
    ENDS_F.write_text(json.dumps(ends))
    return ends


# ---------------------------------------------------------------- stats
def expect(r_opp, r_us):
    return 1.0 / (1.0 + 10 ** ((r_opp - r_us) / 400.0))


def summ(rows):
    n = len(rows)
    if not n:
        return None
    w = sum(r["s"] == 1 for r in rows)
    l = sum(r["s"] == 0 for r in rows)
    pae = [r["pae"] for r in rows]
    mu = sum(pae) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in pae) / (n - 1)) if n > 1 else 0.0
    return {"n": n, "w": w, "l": l, "d": n - w - l, "pae": mu, "se": sd / math.sqrt(n),
            "opp": sum(r["ropp"] for r in rows) / n}


def fmt(s, pae=True):
    if not s:
        return "-"
    t = f"{s['w']}-{s['l']}" + (f"-{s['d']}" if s["d"] else "")
    if pae:
        t += f" {s['pae'] * 100:+5.1f}"
    return t


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def paired(A, B, min_map, reps=2000, seed=1):
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for r in A:
        ga[r["map"]].append(r["pae"])
    for r in B:
        gb[r["map"]].append(r["pae"])
    maps = sorted(m for m in ga if len(ga[m]) >= min_map and len(gb.get(m, [])) >= min_map)
    if not maps:
        return None

    def est(xa, xb):
        num = den = 0.0
        for m in maps:
            na, nb = len(xa[m]), len(xb[m])
            w = na * nb / (na + nb)
            num += w * (sum(xb[m]) / nb - sum(xa[m]) / na)
            den += w
        return num / den
    d0 = est(ga, gb)
    rng = random.Random(seed)
    bs = []
    for _ in range(reps):
        xa = {m: [rng.choice(ga[m]) for _ in ga[m]] for m in maps}
        xb = {m: [rng.choice(gb[m]) for _ in gb[m]] for m in maps}
        bs.append(est(xa, xb))
    bs.sort()
    lo, hi = bs[int(0.025 * reps)], bs[int(0.975 * reps) - 1]
    diffs = {m: sum(gb[m]) / len(gb[m]) - sum(ga[m]) / len(ga[m]) for m in maps}
    k = sum(d > 0 for d in diffs.values())
    return {"d": d0, "lo": lo, "hi": hi, "maps": maps, "k": k, "n": len(maps),
            "p_sign": binom_two_sided(k, len(maps)), "diffs": diffs}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subs", nargs="+", help="submission names (NAME or NAME@ID); first one is baseline A")
    ap.add_argument("--since", action="append", default=[], help="NAME=ISO_UTC (repeatable)")
    ap.add_argument("--until", action="append", default=[], help="NAME=ISO_UTC (repeatable)")
    ap.add_argument("--ref", default="pooled")
    ap.add_argument("--min-map", type=int, default=5)
    ap.add_argument("--grace", type=int, default=300)
    ap.add_argument("--ends", action="store_true")
    ap.add_argument("--no-maps", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--json", default="", help="also write per-game rows to this file")
    a = ap.parse_args()
    if len(a.subs) < 2:
        ap.error("need at least two submissions")

    subs = api.get("/api/v1/submissions")
    subs.sort(key=lambda s: s["uploadedAt"])
    for i, s in enumerate(subs):
        s["_from"] = parse_t(s["uploadedAt"]) + dt.timedelta(seconds=a.grace)
        s["_to"] = parse_t(subs[i + 1]["uploadedAt"]) if i + 1 < len(subs) else dt.datetime.now(dt.timezone.utc)
    since_o = dict(x.split("=", 1) for x in a.since)
    until_o = dict(x.split("=", 1) for x in a.until)

    labels, windows, byid = [], {}, {}
    for tok in a.subs:
        name, _, sid = tok.partition("@")
        ss = [s for s in subs if s["name"] == name and (not sid or str(s["id"]) == sid)]
        if not ss:
            sys.exit(f"no submission named {tok}")
        wins = []
        for s in ss:
            f, t = s["_from"], s["_to"]
            if tok in since_o or name in since_o:
                f = max(f, parse_t(since_o.get(tok, since_o.get(name))))
            if tok in until_o or name in until_o:
                t = min(t, parse_t(until_o.get(tok, until_o.get(name))))
            if t > f:
                wins.append((f, t, s))
        labels.append(tok)
        windows[tok] = wins
        byid[tok] = ss
    earliest = min(f for w in windows.values() for f, _, _ in w)
    games = load_games(earliest, a.refresh)

    top10 = set()
    try:
        L = api.get("/api/v1/leaderboard")
        top10 = {t["id"] for t in sorted((t for t in L if isinstance(t.get("rank"), int) and t["id"] != US_ID),
                                          key=lambda t: t["rank"])[:10]}
    except Exception as e:  # noqa: BLE001
        print("leaderboard failed:", e, file=sys.stderr)

    rows = {lab: [] for lab in labels}
    for g in games.values():
        if g["status"] != "completed":
            continue
        t = parse_t(g["at"])
        us, them = (g["a"], g["b"]) if g["a"]["id"] == US_ID else (g["b"], g["a"])
        if us["id"] != US_ID or them["id"] == US_ID:
            continue
        side = "a" if g["a"]["id"] == US_ID else "b"
        s = 0.5 if g["winner"] not in ("a", "b") else (1.0 if g["winner"] == side else 0.0)
        for lab in labels:
            if any(f <= t < u for f, u, _ in windows[lab]):
                rows[lab].append({"id": g["id"], "map": g["mapName"], "s": s, "rus": us["elo"], "ropp": them["elo"],
                                  "opp": them["name"], "oppId": them["id"], "ranked": g["ranked"],
                                  "challenge": g.get("challenge"), "top10": them["id"] in top10, "at": g["at"]})
    allr = [r for lab in labels for r in rows[lab]]
    if not allr:
        sys.exit("no games found in the windows")
    if a.ref == "pooled":
        ref = sum(r["rus"] for r in allr) / len(allr)
    elif a.ref == "self":
        ref = None
    else:
        ref = float(a.ref)
    for r in allr:
        r["pae"] = r["s"] - expect(r["ropp"], r["rus"] if ref is None else ref)

    ends = load_ends([r["id"] for r in allr]) if a.ends else {}
    for r in allr:
        r["end"] = ends.get(str(r["id"]))

    # ---- header
    print(f"R_us = {'own Elo per game' if ref is None else f'{ref:.0f} ({a.ref})'}; PAE shown as percentage points per game")
    for lab in labels:
        ws = "; ".join(f"#{s['id']} {iso(f)}..{iso(t)}" for f, t, s in windows[lab])
        print(f"  {lab:10s} {ws}")
    # ---- overview / splits
    W = 12
    print()
    print(f"{'split':22s}" + "".join(f"{lab:>{W + 10}s}" for lab in labels))
    print(f"{'':22s}" + "".join(f"{'W-L  PAE/g (se)':>{W + 10}s}" for _ in labels))
    splits = [("ALL", lambda r: True), ("ranked", lambda r: r["ranked"]), ("unranked", lambda r: not r["ranked"]),
              ("challenge", lambda r: r["challenge"]), ("autoscrim", lambda r: r["challenge"] is False),
              ("vs top-10", lambda r: r["top10"]), ("vs rest", lambda r: not r["top10"])]
    if a.ends:
        splits += [("ends: elimination", lambda r: r["end"] == "elim"), ("ends: r500 tiebreak", lambda r: r["end"] == "r500")]
    for nm, f in splits:
        cells = []
        for lab in labels:
            s = summ([r for r in rows[lab] if f(r)])
            cells.append(f"{fmt(s)} ({s['se'] * 100:4.1f})" if s else "-")
        print(f"{nm:22s}" + "".join(f"{c:>{W + 10}s}" for c in cells))
    print(f"{'mean opp Elo':22s}" + "".join(f"{summ(rows[lab])['opp'] if rows[lab] else 0:>{W + 10}.0f}" for lab in labels))
    print(f"{'server rating':22s}" + "".join(f"{'/'.join(str(s.get('rating')) for s in byid[lab]):>{W + 10}s}" for lab in labels))
    if a.ends:
        for lab in labels:
            c = collections.Counter((r["end"], r["s"]) for r in rows[lab])
            print(f"  {lab}: elim W/L {c[('elim', 1.0)]}/{c[('elim', 0.0)]}, r500 W/L {c[('r500', 1.0)]}/{c[('r500', 0.0)]}")

    # ---- per map
    pairs = [(labels[0], lab) for lab in labels[1:]]
    if not a.no_maps:
        maps = sorted({r["map"] for r in allr})
        print()
        hdr = f"{'map':18s}" + "".join(f"{lab + ' W-L PAE srv':>24s}" for lab in labels)
        hdr += "".join(f"{'d(' + b + ')':>10s}" for _, b in pairs)
        print(hdr)
        for m in maps:
            cells, sm = [], {}
            for lab in labels:
                s = summ([r for r in rows[lab] if r["map"] == m])
                sm[lab] = s
                srv = "/".join(str(((x.get("byMap") or {}).get(m) or {}).get("rating", "-")) for x in byid[lab])
                cells.append(f"{fmt(s)} {srv}" if s else "-")
            line = f"{m:18s}" + "".join(f"{c:>24s}" for c in cells)
            for A_, B_ in pairs:
                if sm[A_] and sm[B_]:
                    line += f"{(sm[B_]['pae'] - sm[A_]['pae']) * 100:>+10.1f}"
                else:
                    line += f"{'-':>10s}"
            print(line)

    # ---- paired + verdict
    print()
    for A_, B_ in pairs:
        P = paired(rows[A_], rows[B_], a.min_map)
        sa, sb = summ(rows[A_]), summ(rows[B_])
        raw = (sb["pae"] - sa["pae"]) * 100 if sa and sb else float("nan")
        if not P:
            print(f"{B_} vs {A_}: no map with >= {a.min_map} games each; unpaired PAE diff {raw:+.1f} pp/game -> inconclusive")
            continue
        verdict = "better than" if P["lo"] > 0 else "worse than" if P["hi"] < 0 else "inconclusive vs"
        print(f"paired over {P['n']} maps (>= {a.min_map} games each): B>A on {P['k']}/{P['n']} maps, sign-test p={P['p_sign']:.2f}; "
              f"unpaired PAE diff {raw:+.1f} pp")
        print(f"VERDICT: {B_} {verdict} {A_}: {P['d'] * 100:+.1f} pp/game (95% CI {P['lo'] * 100:+.1f}..{P['hi'] * 100:+.1f}), "
              f"n={sa['n']}/{sb['n']} games")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(rows, indent=0))


if __name__ == "__main__":
    main()
