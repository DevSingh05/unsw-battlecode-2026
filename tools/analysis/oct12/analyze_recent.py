#!/usr/bin/env python3
"""analyze_recent.py: loss mechanics for the replays in work/oct12/replays (uses work/gfloss/analyze.py's analyse()).

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/analyze_recent.py            # writes work/oct12/rows.json, prints per-map tables"""
import collections
import json
import pathlib
import statistics as st
import sys
from multiprocessing import Pool

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "work" / "gfloss"))
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import analyze as AN  # noqa: E402

W = ROOT / "work" / "oct12"


def safe(a):
    try:
        return AN.analyse(a)
    except Exception as e:  # noqa: BLE001
        return {"id": a[0], "error": repr(e)}


def main():
    G = {r["gid"]: r for r in json.loads((W / "games_recent.json").read_text())}
    cf = W / "rows_cache.json"
    cache = json.loads(cf.read_text()) if cf.exists() else {}
    todo = [(g, G[g]["side"].upper(), str(W / "replays")) for g in G
            if str(g) not in cache and (W / "replays" / f"{g}.replay").exists()]
    if todo:
        with Pool(3) as P:
            for row in P.imap_unordered(safe, todo, chunksize=2):
                cache[str(row["id"])] = row
        cf.write_text(json.dumps(cache))
    rows = []
    for k, row in cache.items():
        if "error" in row:
            continue
        rows.append({**G[int(k)], **row})
    (W / "rows.json").write_text(json.dumps(rows))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["map"]].append(r)

    def med(L, f):
        v = [f(r) for r in L]
        v = [x for x in v if x is not None]
        return f"{st.median(v):.2f}" if v else "-"

    def ratio(k):
        return lambda r: (r[k]["us_tot"] / r[k]["th_tot"]) if r.get(k) and r[k]["th_tot"] else None

    print("| map | n | W-L | decisions in losses | our queen death in losses (mode x n) | median queen death round (L) | "
          "our queen alive at end W/L | r100 len ratio L/W | r300 len ratio L/W | units r100 us/them (L) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for mp, L in sorted(by.items()):
        Ls = [r for r in L if not r["win"]]
        Ws = [r for r in L if r["win"]]
        dec = collections.Counter(r["decision"] for r in Ls)
        qm = collections.Counter(r["q"].get("mode", "alive") for r in Ls)
        qr = [r["q"]["round"] for r in Ls if not r["q"]["alive"]]
        print(f"| {mp} | {len(L)} | {len(Ws)}-{len(Ls)} | {dict(dec)} | {dict(qm)} | {st.median(qr) if qr else '-'} | "
              f"{sum(r['q']['alive'] for r in Ws)}/{len(Ws)} / {sum(r['q']['alive'] for r in Ls)}/{len(Ls)} | "
              f"{med(Ls, ratio('r100'))} / {med(Ws, ratio('r100'))} | {med(Ls, ratio('r300'))} / {med(Ws, ratio('r300'))} | "
              f"{med(Ls, lambda r: r['r100']['us_n'] if r.get('r100') else None)} / {med(Ls, lambda r: r['r100']['th_n'] if r.get('r100') else None)} |")


if __name__ == "__main__":
    main()
