#!/usr/bin/env python3
"""ASCII render of a .map: walls as | and _, spawn tiles by rate, dragons by team.

usage: showmap.py maps/foo.map
Tile chars: '#' gap [1,1], '+' mean gap <= 10, 'o' <= 50, '.' spawns rarely, ' ' never.
Dragon heads A/B, bodies a/b. Portal edges shown as 'P'.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from genmaps import parse  # noqa: E402


def main():
    m = parse(pathlib.Path(sys.argv[1]))
    w, h, nxt = m["w"], m["h"], m["nxt"]
    body = {}
    for team, pts in m["dragons"]:
        for i, p in enumerate(pts):
            body[p] = ("AB"[team] if i == 0 else "ab"[team])
    print(m["name"], w, "x", h, "sym", m["sym"], "dragons", len(m["dragons"]))
    print("    " + "".join(f"{x % 10} " for x in range(w)))
    for y in range(h):
        top = "    "
        row = f"{y:3d} "
        for x in range(w):
            t = y * w + x
            n = nxt[t * 4 + 0]
            plain_n = ((y - 1) % h) * w + x
            top += ("__" if n == -1 else "PP" if n != plain_n else "  ")
            wv = nxt[t * 4 + 3]
            plain_w = y * w + (x - 1) % w
            wall = "|" if wv == -1 else "P" if wv != plain_w else " "
            mn, mx = m["gmin"][t], m["gmax"][t]
            if (x, y) in body:
                c = body[(x, y)]
            elif mx == 0:
                c = " "
            elif mx == 1:
                c = "#"
            elif (mn + mx) / 2 <= 10:
                c = "+"
            elif (mn + mx) / 2 <= 50:
                c = "o"
            else:
                c = "."
            row += wall + c
        print(top)
        print(row)


if __name__ == "__main__":
    main()
