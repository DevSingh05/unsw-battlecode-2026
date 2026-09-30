#!/usr/bin/env python3
"""Write unseen, plausible maps for Sprint-style testing (wraps the Loong series' generator).

usage: mapgen.py OUTDIR COUNT SEED
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "reference" / "loong"))
from harness.mapgen import generate_map, serialise_map  # noqa: E402


def main():
    out, count, seed = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    i = 0
    while i < count:
        try:
            m = generate_map(rng, f"g{seed}_{i:02d}")
        except (IndexError, ValueError):
            continue  # the generator occasionally paints itself into a corner; draw again
        (out / f"g{seed}_{i:02d}.map").write_text(serialise_map(m))
        i += 1
    print(f"wrote {count} maps to {out}")


if __name__ == "__main__":
    main()
