#!/usr/bin/env python3
"""One isolated batch; reuse read-only repo builders, retain every result/error."""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import pathlib
import re
import resource
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
import arena
from pool import interval

arena.BIN = HERE / "build"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["UNSWBC_NO_UPDATE"] = "1"
os.environ["TMPDIR"] = str(HERE / "build")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--pool", default="variants/v13")
    ap.add_argument("--maps", default="gen")
    ap.add_argument("--map-dir", help="Read all .map files from a custom fixture directory")
    ap.add_argument("--replays", action="store_true", help="Keep replays under this run's results directory")
    ap.add_argument("--debug", action="store_true", help="Retain LOG/INDICATOR events for mechanism analysis")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--seed-base", type=int, required=True)
    ap.add_argument("--jobs", type=int, default=4, choices=range(1, 5))
    ap.add_argument("--output", required=True)
    ap.add_argument("--sandbox", action="store_true", help="Use prepared source directories and judge metering")
    a = ap.parse_args()
    dest = (HERE / a.output).resolve()
    assert dest.is_relative_to(HERE) and not dest.exists(), "Use a new output inside codex-battlecode"
    # macOS truncates `comm` paths; ucomm supplies the executable basename.
    processes = subprocess.run(["ps", "-axo", "pid=,ucomm=,args="], capture_output=True, text=True, check=True).stdout
    active = [line for line in processes.splitlines()
              if len(line.split()) > 2 and re.search(r"python", line.split()[1], re.I)
              and re.search(r"(?:pool|arena|evaluate|unseen_eval)\.py", line)
              and int(line.split()[0]) != os.getpid()
              and not (int(line.split()[0]) == os.getppid()
                       and "codex-battlecode/tools/unseen_eval.py" in line)]
    if active:
        sys.exit("Another test batch is active; wait: " + "\n".join(active))
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (max(soft, min(8192, hard)), hard))
    maps = ([p.relative_to(ROOT / "maps").with_suffix("").as_posix()
             for p in sorted((ROOT / "maps" / a.maps).glob("*.map"))]
            if a.maps in ("gen", "genhold") else
            arena.RANKED if a.maps == "ranked" else a.maps.split(","))
    assert maps
    if a.map_dir:
        maps = [str(p.resolve()) for p in sorted(pathlib.Path(a.map_dir).glob("*.map"))]
        assert maps, "No fixture maps found"
    def build(spec):
        if a.sandbox:
            assert ":" not in spec, "Sandbox builds need a prepared source snapshot"
            path = (ROOT / spec).resolve()
            assert path.is_relative_to(HERE), "Sandbox builds must use our own snapshots"
            return str(path)
        return arena.build(spec)
    candidate = build(a.candidate)
    opponents = [(spec, build(spec)) for spec in a.pool.split(",")]
    toolkit = pathlib.Path(shutil.which("unswbc"))
    toolkit_python = toolkit.read_text().splitlines()[0].removeprefix("#!")
    dest.parent.mkdir(parents=True, exist_ok=True)
    log = dest.with_suffix(".jsonl").open("x")
    started = time.monotonic()

    def play(spec, opponent, mp, seed, swapped):
        bots = [opponent, candidate] if swapped else [candidate, opponent]
        map_path = pathlib.Path(mp) if pathlib.Path(mp).is_absolute() else ROOT / "maps" / (mp + ".map")
        cmd = [toolkit_python, str(HERE / "tools" / "local_unswbc.py"), "run", str(map_path), *bots,
               "--seed", str(seed)]
        if not a.debug:
            cmd.append("--no-debug")
        if a.replays:
            replay_dir = dest.parent / (dest.stem + "-replays")
            replay_dir.mkdir(parents=True, exist_ok=True)
            replay = replay_dir / f"{map_path.stem}-{pathlib.Path(opponent).name}-{seed}-{'B' if swapped else 'A'}.replay"
            cmd += ["-o", str(replay)]
        else:
            replay = None
            cmd.append("--no-replay")
        if a.sandbox:
            cmd.append("--sandbox")
        begin = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, timeout=600)
        except subprocess.TimeoutExpired as error:
            def decoded(value):
                return value.decode(errors="replace") if isinstance(value, bytes) else value or ""
            p = subprocess.CompletedProcess(cmd, 124, decoded(error.stdout),
                                            decoded(error.stderr) + "\nHARNESS WALL TIMEOUT 600s\n")
        output = p.stdout + p.stderr
        win = arena.WIN.search(output)
        # Failures never silently become draws or losses.
        winner = win.group(1) if win else "D" if re.search(r"(?:draw|tie) after|game (?:draw|tie)", output, re.I) else "?"
        error = p.returncode != 0 or winner == "?"
        row = dict(opponent=spec, map=mp, seed=seed, side="B" if swapped else "A",
                   winner=winner, score=None if error else 0.5 if winner == "D" else float(winner == ("B" if swapped else "A")),
                   seconds=time.monotonic() - begin, returncode=p.returncode,
                   replay=str(replay) if replay else None,
                   output=output)
        return row

    rows = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futures = [ex.submit(play, spec, opp, mp, a.seed_base + seed, side)
                   for spec, opp in opponents for mp in maps for seed in range(a.seeds) for side in (False, True)]
        print(f"Started {len(futures)} games, {a.jobs} workers, seed base {a.seed_base}", flush=True)
        for future in cf.as_completed(futures):
            row = future.result()
            rows.append(row)
            log.write(json.dumps(row) + "\n")
            log.flush()
            if len(rows) % 20 == 0 or row["score"] is None:
                valid = [r["score"] for r in rows if r["score"] is not None]
                print(f"{len(rows)}/{len(futures)} games; score {sum(valid):.1f}/{len(valid)}; errors {len(rows)-len(valid)}", flush=True)
    valid = [r["score"] for r in rows if r["score"] is not None]
    summary = dict(candidate=a.candidate, pool=a.pool, maps=maps, seed_base=a.seed_base,
                   sandbox=a.sandbox,
                   seeds=a.seeds, games=len(rows), errors=len(rows)-len(valid), score=sum(valid),
                   rate=sum(valid)/max(1, len(valid)), wilson95=interval(sum(valid), len(valid)),
                   elapsed_seconds=time.monotonic()-started,
                   file_limit=resource.getrlimit(resource.RLIMIT_NOFILE)[0],
                   finished=datetime.datetime.now(datetime.timezone.utc).isoformat())
    summary["per_map"] = {mp: [sum(r["score"] for r in rows if r["map"] == mp and r["score"] is not None),
                                sum(r["map"] == mp and r["score"] is not None for r in rows)] for mp in maps}
    dest.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("maps", "per_map")}), flush=True)
    return bool(summary["errors"])


if __name__ == "__main__":
    sys.exit(main())
