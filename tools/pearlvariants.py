#!/usr/bin/env python3
"""Make pearl-layout variants of known maps: same walls/portals/starts, different pearl tiles/gaps.

usage: pearlvariants.py OUTDIR SEED   (writes <map>_pv<SEED>.map for the 10 ranked maps)
Mirror tiles keep equal gaps, as the engine requires.
"""
import pathlib
import random
import sys

RANKED = ["devil", "schooltime", "portals", "default", "queen_of_spades", "trophy",
          "autarky", "dilemma", "slithery_fight", "trauma"]
GAPS = [(1, 1), (1, 10), (1, 20), (20, 50), (20, 80), (1, 100), (20, 200), (1, 500)]


def mirror(x, y, w, h, sym):
    return {"x": (x, h - 1 - y), "y": (w - 1 - x, y), "xy": (w - 1 - x, h - 1 - y)}.get(sym, (x, y))


def main():
    out, seed = pathlib.Path(sys.argv[1]), int(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    root = pathlib.Path(__file__).resolve().parent.parent
    for name in RANKED:
        rng = random.Random(f"{seed}-{name}")
        lines = (root / "maps" / f"{name}.map").read_text().splitlines()
        w, h = map(int, next(l for l in lines if l.startswith("MAP ")).split()[1:3])
        sym = next((l.split()[1] for l in lines if l.startswith("SYMMETRY")), "none")
        n_tiles = sum(1 for l in lines if l.startswith("TILE "))
        spawn_now = sum(1 for l in lines if l.startswith("TILE ") and l.split()[4] != "0")
        target = max(20, int(spawn_now * rng.uniform(0.5, 1.2)))
        gaps = {}
        cells = [(x, y) for y in range(h) for x in range(w)]
        rng.shuffle(cells)
        # a few pearl "fountains" plus scattered tiles
        for (x, y) in cells:
            if len(gaps) >= target:
                break
            if (x, y) in gaps:
                continue
            g = rng.choice(GAPS)
            gaps[(x, y)] = g
            gaps[mirror(x, y, w, h, sym)] = g
        new = []
        for l in lines:
            if l.startswith("TILE "):
                _, x, y, _, _ = l.split()
                g = gaps.get((int(x), int(y)), (0, 0))
                new.append(f"TILE {x} {y} {g[0]} {g[1]}")
            elif l.startswith("MAP_NAME"):
                new.append(l)  # keep the name: the bot must still recognise the walls
            else:
                new.append(l)
        assert sum(1 for l in new if l.startswith("TILE ")) == n_tiles
        (out / f"{name}_pv{seed}.map").write_text("\n".join(new) + "\n")
    print("wrote pearl variants to", out)


if __name__ == "__main__":
    main()
