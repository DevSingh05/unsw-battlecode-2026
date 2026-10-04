#!/usr/bin/env python3
"""The anti-overfitting check for GENERAL (unseen-map) changes.

Runs a candidate against a baseline on:
  1. gen      - generated maps in maps/gen (tuning set)
  2. blind    - the 10 ranked maps with map knowledge switched off on BOTH sides
                (the devs' own designs, treated as unseen)
  3. lesson   - hand-designed lesson maps in maps/lesson (if present)
  4. holdout  - maps/genhold, ONLY when --holdout is given (final pass/fail; don't tune on it)
  5. ladder   - the 10 ranked maps WITH map knowledge (must not regress)

usage: unseen_eval.py "bot:-DFLAG=1" [--base variants/v61] [--seeds 1] [--jobs 6] [--holdout] [--sets gen,blind,lesson,ladder,gated,blindvk]\n  gated   - portal-gated lesson/gen maps\n  blindvk - candidate WITHOUT map knowledge vs the map-aware base (+ the base-blind reference line); not pooled\n  real/realhold/samesize - tools/realmapgen.py sets (maps/real_gen/tune, hold, samesize); blind17 - 17 official maps, both blind\n  sprint  - the 7 Sprint maps; KNOWN to v40+ bots, so not pooled any more
Prints one line per set plus a pooled unseen score. A change is worth keeping only if the pooled
unseen score is clearly above 0.50 and no set is clearly below it.
"""
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# portal-gated maps (notes/unseen/PLAN.md): most food sits behind portals
GATED = ["lesson/islands_a", "lesson/islands_b", "lesson/vault_a", "lesson/vault_b", "lesson/vault_c",
         "gen/g2026_23", "gen/g2026_28", "gen/g2026_32", "genhold/g2027_13", "genhold/g2027_16"]
# candidate WITHOUT map knowledge vs the map-aware base: the real-opponent view of an unseen map
BLINDVK = ["default", "queen_of_spades", "portals", "schooltime", "trauma"]
RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy",
          "autarky", "dilemma", "slithery_fight", "trauma"]


def maps_in(folder):
    return [f"{folder}/{p.stem}" for p in sorted((ROOT / "maps" / folder).glob("*.map"))]


def with_flag(spec, flag):
    return spec + (" " if ":" in spec else ":") + flag


def run(cand, base, maps, seeds, jobs, seed_base):
    cmd = [sys.executable, str(ROOT / "tools" / "pool.py"), cand, "--pool", base, "--maps", ",".join(maps),
           "--seeds", str(seeds), "--seed-base", str(seed_base), "--jobs", str(jobs)]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).stdout
    line = [l for l in out.splitlines() if l.startswith("OVERALL")]
    if not line:
        return None, None, out[-500:]
    frac = line[0].split(":")[-1].strip()  # "a/b = x  95% [lo, hi]"
    score, n = frac.split("=")[0].strip().split("/")
    return float(score), int(n), line[0].split(": ", 1)[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--base", default="variants/v61")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--seed-base", type=int, default=60000)
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--sets", default="gen,blind,lesson,ladder")
    a = ap.parse_args()
    sets = a.sets.split(",") + (["holdout"] if a.holdout else [])
    total_s = total_n = 0.0
    for s in sets:
        if s == "gen":
            res = run(a.cand, a.base, maps_in("gen"), a.seeds, a.jobs, a.seed_base)
        elif s == "blind":
            res = run(with_flag(a.cand, "-DNO_KNOWN_MAPS=1"), with_flag(a.base, "-DNO_KNOWN_MAPS=1"),
                      RANKED, max(2, a.seeds * 2), a.jobs, a.seed_base)
        elif s == "lesson":
            ms = maps_in("lesson")
            if not ms:
                print("lesson   (no maps yet)")
                continue
            res = run(a.cand, a.base, ms, a.seeds, a.jobs, a.seed_base)
        elif s == "holdout":
            res = run(a.cand, a.base, maps_in("genhold"), a.seeds, a.jobs, a.seed_base)
        elif s == "gated":
            res = run(a.cand, a.base, GATED, max(2, a.seeds * 2), a.jobs, a.seed_base)
        elif s == "blindvk":
            # compare against the same run with the base itself blind (printed as 'blindvk-base')
            res = run(with_flag(a.cand, "-DNO_KNOWN_MAPS=1"), a.base, BLINDVK, max(2, a.seeds * 2), a.jobs, a.seed_base)
            ref = run(with_flag(a.base, "-DNO_KNOWN_MAPS=1"), a.base, BLINDVK, max(2, a.seeds * 2), a.jobs, a.seed_base)
            print(f"blindvk-base {ref[2]}", flush=True)
        elif s == "sprint":
            # the 7 Sprint maps: KNOWN to v40+ bots (SPRINT_KNOWN), so printed but not pooled as unseen
            res = run(a.cand, a.base, maps_in("sprint"), max(2, a.seeds * 2), a.jobs, a.seed_base)
        elif s in ("real", "realhold", "samesize"):
            # tools/realmapgen.py maps shaped like the official ones (notes/newrules/UNSEEN_GENERALISATION.md 6.4)
            folder = {"real": "real_gen/tune", "realhold": "real_gen/hold", "samesize": "real_gen/samesize"}[s]
            res = run(a.cand, a.base, maps_in(folder), a.seeds, a.jobs, a.seed_base)
        elif s == "blind17":
            # the 17 official maps with map knowledge off on both sides
            res = run(with_flag(a.cand, "-DNO_KNOWN_MAPS=1"), with_flag(a.base, "-DNO_KNOWN_MAPS=1"),
                      RANKED + maps_in("sprint"), max(2, a.seeds * 2), a.jobs, a.seed_base)
        elif s == "ladder":
            res = run(a.cand, a.base, RANKED, max(2, a.seeds * 2), a.jobs, a.seed_base)
        else:
            continue
        score, n, text = res
        print(f"{s:8s} {text}", flush=True)
        if score is not None and s not in ("ladder", "blindvk", "sprint"):
            total_s += score
            total_n += n
    if total_n:
        p = total_s / total_n
        print(f"POOLED UNSEEN {total_s:.1f}/{int(total_n)} = {p:.3f}")


if __name__ == "__main__":
    main()
