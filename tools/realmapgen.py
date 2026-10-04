#!/usr/bin/env python3
"""Realistic unseen-map generator modelled on the 17 official maps (notes/newrules/UNSEEN_GENERALISATION.md 6.4).

usage: python3 tools/realmapgen.py OUTDIR COUNT SEED [--prefix rg]
       (run from the project root; writes OUTDIR/<prefix><seed>_<i>.map, never overwrites an existing file)

Each map mixes motifs taken from the official designs and must pass the official-range checks in accept()
(stats from notes/newrules/mapstats.py; --official-sizes keeps the official W x H exactly, which makes every map
a look-alike candidate for the bot's known-map matcher):
  vault      portal-only rich room per side, entered by one portal door (Australia, Schooltime yard, QoS rooms)
  pen        sealed home pen whose exits are portals (Trauma, Portals)
  midrich    poor home, rich contested middle (weakhold, Tower Defense, Maze)
  mazeband   band of 1-wide serpentine corridors with dead-end tips across the middle (Maze, Schooltime band)
  bands      full-width kelp lines, bands linked by portals (Stripes)
  open       big, sparse kelp (Around UNSW)
Queen (first DRAGON pair) spawn is protected, as in the 1.2.6 maps: a sealed box, a cup with one door, the pen,
or the back of the home half. Symmetry is xy (75%) or y. Food is clustered in mirrored rate classes.
"""
import argparse
import collections
import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reference" / "loong"))
sys.path.insert(0, str(ROOT / "notes" / "newrules"))
from harness.mapgen import GeneratedMap, mirror_tile, mirror_edge, serialise_map  # noqa: E402
import mapstats  # noqa: E402

DIRS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
DIMS = [(24, 12), (32, 16), (32, 32), (40, 15), (40, 20), (48, 24), (54, 18), (56, 40), (60, 40), (63, 27),
        (64, 64), (25, 35), (25, 25), (44, 30), (36, 36), (64, 32), (50, 50), (48, 48)]
OFFICIAL = [(54, 18), (32, 32), (32, 16), (25, 35), (60, 40), (63, 27), (48, 24), (25, 25), (64, 64), (56, 40), (24, 12),
            (40, 15)]
# rate classes seen on the official maps (min, max gap) and their weights
CLASSES = [((1, 1), 3), ((1, 4), 12), ((1, 10), 18), ((10, 30), 25), ((40, 200), 32), ((400, 500), 5), ((20, 200), 5)]


def edge_of(m, t, d):
    x, y = t
    return {"N": ("N", x, y), "S": ("N", x, (y + 1) % m.height), "W": ("W", x, y), "E": ("W", (x + 1) % m.width, y)}[d]


def step(m, t, d):
    dx, dy = DIRS[d]
    return ((t[0] + dx) % m.width, (t[1] + dy) % m.height)


class Gen:
    def __init__(self, rng, name, exact=False):
        self.r = rng
        w, h = rng.choice(OFFICIAL if exact else DIMS)
        if not exact:
            w = max(20, min(64, w + rng.randint(-4, 4)))
            h = max(12, min(64, h + rng.randint(-3, 3)))
        self.m = GeneratedMap(width=w, height=h, symmetry="xy" if rng.random() < 0.75 else "y",
                              declare_symmetry=True, name=name)
        self.reserved = set()  # tiles inside structures (no random kelp / dragons there)
        self.next_pid = 0
        self.motifs = []
        self.queen_mode = None
        self.food_bias = {}  # tile -> forced class

    # ---------- primitives
    def half_a(self, t):
        return t[0] < self.m.width // 2

    def kelp(self, e):
        m = self.m
        if e in m.portals or mirror_edge(m, e) in m.portals:
            return
        m.kelp.add(e)
        m.kelp.add(mirror_edge(m, e))

    def unkelp(self, e):
        self.m.kelp.discard(e)
        self.m.kelp.discard(mirror_edge(self.m, e))

    def portal_pair(self, e1, e2):
        """e1/e2 same orientation, both off the mirror line; adds the pair and its mirror pair."""
        m = self.m
        if e1[0] != e2[0]:
            return False
        group = [e1, e2, mirror_edge(m, e1), mirror_edge(m, e2)]
        if any(mirror_edge(m, e) == e for e in (e1, e2)) or len(set(group)) < 4:
            return False
        if any(e in m.portals for e in group):
            return False
        for e in group:
            m.kelp.discard(e)
        m.portals[e1] = m.portals[e2] = self.next_pid
        m.portals[group[2]] = m.portals[group[3]] = self.next_pid + 1
        self.next_pid += 2
        return True

    def rect_box(self, x0, y0, bw, bh, doors=()):
        """Kelp around the rectangle [x0,x0+bw) x [y0,y0+bh) (team A frame, mirrored); doors = edges left open."""
        m = self.m
        es = []
        for x in range(x0, x0 + bw):
            es.append(("N", x % m.width, y0 % m.height))
            es.append(("N", x % m.width, (y0 + bh) % m.height))
        for y in range(y0, y0 + bh):
            es.append(("W", x0 % m.width, y % m.height))
            es.append(("W", (x0 + bw) % m.width, y % m.height))
        for e in es:
            if e not in doors:
                self.kelp(e)
        tiles = {((x0 + i) % m.width, (y0 + j) % m.height) for i in range(bw) for j in range(bh)}
        for t in tiles:
            self.reserved.add(t)
            self.reserved.add(mirror_tile(m, t))
        return es, tiles

    def free_rect(self, bw, bh, xmax=None, margin=1):
        m = self.m
        xmax = xmax if xmax is not None else m.width // 2 - bw - 1
        for _ in range(200):
            if xmax < 1:
                return None
            x0 = self.r.randint(1, max(1, xmax))
            y0 = self.r.randint(1, max(1, m.height - bh - 1))
            area = {((x0 + i) % m.width, (y0 + j) % m.height) for i in range(-margin, bw + margin)
                    for j in range(-margin, bh + margin)}
            if area & self.reserved:
                continue
            if any(not self.half_a(t) for t in area):
                continue
            return x0, y0
        return None

    def open_main_edge(self, side):
        """A random open edge of orientation `side` between two unreserved team-A-half tiles."""
        m = self.m
        for _ in range(400):
            x, y = self.r.randrange(1, m.width // 2 - 1), self.r.randrange(m.height)
            e = (side, x, y)
            a = (x, y)
            b = (x, (y - 1) % m.height) if side == "N" else ((x - 1) % m.width, y)
            if a in self.reserved or b in self.reserved or e in m.kelp or e in m.portals:
                continue
            if mirror_edge(m, e) == e:
                continue
            return e
        return None

    # ---------- base kelp
    def base_kelp(self, density):
        m = self.m
        n = int(m.width * m.height * density)
        for _ in range(n):
            x, y = self.r.randrange(m.width), self.r.randrange(m.height)
            length = self.r.randint(2, max(3, min(m.width, m.height) // 4))
            horiz = self.r.random() < 0.5
            for k in range(length):
                t = ((x + k) % m.width, y) if horiz else (x, (y + k) % m.height)
                if t in self.reserved:
                    break
                self.kelp(("N", t[0], t[1]) if horiz else ("W", t[0], t[1]))
        # a few pillars / small rooms with 1-2 doors
        for _ in range(self.r.randint(0, max(1, m.width * m.height // 400))):
            bw, bh = self.r.randint(3, 7), self.r.randint(3, 6)
            pos = self.free_rect(bw, bh)
            if not pos:
                continue
            es, tiles = self.rect_box(*pos, bw, bh)
            for e in self.r.sample(es, self.r.randint(1, 3)):
                self.unkelp(e)
            for t in tiles:  # rooms are not structures: allow later kelp/dragons
                self.reserved.discard(t)
                self.reserved.discard(mirror_tile(m, t))

    # ---------- motifs
    def vault(self):
        bw, bh = self.r.randint(4, 8), self.r.randint(3, 6)
        pos = self.free_rect(bw, bh)
        if not pos:
            return False
        x0, y0 = pos
        es, tiles = self.rect_box(x0, y0, bw, bh)
        door = ("N", x0 + self.r.randrange(bw), y0)  # top wall: crossing the outer edge moving S lands inside
        outer = self.open_main_edge("N")
        if not outer or not self.portal_pair(outer, door):
            return False
        cls = self.r.choice([(1, 4), (1, 10), (5, 30), (1, 1)])
        for t in tiles:
            if self.r.random() < 0.7:
                self.food_bias[t] = cls
        self.motifs.append("vault")
        return True

    def pen(self):
        m = self.m
        bw, bh = self.r.randint(7, 11), self.r.randint(5, min(9, m.height - 3))
        pos = self.free_rect(bw, bh, xmax=max(1, m.width // 4 - bw // 2))
        if not pos:
            return None
        x0, y0 = pos
        es, tiles = self.rect_box(x0, y0, bw, bh)
        doors = 0
        for _ in range(20):
            if doors >= 2:
                break
            side = self.r.choice("NW")
            if side == "N":
                d = ("N", x0 + self.r.randrange(bw), self.r.choice([y0, y0 + bh]) % m.height)
            else:
                d = ("W", self.r.choice([x0, x0 + bw]) % m.width, y0 + self.r.randrange(bh))
            outer = self.open_main_edge(side)
            if outer and self.portal_pair(outer, d):
                doors += 1
        if doors == 0:
            return None
        for t in tiles:
            if self.r.random() < 0.25:
                self.food_bias[t] = (40, 200)
            else:
                self.food_bias[t] = (0, 0)
        self.motifs.append("pen")
        return tiles

    def midrich(self):
        m = self.m
        band = max(2, m.width // self.r.choice([8, 6, 5]))
        mid = m.width // 2
        for x in range(m.width):
            for y in range(m.height):
                t = (x, y)
                if t in self.food_bias:
                    continue
                if abs(x - mid + 0.5) <= band and self.r.random() < 0.35:
                    self.food_bias[t] = self.r.choice([(1, 10), (10, 30), (10, 30), (40, 200)])
                elif (x < m.width // 4 or x >= m.width - m.width // 4) and self.r.random() < 0.9:
                    self.food_bias[t] = (0, 0)
        self.motifs.append("midrich")

    def mazeband(self):
        m = self.m
        bw = self.r.randint(3, max(4, m.width // 6))
        x0 = m.width // 2 - bw
        rows = list(range(1, m.height - 1, 2))
        for i, y in enumerate(rows):
            gap = x0 if i % 2 == 0 else x0 + bw - 1
            for x in range(x0, x0 + bw):
                t = (x, y)
                if t in self.reserved or x == gap:
                    continue
                self.kelp(("N", x, y))
        # dead-end tips with fast food on the band's edge
        for _ in range(self.r.randint(2, 5)):
            y = self.r.choice(rows)
            x = x0 - 1
            if (x, y) in self.reserved:
                continue
            self.kelp(("N", x, y))
            self.kelp(("N", x, (y + 1) % m.height))
            self.food_bias[(x, y)] = self.r.choice([(1, 4), (1, 10), (5, 15)])
        self.motifs.append("mazeband")

    def bands(self):
        m = self.m
        if m.height < 12:
            return False
        bh = self.r.randint(3, 5)
        ys = list(range(bh, m.height // 2, bh))
        for y in ys:
            for x in range(m.width):
                self.kelp(("N", x, y))
        # link bands with portals (shortcut doors between bands, both orientations)
        for y in ys:
            for _ in range(self.r.randint(1, 2)):
                e_low = ("N", self.r.randrange(1, m.width // 2 - 1), y)
                other = self.open_main_edge("N")
                if other:
                    self.portal_pair(other, e_low)
        self.motifs.append("bands")
        return True

    def queen_box(self):
        bw, bh = self.r.choice([(3, 2), (2, 3), (3, 3)])
        pos = self.free_rect(bw, bh, xmax=max(1, self.m.width // 3))
        if not pos:
            return None
        es, tiles = self.rect_box(*pos, bw, bh)
        food = self.r.choice(sorted(tiles))
        for t in tiles:
            self.food_bias[t] = (0, 0)
        self.food_bias[food] = (20, 200)
        return tiles

    def queen_cup(self):
        bw, bh = self.r.randint(4, 7), self.r.randint(4, 6)
        pos = self.free_rect(bw, bh, xmax=max(1, self.m.width // 3))
        if not pos:
            return None
        x0, y0 = pos
        es, tiles = self.rect_box(x0, y0, bw, bh)
        side = self.r.choice(es)
        self.unkelp(side)
        if self.r.random() < 0.5:  # a 2-tile door
            s, x, y = side
            self.unkelp((s, x + 1, y) if s == "N" else (s, x, y + 1))
        for t in tiles:
            self.food_bias[t] = (0, 0)
        return tiles

    # ---------- food
    def food(self):
        m = self.m
        target = self.r.uniform(0.08, 0.28) * m.width * m.height
        spawn = {}
        for t, c in self.food_bias.items():
            if c != (0, 0):
                spawn[t] = c
        tries = 0
        while len(spawn) * 2 < target and tries < 2000:
            tries += 1
            c = (self.r.randrange(m.width // 2), self.r.randrange(m.height))
            if self.food_bias.get(c) == (0, 0):
                continue
            cls = self.r.choices([k for k, _ in CLASSES], weights=[w for _, w in CLASSES])[0]
            size = self.r.randint(2, 14)
            q, seen = [c], {c}
            while q and len(seen) < size:
                t = q.pop(self.r.randrange(len(q)))
                for d in "NESW":
                    u = step(m, t, d)
                    if u not in seen and edge_of(m, t, d) not in m.kelp and self.food_bias.get(u) != (0, 0):
                        seen.add(u)
                        q.append(u)
            for t in seen:
                if t not in spawn and self.food_bias.get(t) != (0, 0):
                    spawn[t] = cls
        for x in range(m.width):
            for y in range(m.height):
                m.spawn_ranges[(x, y)] = (0, 0)
        for t, c in spawn.items():
            m.spawn_ranges[t] = c
            m.spawn_ranges[mirror_tile(m, t)] = c

    # ---------- dragons
    def can_link(self, a, b):
        for d in "NESW":
            if step(self.m, a, d) == b:
                e = edge_of(self.m, a, d)
                return e not in self.m.kelp and e not in self.m.portals
        return False

    def body_from(self, head, length, occupied, region=None):
        m = self.m
        body = [head]
        while len(body) < length:
            opts = []
            for d in "NESW":
                u = step(m, body[-1], d)
                if u in body or u in occupied or not self.half_a(u) or not self.can_link(body[-1], u):
                    continue
                if region is not None and u not in region:
                    continue
                opts.append(u)
            if not opts:
                return None
            if len(body) >= 2:
                st = (2 * body[-1][0] - body[-2][0], 2 * body[-1][1] - body[-2][1])
                if st in opts and self.r.random() < 0.7:
                    opts = [st]
            body.append(self.r.choice(opts))
        return body

    def far_ok(self, body, occupied):
        m = self.m
        enemy = [mirror_tile(m, t) for t in body] + [mirror_tile(m, t) for t in occupied]
        def cheb(a, b):
            dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
            return max(min(dx, m.width - dx), min(dy, m.height - dy))
        if any(cheb(a, b) < 4 for a in body + list(occupied) for b in enemy):
            return False
        return not any(cheb(a, b) < 2 for a in body for b in occupied)

    def place(self, queen_region):
        m = self.m
        r = self.r
        per_team = r.choices([2, 3, 4, 5, 6, 9], weights=[30, 30, 20, 8, 7, 5])[0]
        qlen = r.choice([3, 3, 4, 4, 5])
        lens = [qlen]
        big = r.random() < 0.15
        for i in range(per_team - 1):
            lens.append(r.randint(8, 14) if big and i == 0 else r.choice([2, 3, 3, 4, 4, 5, 6]))
        occupied = set()
        free = [(x, y) for x in range(m.width // 2) for y in range(m.height) if (x, y) not in self.reserved]
        for i, L in enumerate(lens):
            ok = False
            for _ in range(300):
                if i == 0 and queen_region:
                    region = queen_region
                    head = r.choice(sorted(region))
                    L = min(L, max(2, len(region) - 1)) if self.queen_mode == "box" else L
                elif i == 0 and self.queen_mode == "back":
                    xs = max(1, m.width // 8)
                    head = r.choice([t for t in free if t[0] < xs] or free)
                    region = None
                else:
                    head = r.choice(free)
                    region = None
                body = self.body_from(head, L, occupied, region)
                if not body or not self.far_ok(body, occupied):
                    continue
                exits = sum(1 for d in "NESW" if self.can_link(head, step(m, head, d)) and step(m, head, d) not in body
                            and step(m, head, d) not in occupied)
                if exits < 1:
                    continue
                occupied.update(body)
                m.dragons.append((0, body))
                m.dragons.append((1, [mirror_tile(m, t) for t in body]))
                ok = True
                break
            if not ok:
                if i == 0:
                    return False
                break
        return len(m.dragons) >= 4

    # ---------- build
    def build(self):
        r = self.r
        m = self.m
        open_map = m.width * m.height >= 2000 and r.random() < 0.25
        if open_map:
            self.motifs.append("open")
        # queen protection first (it needs room near home)
        mode = r.choices(["box", "cup", "pen", "back"], weights=[10, 20, 15, 55])[0]
        qreg = None
        if mode == "pen":
            qreg = self.pen()
        elif mode == "box":
            qreg = self.queen_box()
        elif mode == "cup":
            qreg = self.queen_cup()
        if qreg is None:
            mode = "back"
        self.queen_mode = mode
        if r.random() < 0.55:
            self.vault()
            if r.random() < 0.3:
                self.vault()
        if r.random() < 0.4:
            self.midrich()
        if not open_map and r.random() < 0.3:
            self.mazeband()
        if not open_map and mode != "pen" and r.random() < 0.1:
            self.bands()
        if r.random() < 0.5:  # kelp on the wrap border (most official maps), with a few gaps
            gap = r.choice([0, 0, 6, 9])
            for x in range(m.width):
                if (not gap or x % gap) and (x, 0) not in self.reserved and (x, m.height - 1) not in self.reserved:
                    self.kelp(("N", x, 0))
            for y in range(m.height):
                if (not gap or y % gap) and (0, y) not in self.reserved and (m.width - 1, y) not in self.reserved:
                    self.kelp(("W", 0, y))
        self.base_kelp(r.uniform(0.004, 0.012) if open_map else r.uniform(0.02, 0.05))
        # a few plain shortcut portals
        for _ in range(r.randint(0, 3)):
            e1 = self.open_main_edge("N")
            e2 = self.open_main_edge("N")
            if e1 and e2 and e1 != e2:
                self.portal_pair(e1, e2)
        self.food()
        if not self.place(qreg if mode in ("box", "cup", "pen") else None):
            return False
        return True


def teams_meet(path):
    """Some team-A dragon can reach some team-B dragon (portals allowed): the teams are not walled apart."""
    m = mapstats.parse(path)
    heads = [p[1][0][1] * m['w'] + p[1][0][0] for p in m['dragons']]
    teams = [p[0] for p in m['dragons']]
    D = mapstats.bfs(m, [h for h, t in zip(heads, teams) if t == 0])
    return any(D[h] >= 0 for h, t in zip(heads, teams) if t == 1)


def accept(path):
    s = mapstats.stats(path)
    if not teams_meet(path):
        return False, s
    ok = (0.07 <= s["kelp"] <= 0.32 and 0.04 <= s["corr"] <= 0.42 and s["deadend"] <= 0.16
          and 0.05 <= s["spf"] <= 0.40 and s.get("dqe", 99) != 0 and (s["dqq"] == -1 or s["dqq"] >= 20)
          and (s.get("dqe", 99) == -1 or s.get("dqe", 99) >= 12) and s["sealed"] <= 0.25 and s["rate"] > 0)
    return ok, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("count", type=int)
    ap.add_argument("seed", type=int)
    ap.add_argument("--prefix", default="rg")
    ap.add_argument("--official-sizes", action="store_true",
                    help="use the official map sizes exactly (stress test for known-map look-alikes)")
    a = ap.parse_args()
    out = pathlib.Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(a.seed)
    tmp = pathlib.Path(tempfile.gettempdir()) / f"realmapgen_{a.seed}.map"
    made = tries = 0
    while made < a.count and tries < a.count * 400:
        tries += 1
        name = f"{a.prefix}{a.seed}_{made:02d}"
        g = Gen(rng, name, a.official_sizes)
        try:
            if not g.build():
                continue
        except (IndexError, ValueError, StopIteration):
            continue
        text = serialise_map(g.m)
        tmp.write_text(text)
        try:
            ok, s = accept(tmp)
        except Exception:
            continue
        if not ok:
            continue
        dst = out / f"{name}.map"
        if dst.exists():
            print(f"exists, skipped: {dst}")
            made += 1
            continue
        dst.write_text(text)
        made += 1
        print(f"{name} {g.m.width}x{g.m.height} {g.m.symmetry} queen={g.queen_mode} motifs={','.join(g.motifs) or '-'} "
              f"kelp={s['kelp']:.2f} corr={s['corr']:.2f} pp={s['pp']:.0f} spf={s['spf']:.2f} dqq={s['dqq']} "
              f"ponly_food={s['ponly_food']:.2f} hot={s['hot']}", flush=True)
    print(f"wrote {made} maps to {out} ({tries} tries)")


if __name__ == "__main__":
    main()
