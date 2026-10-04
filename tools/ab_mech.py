#!/usr/bin/env python3
"""Mechanism stats from server replays, per submission name (stage 1 of the A/B protocol). Read-only on the
server: it only downloads replays of games already played.

usage (run from the project root):
  python3 tools/ab_mech.py v61 c1                    # compare table, baseline first
  python3 tools/ab_mech.py v61 --limit 60            # one name
  options: --limit 60        max games per name (0 = all); a fixed pseudo-random sample, stable between runs
           --since/--until NAME=ISO, --window NAME=ISO..ISO, --grace 300    same meaning as tools/ab_server.py
           --maps "Devil,Maze"   only these maps        --non-top10   only opponents outside the top 10
           --no-download     use cached replays only    --seed 1      sample seed
           --json FILE       dump the per-game rows

Games are attributed to a name exactly as in tools/ab_server.py (upload windows). Replays are cached in
replays/ab_mech/<name>/<gameId>.replay (a replay already present in another replays/*/ folder is copied, not
downloaded); per-game stats are cached in replays/ab_mech/<name>/rows.json. Downloads use the public replay
endpoint, >= 1.5 s apart, backing off on HTTP 429.

Per-game stats ("we" = team 952; queen = the starting dragon):
  q_alive_r100     our queen has not died by round 100 (all games)
  q_alive_r500     our queen alive at the end, among games that reached the round limit
  len_ratio_r100 / len_ratio_r300   our total length / theirs at that round (geometric mean over games that
                   reached the round with both sides alive)
  eliminated       game ended before the round limit and we lost
  stillborn_by_r100       our split children born by r100 that died within 1 round of birth (count per game)
  stillborn_len_by_r100   their total length (per game);  stillborn_share_r100 = stillborn / splits by r100
  r500_qdead_loss  lost at the round limit with our queen dead and theirs alive (share of all games)
  lone_queen       ... and the enemy had <= 3 units left at the end (share of all games)
  king_qkill       enemy queen killed head-to-head by our king (our longest non-queen unit, L >= 8)
  any_qkill        enemy queen killed head-to-head by any of our units
CIs: Wilson for shares, mean +- 1.96 se for means; difference = B - A with a normal-approximation CI.
"""
import argparse
import hashlib
import json
import math
import pathlib
import shutil
import sys
import time
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import ab_server  # noqa: E402
import api  # noqa: E402

OUT = ROOT / "replays" / "ab_mech"
VER = 1  # bump when game_row changes
KING_MIN_LEN = 8
PACE = 1.5

# name -> (kind, description). kind: share (0/1 per game), mean, geo (ratio, geometric mean)
STATS = {
    "win": ("share", "win rate"),
    "q_alive_r100": ("share", "our queen alive at r100"),
    "q_alive_r500": ("share", "our queen alive at r500 (r500 games)"),
    "len_ratio_r100": ("geo", "total length ratio at r100"),
    "len_ratio_r300": ("geo", "total length ratio at r300"),
    "eliminated": ("share", "we were eliminated"),
    "stillborn_by_r100": ("mean", "stillborn children by r100 /game"),
    "stillborn_len_by_r100": ("mean", "stillborn length by r100 /game"),
    "stillborn_share_r100": ("mean", "stillborn share of splits by r100"),
    "r500_qdead_loss": ("share", "r500 loss, our Q dead, theirs alive"),
    "lone_queen": ("share", "  of those: enemy had <= 3 units"),
    "king_qkill": ("share", "enemy queen killed by our king"),
    "any_qkill": ("share", "enemy queen killed by any unit"),
}


def game_row(path, side):
    """Mechanism stats of one replay; side = 'A' or 'B' (our team)."""
    import replay_sim as RS
    g = RS.simulate(str(path))
    us, th = side, ("B" if side == "A" else "A")
    uq = 0 if g["team"][0] == us else 1
    tq = 1 - uq
    d = {}
    for x in g["deaths"]:
        d.setdefault(x["id"], x)
    res = g["result"]
    r500 = res.get("endReason") == "roundLimit"
    win = res.get("winner") == us
    lost = res.get("winner") == th
    snaps = dict(g["rounds"])
    fin = g["rounds"][-1][1]
    row = {"v": VER, "last": g["last_round"], "r500": r500, "win": int(win),
           "q_alive_r100": int(uq not in d or d[uq]["round"] > 100),
           "q_alive_r500": int(uq not in d) if r500 else None,
           "eliminated": int(lost and not r500)}
    for r in (100, 300):
        s = snaps.get(r)
        ok = s and s[us]["total"] > 0 and s[th]["total"] > 0
        row[f"len_ratio_r{r}"] = s[us]["total"] / s[th]["total"] if ok else None
    sp = [s for s in g["splits"] if s["team"] == us and s["round"] <= 100]
    sb = [s for s in sp if s["child"] in d and d[s["child"]]["round"] - s["round"] <= 1]
    row["splits_by_r100"] = len(sp)
    row["stillborn_by_r100"] = len(sb)
    row["stillborn_len_by_r100"] = sum(s["k"] for s in sb)
    row["stillborn_share_r100"] = len(sb) / len(sp) if sp else None
    qdl = r500 and lost and uq in d and tq not in d
    row["r500_qdead_loss"] = int(qdl)
    row["lone_queen"] = int(qdl and fin[th]["n"] <= 3)
    row["enemy_units_end"] = fin[th]["n"]
    x = d.get(tq)
    anyk = bool(x and x["reason"] == "HitHeadToHead" and x.get("killer_team") == us)
    king = False
    if anyk and x["killer"] != uq and x["killer_len"] >= KING_MIN_LEN:
        prev = snaps.get(x["round"] - 1, {}).get(us, {}).get("ids", {})
        others = [L for i, L in prev.items() if i not in (uq, x["killer"])]
        king = x["killer_len"] >= max(others, default=0)
    row["any_qkill"] = int(anyk)
    row["king_qkill"] = int(king)
    row["tq_dead_round"] = x["round"] if x else None
    row["q_dead_round"] = d[uq]["round"] if uq in d else None
    return row


def fetch(gid, dest, download=True):
    """Make dest exist: copy from another replays/*/ folder, else download (paced). Returns True on success."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    for p in (ROOT / "replays").glob(f"*/{gid}.replay"):
        if p != dest and p.stat().st_size > 0:
            shutil.copyfile(p, dest)
            return True
    for p in (ROOT / "replays").glob(f"*/*/{gid}.replay"):
        if p != dest and p.stat().st_size > 0:
            shutil.copyfile(p, dest)
            return True
    if not download:
        return False
    for att in range(4):
        try:
            api.download_replay(gid, dest)
            time.sleep(PACE)
            return dest.exists() and dest.stat().st_size > 0
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(20 * (att + 1))
                continue
            time.sleep(PACE)
            return False
        except Exception:  # noqa: BLE001
            time.sleep(5 * (att + 1))
    return False


def mech_rows(label, rows, limit=60, seed=1, download=True, quiet=False):
    """rows: ab_server rows of this label (already filtered). Returns per-game dicts (ab_server row + stats)."""
    d = OUT / label.replace("@", "_").replace("/", "_")
    d.mkdir(parents=True, exist_ok=True)
    cf = d / "rows.json"
    cache = json.loads(cf.read_text()) if cf.exists() else {}
    order = sorted(rows, key=lambda r: hashlib.md5(f"{seed}:{r['id']}".encode()).hexdigest())
    if limit:
        order = order[:limit]
    out, ndl, nfail = [], 0, 0
    for r in order:
        k = str(r["id"])
        c = cache.get(k)
        if not c or c.get("v") != VER:
            p = d / f"{k}.replay"
            had = p.exists()
            if not fetch(r["id"], p, download):
                nfail += 1
                continue
            ndl += not had
            try:
                c = game_row(p, r["side"])
            except Exception as e:  # noqa: BLE001
                c = {"v": VER, "err": str(e)[:200]}
            cache[k] = c
            if ndl % 20 == 0:
                cf.write_text(json.dumps(cache))
        if "err" in c:
            nfail += 1
            continue
        out.append({**r, **c})
    tmp = cf.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache))
    tmp.replace(cf)
    if not quiet:
        print(f"  {label}: {len(out)} games analysed of {len(rows)} in window "
              f"({ndl} replays fetched, {nfail} unavailable)", file=sys.stderr)
    return out


def summarise(rows):
    """{stat: {v, lo, hi, n, se, kind}}; for geo stats v/lo/hi are ratios and se is on the log scale."""
    S = {}
    for k, (kind, _) in STATS.items():
        xs = [r[k] for r in rows if r.get(k) is not None]
        n = len(xs)
        if not n:
            S[k] = {"v": None, "n": 0, "kind": kind}
            continue
        if kind == "share":
            p = sum(xs) / n
            z = 1.96
            den = 1 + z * z / n
            c = (p + z * z / (2 * n)) / den
            h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
            S[k] = {"v": p, "lo": c - h, "hi": c + h, "n": n, "se": math.sqrt(p * (1 - p) / n), "kind": kind}
        else:
            ys = [math.log(x) for x in xs] if kind == "geo" else xs
            mu = sum(ys) / n
            se = math.sqrt(sum((y - mu) ** 2 for y in ys) / (n - 1) / n) if n > 1 else 0.0
            f = math.exp if kind == "geo" else (lambda t: t)
            S[k] = {"v": f(mu), "lo": f(mu - 1.96 * se), "hi": f(mu + 1.96 * se), "n": n, "se": se, "kind": kind,
                    "mu": mu}
    return S


def cell(s):
    if s["v"] is None:
        return "-"
    if s["kind"] == "share":
        return f"{100 * s['v']:5.1f}% [{100 * s['lo']:.0f}..{100 * s['hi']:.0f}] n={s['n']}"
    return f"{s['v']:6.2f} [{s['lo']:.2f}..{s['hi']:.2f}] n={s['n']}"


def diff(a, b):
    if a["v"] is None or b["v"] is None:
        return "-"
    if a["kind"] == "geo":
        dm, se = b["mu"] - a["mu"], math.hypot(a["se"], b["se"])
        return f"x{math.exp(dm):.2f} [{math.exp(dm - 1.96 * se):.2f}..{math.exp(dm + 1.96 * se):.2f}]"
    dm, se = b["v"] - a["v"], math.hypot(a["se"], b["se"])
    if a["kind"] == "share":
        return f"{100 * dm:+5.1f} pp [{100 * (dm - 1.96 * se):+.0f}..{100 * (dm + 1.96 * se):+.0f}]"
    return f"{dm:+6.2f} [{dm - 1.96 * se:+.2f}..{dm + 1.96 * se:+.2f}]"


def run(tokens, limit=60, seed=1, download=True, maps=None, non_top10=False, grace=300, since=(), until=(),
        window=(), quiet=False):
    """Returns {label: (rows, summary)} for each token."""
    C = ab_server.collect(tokens, grace, since, until, window)
    res = {}
    for lab in C["labels"]:
        rs = C["rows"][lab]
        if maps:
            rs = [r for r in rs if r["map"] in maps]
        if non_top10:
            rs = [r for r in rs if not r["top10"]]
        rows = mech_rows(lab, rs, limit, seed, download, quiet)
        res[lab] = (rows, summarise(rows))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subs", nargs="+", help="submission names (NAME or NAME@ID); the first is the baseline")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--since", action="append", default=[])
    ap.add_argument("--until", action="append", default=[])
    ap.add_argument("--window", action="append", default=[])
    ap.add_argument("--grace", type=int, default=300)
    ap.add_argument("--maps", default="")
    ap.add_argument("--non-top10", action="store_true")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    maps = [m.strip() for m in a.maps.split(",") if m.strip()] or None
    res = run(a.subs, a.limit, a.seed, not a.no_download, maps, a.non_top10, a.grace, a.since, a.until, a.window)
    labs = list(res)
    base = labs[0]
    hdr = f"{'stat':40s}" + "".join(f"{lab:>28s}" for lab in labs)
    hdr += "".join(f"{lab + ' - ' + base:>28s}" for lab in labs[1:])
    print(hdr)
    for k, (_, desc) in STATS.items():
        line = f"{desc:40s}" + "".join(f"{cell(res[lab][1][k]):>28s}" for lab in labs)
        line += "".join(f"{diff(res[base][1][k], res[lab][1][k]):>28s}" for lab in labs[1:])
        print(line)
    for lab in labs:
        rows = res[lab][0]
        q = sum(r["r500_qdead_loss"] for r in rows)
        print(f"  {lab}: {len(rows)} games, {sum(r['r500'] for r in rows)} reached r500; r500 queen-dead losses {q}, "
              f"lone queen {sum(r['lone_queen'] for r in rows)} of those; enemy queen kills by king "
              f"{sum(r['king_qkill'] for r in rows)}, by any unit {sum(r['any_qkill'] for r in rows)}")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps({lab: res[lab][0] for lab in labs}, indent=0))


if __name__ == "__main__":
    main()
