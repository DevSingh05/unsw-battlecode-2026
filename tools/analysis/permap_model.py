"""Per-map, per-equivalence-class opponent-adjusted analysis of our server builds (label: measure).
Read-only: uses replays/ab_server/games.json, scratch subs.json, replays/ab_mech/*/rows.json."""
import json, math, collections, datetime as dt, sys, pathlib
import numpy as np

ROOT = pathlib.Path("/Users/devsingh/Developer/UNSW_Battlecode")
HERE = pathlib.Path(__file__).parent
US = 952
GRACE = 300
START = "2026-10-03T07:13"   # v44@15640 upload (context block before v55)
LAM_C = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25   # ridge on per-map class effects (logit)
import os
PLACEBO = os.environ.get("PLACEBO")
DAYH = int(sys.argv[2]) if len(sys.argv) > 2 else 24        # opponent x time-block length (hours)

MAPS17 = ["Around UNSW", "Australia", "Autarky", "Default", "Devil", "Islands", "Maze", "Portals",
          "Prisoners Dilemma", "Queen Of Spades", "Schooltime", "Slithery Fight", "Stripes", "Tower Defense",
          "Trauma", "Trophy", "weakhold"]
ALL = set(MAPS17)
# token -> maps where it changes play
TOK = {
    "QS": ALL, "QSR": ALL, "QEXIT": ALL, "L34": ALL, "QKBIG": ALL, "QEP": ALL, "C1": ALL, "FUEL": ALL,
    "H1": ALL, "SDEF": ALL, "MID": ALL, "PB": ALL, "KF": ALL,
    "PARK_P": {"Portals"}, "PARK_M": {"Maze"}, "QKEG": {"Portals", "Maze"}, "QGR": {"Portals", "Maze"},
    "STR": {"Stripes"}, "TRQ": {"Trophy"}, "SCHB": {"Schooltime"}, "TRG": {"Trophy"},
    "Q1PARK": {"Australia", "Around UNSW", "Slithery Fight", "Tower Defense", "weakhold"},
    "CRAUS": {"Australia"}, "CRAUN": {"Around UNSW"},
    "LANE": {"Tower Defense", "Devil", "Autarky", "Queen Of Spades"},
    "TDP": {"Tower Defense"}, "QVA": {"Australia"}, "QVS": {"Slithery Fight"},
    "SCHD": {"Schooltime"}, "SCHC": {"Schooltime"},
}
V61 = {"QS", "QSR"}
B1 = V61 | {"PARK_P", "PARK_M"}
B2 = B1 | {"FUEL"}
B3 = B2 | {"CRAUS"}
B4 = B3 | {"TDP", "QVA"}
BUILD = {
    "v44": set(), "v55": {"QS"}, "v60": {"QS", "QEXIT"}, "v61": V61, "v64": V61 | {"L34"},
    "v65": V61 | {"QKBIG"}, "v69": V61 | {"QEP"}, "c1": V61 | {"C1"},
    "m1": B1 | {"STR", "TRQ", "SCHB"}, "m2": B1 | {"STR", "TRQ"}, "b1": B1,
    "q1": B1 | {"Q1PARK"}, "f1": B2, "h1": B2 | {"H1"}, "k2": B2 | {"QKEG"}, "cm1": B2 | {"CRAUS", "CRAUN"},
    "b3": B3, "s1": B3 | {"SDEF"}, "l1": B3 | {"LANE"}, "ms1": B3 | {"MID"},
    "u1": B3 | {"TDP", "QVA", "QVS", "SCHD", "SCHC", "TRG", "QGR"}, "v1": B3 | {"TDP", "QVA", "QVS", "SCHD"},
    "b4": B4, "pb2": B4 | {"PB"}, "kf1": B4 | {"KF"},
}


def pt(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def key(build, m):
    return frozenset(t for t in BUILD[build] if m in TOK[t])


subs = json.load(open(HERE / "subs.json"))
subs.sort(key=lambda s: s["uploadedAt"])
now = dt.datetime.now(dt.timezone.utc)
wins = []
for i, s in enumerate(subs):
    f = pt(s["uploadedAt"]) + dt.timedelta(seconds=GRACE)
    t = pt(subs[i + 1]["uploadedAt"]) if i + 1 < len(subs) else now
    if t > f and s["uploadedAt"] >= START:
        wins.append((f, t, s["name"], s["id"]))
games = json.load(open(ROOT / "replays/ab_server/games.json"))["games"]
t0 = pt(START + ":00Z")
rows = []
for g in games.values():
    if g["status"] != "completed" or g.get("tournament"):
        continue
    t = pt(g["at"])
    if t < t0:
        continue
    us, them = (g["a"], g["b"]) if g["a"]["id"] == US else (g["b"], g["a"])
    if us["id"] != US or them["id"] == US or g["mapName"] not in ALL:
        continue
    b = next(((n, sid) for f, u, n, sid in wins if f <= t < u), None)
    # server per-map counts show v61#16388 (not kf1) was the active submission from ~03:20 UTC 7 Oct until the
    # b4 upload at 19:26 (suffix of the kf1 window matches v61's extra W-L on all 17 maps within 30 games;
    # team rating history drops 2210 -> 2174 between 03:13 and 03:23). Ambiguous 03:13-03:25 dropped.
    if pt("2026-10-07T03:13:00Z") <= t < pt("2026-10-07T03:25:00Z"):
        continue
    if pt("2026-10-07T03:25:00Z") <= t < pt("2026-10-07T19:26:05Z"):
        b = ("v61", 16388)
    if not b or b[0] not in BUILD:
        continue
    side = "a" if g["a"]["id"] == US else "b"
    s = 0.5 if g["winner"] not in ("a", "b") else (1.0 if g["winner"] == side else 0.0)
    rows.append(dict(id=g["id"], t=t, map=g["mapName"], s=s, b=b[0], sid=b[1], opp=them["id"], oname=them["name"],
                     ropp=them["elo"], ranked=bool(g["ranked"]), scrim=not g.get("challenge"),
                     blk=int((t - t0).total_seconds() // (DAYH * 3600))))
print(f"{len(rows)} games {min(r['t'] for r in rows)} .. {max(r['t'] for r in rows)}", file=sys.stderr)

# classes per map
cls_members = {}  # (map, key) -> set of builds
for r in rows:
    k = key(r["b"], r["map"])
    r["k"] = k
    if os.environ.get("SPLIT61") and r["b"] == "v61" and r["t"] >= pt("2026-10-07T03:25:00Z"):
        r["k"] = k | {"OCT7"}
    if PLACEBO and k == key("b4", r["map"]) and r["t"] < pt(PLACEBO):
        r["k"] = k | {"EARLY"}
    cls_members.setdefault((r["map"], k), set()).add(r["b"])

def fit(rs, use_od=True, min_opp=12):
    oc = collections.Counter(r["opp"] for r in rs)
    ocb = collections.Counter((r["opp"], r["blk"]) for r in rs)
    names, lam = {}, []

    def col(n, l):
        if n not in names:
            names[n] = len(names)
            lam.append(l)
        return names[n]
    for n in ("c", "rk", "scrim", "elo"):
        col(n, 1e-6)
    feats = []
    for r in rs:
        f = [(names["c"], 1.0), (col("M:" + r["map"], 1.0), 1.0)]
        if r["k"] != key("b4", r["map"]):
            f.append((col(("C", r["map"], r["k"]), LAM_C), 1.0))
        if oc[r["opp"]] >= min_opp:
            f.append((col(("O", r["opp"]), 0.3), 1.0))
            if use_od and ocb[(r["opp"], r["blk"])] >= 6:
                f.append((col(("OD", r["opp"], r["blk"]), 1.0), 1.0))
        else:
            f.append((names["elo"], (r["ropp"] - 2000) / 400.0))
        if r["ranked"]:
            f.append((names["rk"], 1.0))
        if r["scrim"]:
            f.append((names["scrim"], 1.0))
        feats.append(f)
    k = len(names)
    X = np.zeros((len(rs), k))
    for i, f in enumerate(feats):
        for j, v in f:
            X[i, j] += v
    y = np.array([r["s"] for r in rs])
    L = np.diag(lam)
    b = np.zeros(k)
    for it in range(60):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
        g = X.T @ (y - p) - L @ b
        H = (X * (p * (1 - p))[:, None]).T @ X + L
        step = np.linalg.solve(H, g)
        b += step
        if np.max(np.abs(step)) < 1e-8:
            break
    return names, b, np.linalg.inv(H), X @ b


names, b, cov, z = fit(rows)
print(f"fit: k={len(names)} rk={b[names['rk']]:+.2f} scrim={b[names['scrim']]:+.2f}", file=sys.stderr)


def sig(x):
    return 1 / (1 + np.exp(-x))


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


LOCH = 36


def local(m, kk, ii):
    """time-local: refit on all games within [first-36h, last+36h] of this class's games on this map, opponent
    terms from that window only (no opponent x block terms); contrast vs b4-class games on this map in the window."""
    f = min(rows[i]["t"] for i in ii) - dt.timedelta(hours=LOCH)
    t = max(rows[i]["t"] for i in ii) + dt.timedelta(hours=LOCH)
    rs = [r for r in rows if f <= r["t"] <= t]
    b4k = key("b4", m)
    nb = sum(1 for r in rs if r["map"] == m and r["k"] == b4k)
    if nb < 8:
        return dict(loc_nb4=nb)
    nm, bb, cv, zz = fit(rs, use_od=False)
    ci = nm[("C", m, kk)]
    est, se = bb[ci], math.sqrt(cv[ci, ci])
    a = [j for j, r in enumerate(rs) if r["map"] == m and r["k"] == kk]
    c = [j for j, r in enumerate(rs) if r["map"] == m and r["k"] == b4k]
    z0 = np.concatenate([zz[a] - est, zz[c]])
    ame = lambda e: 100 * float(np.mean(sig(z0 + e) - sig(z0)))
    return dict(loc_nb4=nb, loc_pp=ame(est), loc_lo=ame(est - 1.96 * se), loc_hi=ame(est + 1.96 * se),
                loc_p=norm_cdf(est / se))


# mechanism rows
mech = {}
for d in (ROOT / "replays/ab_mech").iterdir():
    f = d / "rows.json"
    if f.exists():
        for gid, x in json.load(open(f)).items():
            mech[int(gid)] = x

out = {"lam_c": LAM_C, "dayh": DAYH, "n": len(rows), "maps": {}}
idx = collections.defaultdict(list)
for i, r in enumerate(rows):
    idx[(r["map"], r["k"])].append(i)
for m in MAPS17:
    b4k = key("b4", m)
    base_i = idx.get((m, b4k), [])
    # baseline expected win of b4-class games as b4 (z includes no class term for them)
    e_base = float(np.mean(sig(z[base_i]))) if base_i else float("nan")
    classes = []
    for (mm, kk), ii in idx.items():
        if mm != m:
            continue
        mem = sorted(set(rows[i]["b"] for i in ii), key=lambda n: list(BUILD).index(n))
        allmem = sorted([bb for bb in BUILD if key(bb, m) == kk], key=lambda n: list(BUILD).index(n))
        W = sum(1 for i in ii if rows[i]["s"] == 1); Lo = sum(1 for i in ii if rows[i]["s"] == 0)
        D = len(ii) - W - Lo
        ent = dict(key=sorted(kk), members=mem, all_members=allmem, n=len(ii), W=W, L=Lo, D=D,
                   ranked=sum(rows[i]["ranked"] for i in ii), scrim=sum(rows[i]["scrim"] for i in ii),
                   first=min(rows[i]["t"] for i in ii).isoformat()[:16], last=max(rows[i]["t"] for i in ii).isoformat()[:16],
                   per_build={bb: sum(1 for i in ii if rows[i]["b"] == bb) for bb in mem})
        ci = names.get(("C", m, kk))
        if kk == b4k:
            ent["b4class"] = True
            ent["e_as_b4"] = e_base
        else:
            est, se = b[ci], math.sqrt(cov[ci, ci])
            # z0: linear predictor without the class term, over both arms
            z0 = np.concatenate([z[ii] - est, z[base_i]])
            ame = lambda e: 100 * float(np.mean(sig(z0 + e) - sig(z0)))
            ent.update(logit=float(est), se=float(se), pp=ame(est), lo=ame(est - 1.96 * se), hi=ame(est + 1.96 * se),
                       p_better=norm_cdf(est / se), e_as_b4=float(np.mean(sig(z[ii] - est))))
            ent.update(local(m, kk, ii))
        # opponent mix: share of games vs most common opponents
        om = collections.Counter(rows[i]["oname"] for i in ii).most_common(3)
        ent["top_opps"] = [(o, c) for o, c in om]
        # mechanism
        mr = [mech[rows[i]["id"]] for i in ii if rows[i]["id"] in mech]
        r5 = [x for x in mr if x.get("r500")]
        qa = [x["q_alive_r500"] for x in r5 if x.get("q_alive_r500") is not None]
        lr = [x["len_ratio_r300"] for x in mr if x.get("len_ratio_r300")]
        ent["mech"] = dict(n=len(mr), elim=sum(x.get("eliminated", 0) for x in mr), n_r500=len(qa), q500=sum(qa),
                           lr300=(math.exp(sum(math.log(v) for v in lr) / len(lr)) if lr else None), n_lr=len(lr),
                           q100=sum(x.get("q_alive_r100", 0) for x in mr))
        classes.append(ent)
    classes.sort(key=lambda e: (not e.get("b4class"), -e["n"]))
    out["maps"][m] = classes
json.dump(out, open(HERE / f"permap_l{LAM_C}_d{DAYH}{'_placebo' if PLACEBO else ''}{'_split61' if os.environ.get('SPLIT61') else ''}.json", "w"), indent=1, default=str)
# console summary
for m in MAPS17:
    print(f"\n== {m}")
    for e in out["maps"][m]:
        mem = "+".join(e["members"])
        mc = e["mech"]
        mtxt = f"mech n{mc['n']} el{mc['elim']} q500 {mc['q500']}/{mc['n_r500']} lr300 {mc['lr300'] and round(mc['lr300'],2)}"
        if e.get("b4class"):
            print(f"  B4CLASS {mem:40s} n{e['n']:4d} {e['W']}-{e['L']}-{e['D']} rk{e['ranked']} Eb4 {e['e_as_b4']:.2f} | {mtxt}")
        else:
            print(f"  {mem:48s} n{e['n']:4d} {e['W']}-{e['L']}-{e['D']} rk{e['ranked']} {e['pp']:+5.1f}pp ({e['lo']:+.1f}..{e['hi']:+.1f}) P{e['p_better']:.2f} loc {e.get('loc_pp',float('nan')):+5.1f} P{e.get('loc_p',float('nan')):.2f} nb{e['loc_nb4']} Eb4 {e['e_as_b4']:.2f} | {mtxt}")
