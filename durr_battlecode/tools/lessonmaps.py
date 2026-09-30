#!/usr/bin/env python3
"""Write the hand-designed-style "lesson" map suite (see notes/lesson-maps.md).

usage: lessonmaps.py [OUTDIR]   (default maps/lesson; existing files are never overwritten)
       lessonmaps.py --list     (print each map's stats and lesson, write nothing)

Each builder isolates one strategic lesson, in the devs' style: symmetric (x | y | xy), kelp rooms,
portal doors, pearl gap bands like [1,1] hot tiles, [1,20] fountains, [20,200] sparse, and starting
dragons including long coils. Everything is placed through a mirror-aware builder so the engine's
checks (engine/src/config.cc) hold by construction; validate() re-checks them plus reachability.
"""
import pathlib
import random
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# pearl bands used by the ranked maps
HOT = (1, 1)
RICH = (1, 5)
FOUNT = (1, 20)
MID = (1, 100)
SPARSE = (20, 200)
SLOW = (1, 600)
LATE = (150, 250)
VLATE = (480, 490)
NONE = (0, 0)
OFF = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class Map:
    def __init__(self, name, w, h, sym, bg=NONE, seed=None):
        assert 10 <= w <= 64 and 10 <= h <= 64
        self.name, self.w, self.h, self.sym = name, w, h, sym
        self.gaps = {(x, y): bg for x in range(w) for y in range(h)}
        self.edges = {}  # ('H'|'V', x, y) -> (kind, pid); H = north side of tile, V = west side
        self.dragons = []  # (team, [(x, y), ...]) head first
        self.next_pid = 0
        self.rng = random.Random(zlib.crc32(name.encode()) if seed is None else seed)

    # ---- symmetry -------------------------------------------------------------------------------
    def mt(self, p):
        x, y = p
        if self.sym == "x":
            return (x, self.h - 1 - y)
        if self.sym == "y":
            return (self.w - 1 - x, y)
        return (self.w - 1 - x, self.h - 1 - y)

    def me(self, e):
        o, x, y = e
        w, h = self.w, self.h
        if o == "H":
            nx = x if self.sym == "x" else w - 1 - x
            ny = y if self.sym == "y" else (h - y) % h
        else:
            nx = x if self.sym == "x" else (w - x) % w
            ny = y if self.sym == "y" else h - 1 - y
        return (o, nx, ny)

    # ---- tiles ----------------------------------------------------------------------------------
    def tile(self, x, y, g):
        p = (x % self.w, y % self.h)
        self.gaps[p] = g
        self.gaps[self.mt(p)] = g

    def fill(self, x0, y0, x1, y1, g):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.tile(x, y, g)

    def scatter(self, frac, g, where=None):
        cells = sorted(self.gaps) if where is None else where
        for p in cells:
            if self.rng.random() < frac:
                self.tile(*p, g)

    # ---- edges ----------------------------------------------------------------------------------
    def norm(self, e):
        o, x, y = e
        return (o, x % self.w, y % self.h)

    def set_edge(self, e, kind):
        e = self.norm(e)
        for k in (e, self.me(e)):
            old = self.edges.get(k)
            if old and old[0] == 2:
                raise ValueError(f"{self.name}: edge {k} is already a portal")
            if kind == 0:
                self.edges.pop(k, None)
            else:
                self.edges[k] = (kind, -1)

    def kelp(self, e):
        self.set_edge(e, 1)

    def clear(self, e):
        self.set_edge(e, 0)

    def hwall(self, x0, x1, y):
        """kelp on the north side of tiles (x, y), x0..x1"""
        for x in range(x0, x1 + 1):
            self.kelp(("H", x, y))

    def vwall(self, x, y0, y1):
        """kelp on the west side of tiles (x, y), y0..y1"""
        for y in range(y0, y1 + 1):
            self.kelp(("V", x, y))

    def box(self, x0, y0, x1, y1):
        """kelp around the tile rectangle [x0..x1] x [y0..y1]"""
        self.hwall(x0, x1, y0)
        self.hwall(x0, x1, y1 + 1)
        self.vwall(x0, y0, y1)
        self.vwall(x1 + 1, y0, y1)

    def portal(self, a, b):
        """link edges a and b (same orientation); the mirror pair is added automatically"""
        a, b = self.norm(a), self.norm(b)
        assert a[0] == b[0] and a != b, (a, b)
        ma, mb = self.me(a), self.me(b)
        pairs = [(a, b)]
        if {ma, mb} != {a, b}:
            if ma in (a, b) or mb in (a, b):
                raise ValueError(f"{self.name}: portal {a}-{b} touches its own mirror")
            pairs.append((ma, mb))
        for p, q in pairs:
            for e in (p, q):
                if e in self.edges and self.edges[e][0] == 2:
                    raise ValueError(f"{self.name}: edge {e} already a portal")
        for p, q in pairs:
            self.edges[p] = (2, self.next_pid)
            self.edges[q] = (2, self.next_pid)
            self.next_pid += 1

    # ---- dragons --------------------------------------------------------------------------------
    def dragon(self, pts):
        """team A dragon (head first); team B gets the mirror image, listed right after (turn order A,B,A,B...)"""
        pts = [(x % self.w, y % self.h) for x, y in pts]
        self.dragons.append((0, pts))
        self.dragons.append((1, [self.mt(p) for p in pts]))

    @staticmethod
    def line(x, y, facing, n):
        dx, dy = OFF[facing]
        return [(x - dx * i, y - dy * i) for i in range(n)]

    @staticmethod
    def serp(x0, y0, cols, rows, head_first=True):
        """snake filling a cols x rows block row by row (boustrophedon); head at (x0, y0)"""
        pts = []
        for r in range(rows):
            xs = range(cols) if r % 2 == 0 else range(cols - 1, -1, -1)
            pts += [(x0 + c, y0 + r) for c in xs]
        return pts if head_first else pts[::-1]

    # ---- movement / validation ------------------------------------------------------------------
    def side(self, x, y, d):
        if d == "N":
            return ("H", x, y)
        if d == "S":
            return ("H", x, (y + 1) % self.h)
        if d == "W":
            return ("V", x, y)
        return ("V", (x + 1) % self.w, y)

    def step(self, p, d, partner):
        x, y = p
        e = self.side(x, y, d)
        kind = self.edges.get(e, (0, -1))[0]
        if kind == 1:
            return None
        if kind == 2:
            o, ex, ey = partner[e]
            if o == "H":
                return (ex, (ey if d == "S" else ey - 1) % self.h)
            return ((ex if d == "E" else ex - 1) % self.w, ey)
        return ((x + OFF[d][0]) % self.w, (y + OFF[d][1]) % self.h)

    def partners(self):
        ends = {}
        for e, (k, pid) in self.edges.items():
            if k == 2:
                ends.setdefault(pid, []).append(e)
        partner = {}
        for pid, es in ends.items():
            assert len(es) == 2 and es[0][0] == es[1][0], (self.name, pid, es)
            partner[es[0]], partner[es[1]] = es[1], es[0]
        return partner

    def validate(self):
        w, h = self.w, self.h
        for p, g in self.gaps.items():
            assert g == self.gaps[self.mt(p)], (self.name, "gap mirror", p)
            assert g[1] == 0 or 1 <= g[0] <= g[1], (self.name, "bad gap", p, g)
        for e, v in self.edges.items():
            assert self.edges.get(self.me(e), (0, -1))[0] == v[0], (self.name, "edge mirror", e)
        partner = self.partners()
        occ = {}
        for i, (team, pts) in enumerate(self.dragons):
            assert len(pts) >= 2, (self.name, "short dragon")
            for p in pts:
                assert p not in occ, (self.name, "overlap", p, i, occ.get(p))
                occ[p] = i
            for a, b in zip(pts, pts[1:]):
                # consecutive segments must be plainly adjacent with an open edge between them
                ds = [d for d in OFF if ((b[0] + OFF[d][0]) % w, (b[1] + OFF[d][1]) % h) == a]
                assert ds, (self.name, "not adjacent", a, b)
                assert self.side(*b, ds[0]) not in self.edges, (self.name, "edge inside dragon", a, b)
        for i, (team, pts) in enumerate(self.dragons):
            free = [d for d in OFF if (q := self.step(pts[0], d, partner)) is not None and q not in occ]
            assert free, (self.name, "boxed-in head", i, pts[0])
        # every pearl tile and every tile of the board reachable from team A's heads
        seen, todo = set(), [pts[0] for t, pts in self.dragons if t == 0]
        seen.update(todo)
        while todo:
            p = todo.pop()
            for d in OFF:
                q = self.step(p, d, partner)
                if q is not None and q not in seen:
                    seen.add(q)
                    todo.append(q)
        spawn = [p for p, g in self.gaps.items() if g[1] > 0]
        lost = [p for p in spawn if p not in seen]
        assert not lost, (self.name, "unreachable pearl tiles", lost[:5])
        return len(seen) / (w * h)

    # ---- output ---------------------------------------------------------------------------------
    def text(self):
        w, h = self.w, self.h
        out = [f"MAP {w} {h}", f"SYMMETRY {self.sym}", f"MAP_NAME {self.name}", f"TILE_COUNT {w * h}"]
        for y in range(h):
            for x in range(w):
                mn, mx = self.gaps[(x, y)]
                out.append(f"TILE {x} {y} {mn if mx else 0} {mx}")
        es = []
        for (o, x, y), (k, pid) in self.edges.items():
            row = 2 * y if o == "H" else 2 * y + 1
            es.append((row * (w + 1) + x, k, pid))
        es.sort()
        out.append(f"EDGE_COUNT {len(es)}")
        out += [f"EDGE {i} {k} {pid}" for i, k, pid in es]
        out.append(f"DRAGON_COUNT {len(self.dragons)}")
        for team, pts in self.dragons:
            out.append(f"DRAGON {team} {len(pts)} " + " ".join(f"{x} {y}" for x, y in pts))
        out.append("END")
        return "\n".join(out) + "\n"


# ===================================================================================================
# helpers shared by several lessons


def maze(m, s, x0, y0, cw, ch, loops, wrap=False):
    """symmetric Kruskal maze of cw x ch cells of s x s tiles, starting at tile (x0, y0); thin kelp walls.
    The region must be mapped onto itself by the map symmetry. wrap=True also links cells across the torus seam."""
    walls = []
    for cx in range(cw):
        for cy in range(ch):
            if cx + 1 < cw or wrap:
                walls.append(((cx, cy), ((cx + 1) % cw, cy), "V"))
            if cy + 1 < ch or wrap:
                walls.append(((cx, cy), (cx, (cy + 1) % ch), "H"))

    def wall_edges(a, b, o):
        if o == "V":
            x = x0 + (a[0] + 1) * s
            return [("V", x, y0 + a[1] * s + i) for i in range(s)]
        y = y0 + (a[1] + 1) * s
        return [("H", x0 + a[0] * s + i, y) for i in range(s)]

    for a, b, o in walls:
        for e in wall_edges(a, b, o):
            m.kelp(e)
    # outer frame of the region (skipped on a full-board wrap maze)
    if not wrap:
        m.box(x0, y0, x0 + cw * s - 1, y0 + ch * s - 1)

    def cell_of(p):
        x, y = m.mt((x0 + p[0] * s, y0 + p[1] * s))
        return ((x - x0) // s, (y - y0) // s)

    parent = {}

    def find(c):
        while parent.setdefault(c, c) != c:
            parent[c] = parent.setdefault(parent[c], parent[c])
            c = parent[c]
        return c

    m.rng.shuffle(walls)
    spare = []
    for a, b, o in walls:
        ma, mb = cell_of(a), cell_of(b)
        if find(a) != find(b):
            parent[find(a)] = find(b)
            if find(ma) != find(mb):
                parent[find(ma)] = find(mb)
            for e in wall_edges(a, b, o):
                m.clear(e)
        else:
            spare.append((a, b, o))
    for a, b, o in spare[: int(len(spare) * loops)]:
        for e in wall_edges(a, b, o):
            m.clear(e)


def comb(m, x0, y0, n, depth, gap_end, gap_rest, opening="S"):
    """n 1-wide dead-end pockets side by side (columns x0..x0+n-1, rows y0..y0+depth-1).
    opening = side the pockets open to (S: open at the bottom, closed at the top; N: the reverse).
    The closed end tile gets gap_end, the rest gap_rest."""
    for i in range(n + 1):
        m.vwall(x0 + i, y0, y0 + depth - 1)
    closed_row = y0 if opening == "S" else y0 + depth
    m.hwall(x0, x0 + n - 1, closed_row)
    for i in range(n):
        for j in range(depth):
            y = y0 + j
            end = (j == 0) if opening == "S" else (j == depth - 1)
            m.tile(x0 + i, y, gap_end if end else gap_rest)


def hcomb(m, x0, y0, n, depth, gap_end, gap_rest, opening="E"):
    """horizontal 1-wide pockets (rows y0..y0+n-1, columns x0..x0+depth-1) opening to the east or west"""
    for i in range(n + 1):
        m.hwall(x0, x0 + depth - 1, y0 + i)
    closed_col = x0 if opening == "E" else x0 + depth
    m.vwall(closed_col, y0, y0 + n - 1)
    for i in range(n):
        for j in range(depth):
            end = (j == 0) if opening == "E" else (j == depth - 1)
            m.tile(x0 + j, y0 + i, gap_end if end else gap_rest)


def random_portals(m, count, pick, tries=4000):
    """add `count` random symmetric portal pairs; pick() returns a candidate edge"""
    made = 0
    for _ in range(tries):
        if made >= count:
            break
        a, b = pick(), pick()
        a, b = m.norm(a), m.norm(b)
        if a[0] != b[0] or a == b:
            continue
        if any(m.edges.get(e, (0, -1))[0] == 2 for e in (a, b, m.me(a), m.me(b))):
            continue
        try:
            m.portal(a, b)
        except ValueError:
            continue
        made += 1
    return made


def any_edge(m, x0=0, y0=0, x1=None, y1=None):
    x1 = m.w - 1 if x1 is None else x1
    y1 = m.h - 1 if y1 is None else y1
    return (m.rng.choice("HV"), m.rng.randint(x0, x1), m.rng.randint(y0, y1))


# ===================================================================================================
# lessons.  Each returns (Map, lesson text).


def vault_a():
    m = Map("vault_a", 32, 20, "y", bg=SLOW)
    m.scatter(0.15, SPARSE)
    m.box(2, 7, 7, 12)  # private room, west side (mirror: east side)
    m.fill(2, 7, 7, 12, FOUNT)
    m.fill(4, 9, 5, 10, HOT)
    # single portal door: the room's east wall edge at (8,9) <-> a lone edge out in team A's field
    m.portal(("V", 8, 9), ("V", 12, 3))
    m.dragon(Map.line(11, 15, "E", 4))
    m.dragon(Map.line(11, 17, "E", 4))
    m.dragon(Map.line(10, 5, "N", 4))
    return m, ("Private vault behind one portal door. The room is sealed by kelp; the only way in is to walk "
               "WEST through the lone portal edge at (12,3). Owning (and guarding) your vault wins the economy; "
               "the enemy's vault is a raid target.")


def vault_b():
    m = Map("vault_b", 40, 40, "xy", bg=SPARSE)
    m.scatter(0.5, NONE)
    # two vaults per team: one in the home corner, one far across the seam
    m.box(2, 2, 7, 6)
    m.fill(2, 2, 7, 6, FOUNT)
    m.fill(4, 4, 5, 4, HOT)
    m.box(26, 3, 31, 7)
    m.fill(26, 3, 31, 7, RICH)
    m.portal(("H", 4, 7), ("H", 10, 14))  # enter moving north through (10,14)'s north edge
    m.portal(("V", 26, 5), ("V", 15, 10))  # enter moving east through (15,10)'s west edge
    m.dragon(Map.line(10, 12, "E", 4))
    m.dragon(Map.line(14, 16, "N", 4))
    m.dragon(Map.line(6, 16, "E", 4))
    return m, ("Two vaults per team, each behind a one-edge portal door; the second vault sits in a far corner, "
               "so its door is near your spawn but its room is out towards the enemy. Scouting the door "
               "direction matters (direction is preserved through portals).")


def vault_c():
    m = Map("vault_c", 24, 48, "x", bg=NONE)
    m.scatter(0.25, SLOW)
    # the vault sits beside team A's spawn, but its only door opens in no-man's-land near the middle
    m.box(3, 3, 10, 8)
    m.fill(3, 3, 10, 8, FOUNT)
    m.fill(6, 5, 7, 6, HOT)
    m.portal(("H", 7, 3), ("H", 17, 21))  # moving south from (17,20) across this edge lands in the vault
    m.hwall(13, 21, 20)
    m.dragon(Map.line(15, 6, "S", 4))
    m.dragon(Map.line(18, 4, "S", 4))
    return m, ("Vault next to your spawn whose door is in the contested middle (just behind a kelp shelf). "
               "Lesson: the shortest path to your own food runs past the enemy; guard the door, not the room.")


def fountain_a():
    m = Map("fountain_a", 24, 24, "xy", bg=SPARSE)
    m.scatter(0.4, NONE)
    m.fill(10, 10, 13, 13, RICH)
    m.fill(11, 11, 12, 12, HOT)
    m.dragon(Map.line(3, 3, "E", 3))
    m.dragon(Map.line(3, 6, "S", 3))
    return m, ("Open central fountain (4 hot + 12 rich tiles) contested head-on by both teams; the rest is "
               "sparse. Lesson: contest vs yield, danger zones around a food cluster.")


def fountain_b():
    m = Map("fountain_b", 48, 32, "x", bg=SLOW)
    m.scatter(0.2, SPARSE)
    # fountain straddling the mirror line inside a kelp ring with four 1-wide gates
    m.box(20, 12, 27, 19)
    m.fill(20, 12, 27, 19, FOUNT)
    m.fill(22, 14, 25, 17, RICH)
    m.fill(23, 15, 24, 16, HOT)
    for e in (("H", 23, 12), ("V", 20, 15), ("V", 28, 15)):
        m.clear(e)
    m.dragon(Map.line(6, 4, "E", 4))
    m.dragon(Map.line(40, 5, "W", 4))
    m.dragon(Map.line(22, 5, "S", 4))
    return m, ("Walled fountain on the symmetry line with narrow gates (1-wide north/south, 2-wide on the "
               "sides). Lesson: fighting in chokepoints; a body parked in a gate is a wall for the enemy.")


def fountain_c():
    m = Map("fountain_c", 30, 30, "y", bg=SPARSE)
    m.scatter(0.3, NONE)
    m.fill(13, 5, 16, 8, FOUNT)
    m.fill(14, 6, 15, 7, HOT)
    m.fill(13, 20, 16, 23, FOUNT)
    m.fill(14, 21, 15, 22, HOT)
    m.hwall(11, 18, 14)
    m.hwall(11, 18, 16)
    m.dragon(Map.line(4, 7, "E", 4))
    m.dragon(Map.line(4, 21, "E", 4))
    m.dragon(Map.line(6, 14, "N", 3))
    return m, ("Two fountains on the mirror line (north and south, both equidistant). Lesson: split forces "
               "or concentrate; whoever holds both wins, holding one each is a race.")


def pockets_a():
    m = Map("pockets_a", 32, 16, "y", bg=SLOW)
    comb(m, 2, 0, 12, 5, HOT, FOUNT, "S")
    comb(m, 2, 11, 12, 5, HOT, FOUNT, "N")
    m.dragon(Map.line(6, 7, "E", 4))
    m.dragon(Map.line(6, 9, "E", 4))
    m.dragon(Map.line(10, 8, "E", 4))
    return m, ("Factory lesson: rows of 1-wide dead-end pockets, each with a hot [1,1] tile at the closed end. "
               "A dragon that enters can only leave by splitting (the tail becomes a new head facing out). "
               "Sit-and-split beats walking in and dying.")


def pockets_b():
    m = Map("pockets_b", 40, 24, "xy", bg=SPARSE)
    m.scatter(0.4, NONE)
    hcomb(m, 12, 3, 6, 6, HOT, FOUNT, "W")   # pockets open west, closed on the east side
    hcomb(m, 22, 3, 6, 6, HOT, FOUNT, "E")   # pockets open east
    comb(m, 4, 14, 5, 4, HOT, RICH, "S")
    m.dragon(Map.line(5, 5, "E", 5))
    m.dragon(Map.line(5, 8, "E", 3))
    return m, ("Factory lesson, rotated: banks of horizontal and vertical 1-wide pockets facing different "
               "ways. Lesson: pocket entry direction, and splitting a long dragon to farm several pockets.")


def maze_a():
    m = Map("maze_a", 32, 32, "xy", bg=SPARSE)
    maze(m, 2, 0, 0, 16, 16, loops=0.12, wrap=True)
    # clear spawn rooms (2x2 cells) so starting dragons fit
    for e in list(m.edges):
        o, x, y = e
        if 2 <= x <= 5 and 2 <= y <= 5 and not (o == "V" and x == 2) and not (o == "H" and y == 2):
            m.clear(e)
    m.dragon(Map.line(5, 3, "E", 4))
    m.dragon(Map.line(4, 5, "E", 3))
    for p in [(0, 15), (15, 0), (8, 8), (7, 24)]:
        m.tile(*p, FOUNT)
    return m, ("Wrapping maze of 2-wide corridors with a few loops and sparse pearls. Lesson: whole-map "
               "pathfinding, dead-end avoidance, and not getting cut off in a corridor.")


def maze_b():
    m = Map("maze_b", 48, 24, "y", bg=SLOW)
    maze(m, 3, 0, 0, 16, 8, loops=0.2, wrap=True)
    for e in list(m.edges):
        o, x, y = e
        if 3 <= x <= 8 and 9 <= y <= 14 and not (o == "V" and x == 3) and not (o == "H" and y == 9):
            m.clear(e)
    m.dragon(Map.line(7, 10, "E", 4))
    m.dragon(Map.line(7, 13, "E", 4))
    m.dragon(Map.line(5, 12, "W", 2))
    for p in [(1, 1), (22, 4), (13, 19), (10, 7)]:
        m.tile(*p, MID)
    return m, ("Maze of 3-wide passages (3x3 cells) with more loops and slow pearls everywhere. Lesson: patience; the pearl you can reach safely beats the one you see.")


def islands(m, iw, ih, nx, ny, pairs, rich):
    for i in range(nx):
        for j in range(ny):
            m.box(i * iw, j * ih, i * iw + iw - 1, j * ih + ih - 1)
    for (i, j) in rich:
        cx, cy = i * iw + iw // 2, j * ih + ih // 2
        m.fill(cx - 1, cy - 1, cx, cy, FOUNT)
        m.tile(cx, cy, HOT)

    def pick():
        if m.rng.random() < 0.5:
            return ("V", m.rng.randrange(nx) * iw, m.rng.randint(1, m.h - 2))
        return ("H", m.rng.randint(1, m.w - 2), m.rng.randrange(ny) * ih)

    # keep adding pairs until every tile is reachable from team A
    random_portals(m, pairs, pick)
    for _ in range(60):
        try:
            m.validate_reach_all()
            return
        except AssertionError:
            random_portals(m, 1, pick)
    raise RuntimeError(m.name + ": islands never connected")


def _reach_all(self):
    partner = self.partners()
    seen, todo = set(), [pts[0] for t, pts in self.dragons if t == 0]
    seen.update(todo)
    while todo:
        p = todo.pop()
        for d in OFF:
            q = self.step(p, d, partner)
            if q is not None and q not in seen:
                seen.add(q)
                todo.append(q)
    assert len(seen) == self.w * self.h


Map.validate_reach_all = _reach_all


def islands_a():
    m = Map("islands_a", 32, 32, "xy", bg=SPARSE)
    m.scatter(0.3, SLOW)
    m.dragon(Map.line(4, 3, "E", 4))
    m.dragon(Map.line(3, 6, "E", 3))
    islands(m, 8, 8, 4, 4, 6, rich=[(1, 2), (2, 0)])
    return m, ("4x4 grid of kelp-sealed 8x8 islands, joined only by portals set in the shared walls (each portal "
               "edge is two-sided, so one pair links four islands). Lesson: blind crossings and portal memory.")


def islands_b():
    m = Map("islands_b", 48, 30, "y", bg=SLOW)
    m.scatter(0.2, SPARSE)
    m.dragon(Map.line(5, 4, "E", 4))
    m.dragon(Map.line(5, 24, "E", 4))
    m.dragon(Map.line(3, 14, "S", 3))
    islands(m, 12, 10, 4, 3, 5, rich=[(1, 1), (0, 2)])
    return m, ("4x3 archipelago of 12x10 islands, sparse pearls, a rich island on each side. Lesson: route "
               "planning over a portal graph; which door leads home.")


def open_a():
    m = Map("open_a", 60, 60, "xy", bg=NONE)
    m.scatter(0.25, SPARSE)
    m.scatter(0.02, MID)
    m.dragon(Map.line(12, 12, "E", 4))
    return m, ("Huge empty 60x60 board, sparse pearls, one dragon each. King race: pure foraging efficiency, "
               "timer-aware routing, when to split into foragers and when to feed a champion.")


def open_b():
    m = Map("open_b", 64, 40, "y", bg=NONE)
    m.scatter(0.3, SPARSE)
    m.dragon(Map.line(10, 10, "E", 4))
    m.dragon(Map.line(10, 30, "E", 4))
    for _ in range(14):  # a few small solid kelp pillars, kept clear of the spawns
        x, y = m.rng.randint(2, 28), m.rng.randint(1, 37)
        x1, y1 = x + m.rng.randint(0, 1), y + m.rng.randint(0, 1)
        if 4 <= x1 and x <= 13 and (8 <= y1 and y <= 12 or 28 <= y1 and y <= 32):
            continue
        m.box(x, y, x1, y1)
        m.fill(x, y, x1, y1, NONE)
    return m, ("64x40 open field with pillars and sparse pearls, two dragons each far apart. King race with "
               "lots of room: expansion speed and late champion protection.")


def brawl_a():
    m = Map("brawl_a", 12, 12, "xy", bg=MID)
    m.fill(5, 5, 6, 6, RICH)
    m.dragon(Map.line(2, 2, "E", 3))
    m.dragon(Map.line(2, 5, "S", 3))
    m.dragon(Map.line(4, 8, "E", 3))
    return m, ("Tiny 12x12 torus, three length-3 dragons each. Pure swarm fight: ramming, danger zones, "
               "turn-order kills; there is nowhere to hide.")


def brawl_b():
    m = Map("brawl_b", 12, 12, "x", bg=FOUNT)
    m.box(2, 2, 3, 3)
    m.box(8, 2, 9, 3)
    m.fill(2, 2, 3, 3, NONE)
    m.fill(8, 2, 9, 3, NONE)
    m.tile(5, 0, HOT)
    m.tile(6, 0, HOT)
    m.dragon(Map.line(7, 4, "W", 4))
    m.dragon(Map.line(1, 2, "N", 3))
    return m, ("12x12 food-rich arena with kelp pillars (mirror top/bottom). Fast growth into instant "
               "combat; body-blocking around pillars.")


def famine_a():
    m = Map("famine_a", 24, 24, "xy", bg=NONE)
    for p in [(5, 11), (11, 5), (8, 18), (18, 8)]:
        m.tile(*p, LATE)
    m.dragon(Map.line(7, 4, "E", 6))
    m.dragon(Map.line(7, 7, "E", 6))
    return m, ("Starvation: 8 pearl tiles on [150,250] for the whole board, two length-6 dragons each. "
               "Growth is impossible; the game is decided by kills, corpses and elimination. Lesson: "
               "don't die, and harvest the enemy's drops.")


def famine_b():
    m = Map("famine_b", 40, 20, "y", bg=NONE)
    m.tile(19, 10, VLATE)
    m.tile(10, 3, VLATE)
    m.tile(5, 15, LATE)
    m.hwall(14, 25, 7)
    m.hwall(14, 25, 13)
    m.dragon(Map.line(12, 10, "E", 10))
    m.dragon(Map.line(8, 5, "E", 3))
    m.dragon(Map.line(8, 16, "E", 3))
    return m, ("Starvation with one length-10 flagship and two length-3 escorts per team; a handful of pearls "
               "(two spawn about once per game). Lesson: protect the flagship for the length tiebreak, use "
               "minnows to ram.")


def peel_a():
    m = Map("peel_a", 32, 32, "xy", bg=SPARSE)
    m.scatter(0.3, MID)
    m.dragon(Map.serp(3, 3, 5, 5))  # length-25 coil, head at its corner
    m.dragon(Map.line(11, 4, "E", 3))
    m.dragon(Map.line(4, 11, "S", 3))
    m.dragon(Map.line(11, 11, "E", 3))
    return m, ("One length-25 coil (5x5 serpentine) plus three length-3 dragons per team. Peeling lesson: "
               "a coiled dragon must unwind or split pieces off the outside; small ones can ram the big "
               "head while it is still tangled.")


def peel_b():
    m = Map("peel_b", 40, 24, "y", bg=NONE)
    m.scatter(0.3, SPARSE)
    m.fill(19, 10, 20, 13, FOUNT)
    m.dragon(Map.serp(4, 9, 6, 6))  # single length-36 coil, nothing else
    return m, ("A single length-36 coil per team and nothing else. You start with a king but no army: peel "
               "children off to forage, or keep the king whole for the tiebreak.")


def webs_a():
    m = Map("webs_a", 32, 32, "xy", bg=SLOW)
    m.scatter(0.2, SPARSE)
    m.scatter(0.03, FOUNT)
    for _ in range(10):
        x, y, n = m.rng.randint(0, 31), m.rng.randint(0, 15), m.rng.randint(2, 6)
        if m.rng.random() < 0.5:
            m.hwall(x, x + n - 1, y)
        else:
            m.vwall(x, y, y + n - 1)
    random_portals(m, 8, lambda: any_edge(m))
    m.dragon(Map.line(6, 4, "E", 4))
    m.dragon(Map.line(4, 9, "S", 4))
    return m, ("Asymmetric-looking web of 16 portal pairs and scattered kelp, 180-degree symmetric underneath. "
               "Lesson: blind crossings are dangerous; infer a portal's far end from symmetry and memory.")


def webs_b():
    m = Map("webs_b", 36, 24, "x", bg=SPARSE)
    m.scatter(0.3, NONE)
    m.scatter(0.04, RICH)
    for _ in range(8):
        x, y, n = m.rng.randint(0, 35), m.rng.randint(0, 11), m.rng.randint(2, 5)
        if m.rng.random() < 0.5:
            m.hwall(x, x + n - 1, y)
        else:
            m.vwall(x, y, y + n - 1)
    random_portals(m, 7, lambda: any_edge(m, 0, 0, 35, 10))
    m.dragon(Map.line(8, 3, "E", 4))
    m.dragon(Map.line(26, 5, "W", 4))
    return m, ("Portal web, mirror top/bottom: every portal's twin is on the enemy half. Lesson: a shortcut "
               "you find is also the enemy's shortcut into your half.")


def rush_a():
    m = Map("rush_a", 24, 16, "y", bg=SPARSE)
    m.fill(11, 6, 12, 9, RICH)
    m.dragon(Map.line(8, 5, "E", 4))
    m.dragon(Map.line(8, 8, "E", 4))
    m.dragon(Map.line(8, 11, "E", 4))
    return m, ("Enemy spawn 6 tiles away, heads facing each other over a small rich patch. Early-rush lesson: "
               "round-1 danger zones, turn-order (lower id moves first), and ramming vs retreating.")


def rush_b():
    m = Map("rush_b", 30, 30, "xy", bg=MID)
    m.fill(0, 0, 4, 29, FOUNT)  # far edges are rich; the middle, where you spawn, is thin
    m.fill(13, 13, 16, 16, NONE)
    m.dragon(Map.line(12, 14, "S", 4))
    m.dragon(Map.line(14, 12, "N", 3))
    return m, ("Both teams spawn in the centre, heads a few tiles apart, while the food is out at the board's "
               "edges. Lesson: disengage-and-farm vs fight-first when the enemy starts next to you.")


LESSONS = [vault_a, vault_b, vault_c, fountain_a, fountain_b, fountain_c, pockets_a, pockets_b, maze_a, maze_b,
           islands_a, islands_b, open_a, open_b, brawl_a, brawl_b, famine_a, famine_b, peel_a, peel_b,
           webs_a, webs_b, rush_a, rush_b]


def main():
    args = [a for a in sys.argv[1:] if a != "--list"]
    only_list = "--list" in sys.argv
    out = pathlib.Path(args[0]) if args else ROOT / "maps" / "lesson"
    if not only_list:
        out.mkdir(parents=True, exist_ok=True)
    for build in LESSONS:
        m, lesson = build()
        reach = m.validate()
        per = sum(1 for t, _ in m.dragons if t == 0)
        lens = [len(p) for t, p in m.dragons if t == 0]
        pairs = sum(1 for k, _ in m.edges.values() if k == 2) // 2
        info = f"{m.name:12s} {m.w}x{m.h} sym {m.sym:2s} dragons/team {per} {lens} portals {pairs} reach {reach:.0%}"
        if only_list:
            print(info, "--", lesson)
            continue
        path = out / f"{m.name}.map"
        if path.exists():
            print("exists, skipped:", path)
            continue
        path.write_text(m.text())
        print("wrote", info)


if __name__ == "__main__":
    main()
