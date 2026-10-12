#!/usr/bin/env python3
"""watch_mech.py MAP[,MAP...] [--since UTC]: loss mechanics of the live build's server games on the named maps.
Uses the series cached by build_watch.py (work/oct12/watch/), downloads the replays (paced 1.3 s) into
work/oct12/replays/ and runs work/gfloss/analyze.py's analyse() on them.

Run from /Users/devsingh/Developer/UNSW_Battlecode:
    python3 tools/analysis/oct12/watch_mech.py Atlantis --since 2026-10-12T19:20:06"""
import argparse
import collections
import json
import pathlib
import statistics as st
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "work" / "gfloss"))
sys.path.insert(0, str(ROOT / "notes" / "tools"))
import api  # noqa: E402
import analyze as AN  # noqa: E402

W = ROOT / "work" / "oct12"
US = 952


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("maps")
    ap.add_argument("--since", default="")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    want = set(a.maps.split(","))
    rows = []
    for f in sorted((W / "watch").glob("*.json")):
        d = json.loads(f.read_text())
        m = d["match"]
        if (m["startedAt"] or m["requestedAt"])[:19] < a.since:
            continue
        side = "A" if m["teamAId"] == US else "B"
        opp = d["teamBName"] if side == "A" else d["teamAName"]
        for g in d["games"]:
            if g["mapName"] in want and g["status"] == "completed" and g["winner"] in ("a", "b"):
                rows.append((g["id"], side, g["mapName"], opp, int(g["winner"] == side.lower())))
    (W / "replays").mkdir(exist_ok=True)
    cf = W / "watch_rows_cache.json"
    cache = json.loads(cf.read_text()) if cf.exists() else {}
    for gid, side, mp, opp, win in rows:
        p = W / "replays" / f"{gid}.replay"
        if not p.exists():
            api.download_replay(gid, p)
            time.sleep(1.3)
        if str(gid) not in cache:
            try:
                cache[str(gid)] = AN.analyse((gid, side, str(W / "replays")))
            except Exception as e:  # noqa: BLE001
                cache[str(gid)] = {"id": gid, "error": repr(e)}
    cf.write_text(json.dumps(cache))
    by = collections.defaultdict(list)
    for gid, side, mp, opp, win in rows:
        r = cache[str(gid)]
        if "error" not in r:
            by[mp].append({**r, "opp": opp})
    for mp, L in sorted(by.items()):
        Ls = [r for r in L if not r["win"]]
        med = lambda v: (f"{st.median(v):.2f}" if v else "-")
        rat = lambda r, k: (r[k]["us_tot"] / r[k]["th_tot"]) if r.get(k) and r[k]["th_tot"] else None
        print(f"== {mp}: {sum(r['win'] for r in L)}-{len(Ls)}; loss decisions {dict(collections.Counter(r['decision'] for r in Ls))}; "
              f"our queen alive at end {sum(r['q']['alive'] for r in L)}/{len(L)}, theirs {sum(r['tq']['alive'] for r in L)}/{len(L)}; "
              f"our queen death modes {dict(collections.Counter(r['q'].get('mode') for r in L if not r['q']['alive']))}; "
              f"median queen death round {med([r['q']['round'] for r in L if not r['q']['alive']])}; "
              f"r100 length ratio {med([x for x in (rat(r, 'r100') for r in L) if x is not None])}, r300 {med([x for x in (rat(r, 'r300') for r in L) if x is not None])}; "
              f"units r100 us/them {med([r['r100']['us_n'] for r in L if r.get('r100')])}/{med([r['r100']['th_n'] for r in L if r.get('r100')])}; "
              f"eats us/them {med([r['us_eats'] for r in L])}/{med([r['th_eats'] for r in L])}")
        if a.v:
            for r in L:
                q, tq = r["q"], r["tq"]
                print(f"   {r['id']} {'W' if r['win'] else 'L'} vs {r['opp'][:22]:22s} {r['decision']:22s} end {r['end']} last {r['last']} | "
                      f"queen us {'alive L%d' % r['fin']['us_q'] if q['alive'] else 'dead r%d %s' % (q['round'], q.get('mode'))} / "
                      f"them {'alive L%d' % r['fin']['th_q'] if tq['alive'] else 'dead r%d' % tq['round']} | "
                      f"r100 {r.get('r100', {}).get('us_tot')}/{r.get('r100', {}).get('th_tot')} r300 {r.get('r300', {}).get('us_tot')}/{r.get('r300', {}).get('th_tot')} "
                      f"longest {r['fin']['us_max']}/{r['fin']['th_max']} eats {r['us_eats']}/{r['th_eats']}")


if __name__ == "__main__":
    main()
