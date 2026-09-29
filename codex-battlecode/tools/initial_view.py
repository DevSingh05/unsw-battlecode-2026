#!/usr/bin/env python3
"""Build a no-food round-zero observation for targeted deterministic fixtures."""
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "notes" / "tools"))
from replay_sim import Map


def observation(path, ident=0):
    text = pathlib.Path(path).read_text()
    m = Map(text)
    assert all(high == 0 for _, high in m.tiles.values()), "Only no-food fixtures have deterministic round-zero timers"
    limit = next((int(line.split()[1]) for line in text.splitlines() if line.startswith("UNIT_LIMIT ")), 64)
    team, body = m.dragons[ident]
    hx, hy = body[0]
    def direction(origin, target):
        return next(d for d in "NESW" if m.step(origin, d) == target)
    lines = [f"ID {ident}", f"TEAM {'AB'[team]}", f"MAP {m.w} {m.h}", f"UNIT_LIMIT {limit}",
             "ROUND 0", f"DIR {direction(body[1], body[0])}", f"LENGTH {len(body)}",
             f"UNIT_COUNT {sum(t == team for t, _ in m.dragons)}", "NUM_MSGS 0", "ECHOES 0 0 0 0 0"]
    visible = set()
    for y in range(hy - 3, hy + 4):
        for x in range(hx - 3, hx + 4):
            p = m.wrap(x, y)
            visible.add(p)
            lines.append(f"{p[0]} {p[1]} 0 -1")
    parts = []
    for dragon, (side, segments) in enumerate(m.dragons):
        for i, p in enumerate(segments):
            if p in visible:
                face = direction(segments[1], segments[0]) if i == 0 else direction(p, segments[i - 1])
                parts.append(f"{'AB'[side]} {dragon} {p[0]} {p[1]} {face} {int(i == 0)}")
    lines += [f"DRAGON_BODIES {len(parts)}", *parts]
    for orient, rows, cols in [("H", 8, 7), ("V", 7, 8)]:
        for row in range(rows):
            tokens = []
            for col in range(cols):
                k, pid = m.edges.get((orient, (hx + col - 3) % m.w, (hy + row - 3) % m.h), (0, -1))
                tokens.append("." if k == 0 else "w" if k == 1 else str(pid))
            lines.append(" ".join(tokens))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(observation(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0), end="")
