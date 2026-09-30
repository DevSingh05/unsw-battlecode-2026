#!/usr/bin/env python3
"""Play KC vs v29 (both sides) with replays for kmetrics.py.  python3 notes/king_consensus/mkreplays.py OUTDIR MAPS SEEDS JOBS"""
import sys, os, shutil, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from arena import build, play
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
maps = sys.argv[2].split(','); seeds = int(sys.argv[3]); jobs = int(sys.argv[4])
bd = out / 'bin'; bd.mkdir(exist_ok=True)
kc = bd / 'KC'; v = bd / 'v29'
shutil.copy(build('bot:-DKING_CONSENSUS=1'), kc); shutil.copy(build('variants/v29'), v)
with cf.ThreadPoolExecutor(jobs) as ex:
    fs = [ex.submit(play, str(a), str(b), mp, 1000 + s, str(out)) for mp in maps for s in range(seeds) for a, b in ((kc, v), (v, kc))]
    for f in fs: print(f.result(), flush=True)
