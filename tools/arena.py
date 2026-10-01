#!/usr/bin/env python3
"""Run many local games in parallel and summarise.

usage: arena.py BOT_A BOT_B [--maps m1,m2] [--seeds N] [--jobs J] [--replays DIR]
Each (map, seed) is played twice with sides swapped. Scores are from BOT_A's view.
"""
import argparse
import concurrent.futures as cf
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy",
          "autarky", "dilemma", "slithery_fight", "trauma"]
WIN = re.compile(r"team ([AB]) wins after (\d+) rounds \((?:by |on )?([a-z ]+)[,)]")  # 1.2.3: "(longer queen, 2 to 0)", "(longest dragon, ...)"
DRAW = re.compile(r"(draw|tie)", re.I)


BIN = pathlib.Path("/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/bins")


def build(spec):
    """'dir' or 'dir:-DFOO=1 -DBAR=2'. C++ dirs are compiled natively once; others pass through."""
    path, _, flags = spec.partition(":")
    d = ROOT / path
    srcs = sorted(d.glob("*.cpp"))
    if not srcs:
        return str(d)
    BIN.mkdir(parents=True, exist_ok=True)
    tag = (path + flags).replace("/", "_").replace(" ", "").replace("-D", "_").replace("=", "")
    out = BIN / tag
    newest = max(f.stat().st_mtime for f in list(d.rglob("*.cpp")) + list(d.rglob("*.hpp")))
    if out.exists() and out.stat().st_mtime > newest:
        return str(out)
    tmp = out.with_name(out.name + f".tmp{__import__('os').getpid()}")
    cmd = ["c++", "-std=c++20", "-O2", *flags.split(), "-o", str(tmp), *map(str, srcs)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    tmp.replace(out)
    return str(out)


def play(a, b, mp, seed, replays):
    cmd = ["unswbc", "run", str(ROOT / "maps" / f"{mp}.map"), a, b, "--seed", str(seed), "--no-debug"]
    if replays:
        cmd += ["-o", str(pathlib.Path(replays) / f"{mp}_{seed}_{pathlib.Path(a).name}_vs_{pathlib.Path(b).name}.replay")]
    else:
        cmd.append("--no-replay")
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    text = p.stdout + p.stderr
    m = WIN.search(text)
    if m:
        return m.group(1), int(m.group(2)), m.group(3), text
    if DRAW.search(text):
        return "D", 500, "draw", text
    return "?", 0, "error", text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--maps", default=",".join(RANKED))
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--replays", default=None)
    ap.add_argument("--show-errors", action="store_true")
    args = ap.parse_args()
    maps = args.maps.split(",")
    args.a = build(args.a)
    args.b = build(args.b)
    jobs = []
    with cf.ThreadPoolExecutor(args.jobs) as ex:
        for mp in maps:
            for s in range(args.seeds):
                seed = 1000 + s
                jobs.append((mp, seed, False, ex.submit(play, args.a, args.b, mp, seed, args.replays)))
                jobs.append((mp, seed, True, ex.submit(play, args.b, args.a, mp, seed, args.replays)))
        per_map = {}
        total = [0, 0, 0]
        for mp, seed, swapped, fut in jobs:
            winner, rounds, how, text = fut.result()
            if winner == "?":
                res = "?"
                if args.show_errors:
                    print(text[-800:], file=sys.stderr)
            elif winner == "D":
                res = "D"
            else:
                a_team = "B" if swapped else "A"
                res = "W" if winner == a_team else "L"
            per_map.setdefault(mp, []).append(f"{res}{rounds}{'e' if how.startswith('elim') else 'r'}")
            if res == "W":
                total[0] += 1
            elif res == "L":
                total[1] += 1
            else:
                total[2] += 1
    for mp in maps:
        rs = per_map[mp]
        w = sum(r.startswith("W") for r in rs)
        print(f"{mp:16s} {w}/{len(rs)}  " + " ".join(rs))
    n = sum(total)
    print(f"TOTAL {args.a} vs {args.b}: W{total[0]} L{total[1]} D/err{total[2]}  winrate {total[0] / max(1, n):.2f}")


if __name__ == "__main__":
    main()
