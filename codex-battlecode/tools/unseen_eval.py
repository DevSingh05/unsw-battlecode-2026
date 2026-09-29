#!/usr/bin/env python3
"""Run the team's read-only unseen_eval protocol with isolated builds/results."""
import argparse
import json
import pathlib
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
ROOT = HERE.parent
ap = argparse.ArgumentParser(add_help=False)
ap.add_argument("--label", required=True)
opts, rest = ap.parse_known_args()
sys.argv = [sys.argv[0], *rest]
suite = runpy.run_path(str(ROOT / "tools" / "unseen_eval.py"), run_name="team_unseen_protocol")


def run(candidate, baseline, maps, seeds, jobs, seed_base):
    assert 1 <= jobs <= 4
    label = ("blind" if "NO_KNOWN_MAPS=1" in candidate else "ladder") if "/" not in maps[0] else maps[0].split("/")[0]
    output = f"results/{opts.label}-{label}.json"
    command = [sys.executable, str(HERE / "tools" / "pool.py"), candidate, "--pool", baseline,
               "--maps", ",".join(maps), "--seeds", str(seeds), "--jobs", str(jobs),
               "--seed-base", str(seed_base), "--output", output]
    process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    result = json.loads((HERE / output).read_text())
    assert result["errors"] == 0
    lo, hi = result["wilson95"]
    return result["score"], result["games"], f"{result['score']:.1f}/{result['games']} = {result['rate']:.3f}, 95% [{lo:.3f}, {hi:.3f}]"


suite["main"].__globals__["run"] = run
suite["main"]()
