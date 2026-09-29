#!/usr/bin/env python3
"""Deterministic engine-valid stress fixtures, entirely inside this sandbox."""
import json
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parents[1]
OUT = HERE / "maps" / "extreme_v24"


class Map:
    def __init__(self, name, w, h, food=(0, 0), units=64):
        self.name, self.w, self.h, self.food, self.units = name, w, h, food, units
        self.edges, self.dragons = {}, []

    def mirror(self, p):
        return self.w - 1 - p[0], self.h - 1 - p[1]

    def mirror_edge(self, e):
        kind, x, y = e
        return (kind, self.w - 1 - x, (-y) % self.h) if kind == "H" else (kind, (-x) % self.w, self.h - 1 - y)

    def pair_start(self, body):
        self.dragons.extend([(0, body), (1, [self.mirror(p) for p in body])])

    def starts(self, count=1):
        for k in range(count):
            y = 1 + 2 * k
            assert y < self.h // 2
            self.pair_start([(2, y), (1, y), (0, y)])

    def body_edges(self):
        edges = set()
        for _, body in self.dragons:
            for (x, y), (a, b) in zip(body, body[1:]):
                if y == b:
                    edges.add(("V", x if (x - a) % self.w == 1 else a, y))
                else:
                    edges.add(("H", x, y if (y - b) % self.h == 1 else b))
        return edges

    def portals(self, mirrored_pairs):
        rng = random.Random(92026)
        blocked = self.body_edges()
        for pair in range(mirrored_pairs):
            for _ in range(10000):
                kind = rng.choice(["H", "V"])
                a = kind, rng.randrange(self.w), rng.randrange(self.h)
                b = kind, rng.randrange(self.w), rng.randrange(self.h)
                ma, mb = self.mirror_edge(a), self.mirror_edge(b)
                all_edges = {a, b, ma, mb}
                if len(all_edges) != 4 or any(e in self.edges or e in blocked for e in all_edges):
                    continue
                for e in (a, b): self.edges[e] = (2, 2 * pair)
                for e in (ma, mb): self.edges[e] = (2, 2 * pair + 1)
                break
            else:
                raise RuntimeError("Could not place portals")

    def corridors(self, sealed=False):
        # Two mirrored one-cell-wide rings; nearly every other edge is kelp.
        for y in range(self.h):
            for x in range(self.w):
                self.edges["H", x, y] = (1, -1)
                if y not in (1, self.h - 2): self.edges["V", x, y] = (1, -1)
        if sealed:
            # Each starter has one free step and then an unavoidable collision.
            # This is an action-validity fixture, not a survival expectation.
            for e in [("V", 0, 1), ("V", 4, 1)]:
                self.edges[e] = self.edges[self.mirror_edge(e)] = (1, -1)

    def write(self):
        occupied = set()
        for _, body in self.dragons:
            assert len(body) >= 2
            for p in body:
                assert p not in occupied and 0 <= p[0] < self.w and 0 <= p[1] < self.h
                occupied.add(p)
        assert not self.body_edges() & self.edges.keys(), "Starting bodies must not cross kelp/portals"
        assert all(self.edges.get(self.mirror_edge(e)) is not None for e in self.edges)
        tiles = [(x, y) for y in range(self.h) for x in range(self.w)] if self.food[1] else []
        lines = [f"MAP {self.w} {self.h}", f"MAP_NAME {self.name}", "SYMMETRY xy", f"UNIT_LIMIT {self.units}", f"TILE_COUNT {len(tiles)}"]
        lines += [f"TILE {x} {y} {self.food[0]} {self.food[1]}" for x, y in tiles]
        lines += [f"EDGE_COUNT {len(self.edges)}"]
        for (o, x, y), (kind, pid) in sorted(self.edges.items()):
            index = (2 * y + (o == "V")) * (self.w + 1) + x
            lines.append(f"EDGE {index} {kind} {pid}")
        lines.append(f"DRAGON_COUNT {len(self.dragons)}")
        for team, body in self.dragons:
            lines.append(f"DRAGON {team} {len(body)} " + " ".join(f"{x} {y}" for x, y in body))
        path = OUT / (self.name + ".map")
        assert not path.exists()
        path.write_text("\n".join(lines) + "\n")
        return dict(map=path.name, width=self.w, height=self.h, food=self.food, unit_limit=self.units,
                    starts=[sum(t == team for t, _ in self.dragons) for team in (0, 1)],
                    longest_start=max(len(body) for _, body in self.dragons),
                    kelp=sum(k == 1 for k, _ in self.edges.values()), portal_edges=sum(k == 2 for k, _ in self.edges.values()))


def king_tail_escape():
    m = Map("king_tail_escape", 16, 16, units=2)
    m.pair_start([(4, 4), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6), (3, 5), (3, 4)])
    enemy = [(4, 2), (5, 2), (6, 2)]
    m.dragons.extend([(1, enemy), (0, [m.mirror(p) for p in enemy])])
    wall = ("H", 4, 5)
    m.edges[wall] = m.edges[m.mirror_edge(wall)] = (1, -1)
    return m


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    maps = []
    for name, w, h, food in [
        ("tiny7_empty", 7, 7, (0, 0)), ("tiny8_rich", 8, 8, (1, 1)),
        ("tiny8_portals", 8, 8, (1, 5)), ("wide64x7_sparse", 64, 7, (400, 500)),
        ("tall7x64_sparse", 7, 64, (400, 500)), ("max64_empty", 64, 64, (0, 0)),
        ("max64_rich_many", 64, 64, (1, 1)), ("portal32_rich", 32, 32, (1, 2)),
        ("portal32_empty", 32, 32, (0, 0)), ("walls16_rich", 16, 16, (1, 1)),
        ("walls16_forced", 16, 16, (0, 0))]:
        m = Map(name, w, h, food)
        m.starts(16 if name == "max64_rich_many" else 4 if name == "portal32_rich" else 1)
        if name == "tiny8_portals": m.portals(8)
        if name.startswith("portal32"): m.portals(100)
        if name.startswith("walls16"): m.corridors(sealed=name.endswith("forced"))
        maps.append(m)
    coil = Map("max64_long320_no_split", 64, 64, units=1)
    body = [(x, y) for y in range(1, 21) for x in (range(1, 17) if y % 2 else range(16, 0, -1))]
    coil.pair_start(body)
    maps.append(coil)
    asym = Map("asymmetric_one_vs16", 32, 64, (1, 30))
    asym.starts(16)
    asym.dragons = [d for i, d in enumerate(asym.dragons) if d[0] == 1 or i == 0]
    maps.append(asym)
    maps.append(king_tail_escape())
    manifest = [m.write() for m in maps]
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(maps)} stress fixtures to {OUT}")


if __name__ == "__main__":
    main()
