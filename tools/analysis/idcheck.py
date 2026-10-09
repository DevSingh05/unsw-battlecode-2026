#!/usr/bin/env python3
"""Action-identity check: CAND vs BASE against BASE vs BASE, both sides, --sandbox -v --seed S.
usage: idcheck.py CAND BASE --maps m1.map,m2.map [--seed 1000] [--jobs 6] [--out DIR]
Signature = the full -v transcript (every dragon's stdout + deaths + result) minus CPU points / timing lines.
Prints per map: ref result, and MATCH/DIFF for cand-as-A and cand-as-B, plus the first differing line."""
import argparse, concurrent.futures as cf, hashlib, pathlib, re, subprocess

ROOT = pathlib.Path("/Users/devsingh/Developer/UNSW_Battlecode")
DROP = re.compile(r"^(round \d+: bot \d+ \(team [AB]\) points \d+ memory \d+|running round|team [AB] points per turn|skipped writing replay|loaded |wrote replay|unswbc [\d.]+ is out|  uv tool install)")
RES = re.compile(r"^(team [AB] wins after .*|.*draw.*)$")
PTS = re.compile(r"team ([AB]) points per turn: .*max ([\d.]+)M")


def play(a, b, mp, seed, out):
    cmd = ["unswbc", "run", str(ROOT / mp), a, b, "--seed", str(seed), "--sandbox", "-v", "--no-replay"]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    text = p.stdout + p.stderr
    keep, res, pts = [], "?", {}
    lines = text.splitlines()
    i0 = next((i for i, l in enumerate(lines) if l.startswith("seed 0x")), 0)  # skip build chatter
    for l in lines[i0:]:
        m = PTS.match(l)
        if m:
            pts[m.group(1)] = float(m.group(2))
        if DROP.match(l):
            continue
        l = re.sub(r" \(\d+(\.\d+)?m?s\)$", "", l)
        keep.append(l)
    res = keep[-1] if keep else "?"
    if out:
        pathlib.Path(out).write_text("\n".join(keep))
    return hashlib.md5("\n".join(keep).encode()).hexdigest(), res, pts, keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("base")
    ap.add_argument("--maps", required=True)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=None)
    ap.add_argument("--noref", action="store_true", help="compare cand-as-A vs cand-as-B? no: skip ref (needs --refdir)")
    a = ap.parse_args()
    maps = a.maps.split(",")
    od = pathlib.Path(a.out) if a.out else None
    if od:
        od.mkdir(parents=True, exist_ok=True)
    # warm builds sequentially (avoid concurrent wasm builds in one dir)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        fut = {}
        for mp in maps:
            st = pathlib.Path(mp).stem
            fut[(mp, "ref")] = ex.submit(play, a.base, a.base, mp, a.seed, od / f"{st}_ref.txt" if od else None)
            fut[(mp, "cA")] = ex.submit(play, a.cand, a.base, mp, a.seed, od / f"{st}_cA.txt" if od else None)
            fut[(mp, "cB")] = ex.submit(play, a.base, a.cand, mp, a.seed, od / f"{st}_cB.txt" if od else None)
        nm = nd = 0
        cmax = 0.0
        for mp in maps:
            h0, r0, p0, k0 = fut[(mp, "ref")].result()
            line = f"{pathlib.Path(mp).stem:22s} ref: {r0[:60]:60s}"
            for side in ("cA", "cB"):
                h, r, p, k = fut[(mp, side)].result()
                cmax = max(cmax, p.get("A" if side == "cA" else "B", 0))
                if h == h0:
                    nm += 1
                    line += f" {side}=MATCH"
                else:
                    nd += 1
                    i = next((i for i, (x, y) in enumerate(zip(k0, k)) if x != y), min(len(k0), len(k)))
                    ctx = k[i - 3:i + 1] if i < len(k) else ["<eof>"]
                    line += f" {side}=DIFF(line {i}: {' | '.join(ctx)[:160]}; res {r[:50]})"
            print(line, flush=True)
        print(f"TOTAL match {nm} diff {nd}  (cand max CPU {cmax:.1f}M)")


if __name__ == "__main__":
    main()
