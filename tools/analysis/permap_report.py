"""Markdown tables from permap_*.json + subs.json (server per-map ratings)."""
import json, sys, pathlib, collections
HERE = pathlib.Path(__file__).parent
D = json.load(open(HERE / sys.argv[1]))
S = json.load(open(HERE / "subs.json"))
ALT = json.load(open(HERE / sys.argv[2])) if len(sys.argv) > 2 else None
B4K = None


def srv(name, m):
    best = None
    for s in S:
        if s["name"] != name:
            continue
        v = (s.get("byMap") or {}).get(m)
        if v:
            n = v["wins"] + v["losses"] + v["draws"]
            if not best or n > best[0]:
                best = (n, v["rating"], v["wins"], v["losses"])
    return best


def fmt_pp(e, pre=""):
    if e.get(pre + "pp") is None:
        return "-"
    return f"{e[pre+'pp']:+.1f} ({e[pre+'lo']:+.0f}..{e[pre+'hi']:+.0f})"


out = []
for m, cls in D["maps"].items():
    b4 = next(e for e in cls if e.get("b4class"))
    b4k = set(b4["key"])
    alt = {tuple(e["key"]): e for e in ALT["maps"][m]} if ALT else {}
    out.append(f"\n### {m}\n")
    out.append("| class (games per build) | code vs b4 on this map | n | W-L | win% | adj. vs b4 pp (95% CI) | P(better) | "
               "time-local pp (P) | E[win] as b4 | server map rating (W-L) | mech n: q500 / elim / lr300 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for e in cls:
        k = set(e["key"])
        dif = " ".join(["+" + t for t in sorted(k - b4k)] + ["-" + t for t in sorted(b4k - k)]) or "= b4"
        mem = ", ".join(f"{b} {n}" for b, n in e["per_build"].items())
        sr = []
        for b in e["members"]:
            x = srv(b, m)
            if x and x[0] >= 5:
                sr.append(f"{b} {x[1]} ({x[2]}-{x[3]})")
        mc = e["mech"]
        mtxt = (f"{mc['n']}: {mc['q500']}/{mc['n_r500']} / {mc['elim']} / "
                f"{(round(mc['lr300'], 2) if mc['lr300'] else '-')}") if mc["n"] else "-"
        wr = 100 * (e["W"] + 0.5 * e["D"]) / e["n"]
        if e.get("b4class"):
            adj, pb, loc = "**baseline**", "", ""
        else:
            adj = fmt_pp(e)
            if ALT and tuple(e["key"]) in alt and alt[tuple(e["key"])].get("pp") is not None:
                adj += f" [λ.05: {alt[tuple(e['key'])]['pp']:+.1f}]"
            pb = f"{e['p_better']:.2f}"
            loc = (f"{e['loc_pp']:+.1f} ({e['loc_p']:.2f})" if e.get("loc_pp") is not None
                   else f"n/a (b4-class n={e['loc_nb4']})")
        out.append(f"| {mem} | {dif} | {e['n']} | {e['W']}-{e['L']}{'-'+str(e['D']) if e['D'] else ''} | {wr:.0f} | "
                   f"{adj} | {pb} | {loc} | {e['e_as_b4']:.2f} | {'; '.join(sr) or '-'} | {mtxt} |")
print("\n".join(out))
