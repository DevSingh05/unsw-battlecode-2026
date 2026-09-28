# 02 — Engine, protocol, toolkit and submission (technical reference)

Sources (read 2026-09-26): game.battlecode.au/docs/{quickstart, submitting, cli, execution-order, timeouts,
libraries, helper, protocol, protocol-upgrade, map-files, api}; the `unswbc` 1.1.0 wheel from PyPI (latest);
the public repo https://github.com/unswcpmsoc/unswbc (engine C++ source, examples, maps; repo VERSION says 1.0.2,
so it lags the wheel slightly). Raw copies: `scratchpad/raw-tech/` (`*.html`, `*.txt`, `whl/`, `repo/`).

---

## 1. Big picture

- Each **dragon is its own OS process** (in the judge: its own WebAssembly sandbox instance). There is no shared
  memory between your dragons; the only in-game channel between them is **sonar** (64-bit values).
- A split child is started as a **new process** with a fresh init block. A bot that crashes/times out is also
  restarted as a new process. So static/global state is lost on restart and never shared across dragons.
- The engine talks line-based plain text on stdin/stdout. A helper library parses it for you; you may edit or
  replace the helper.
- The engine source is public (`repo/engine/src/*.cc`, `engine/docs.md` has the full loop pseudocode). When the
  docs are ambiguous, read `protocol.cc`, `actions.cc`, `game.cc`, `sonar.cc`, `scoring.cc`.

## 2. Languages

| bot.toml `language` | Judge | Local `unswbc run` (no --sandbox) |
|---|---|---|
| `py` (also `python`) | CPython 3.13 + NumPy 2.5.3, nothing else | first of `python3`, `python`, `py -3` (override `UNSWBC_PYTHON`) |
| `c` | Clang 20, C17, wasi-libc, `-O2 -msimd128` | first of `cc`, `gcc`, `clang`, `cl` (override `CC`) |
| `c++` (also `cpp`, `cxx`) | Clang 20, C++20, libc++, `-O2 -msimd128` | first of `c++`, `g++`, `clang++`, `cl` (override `CXX`) |

- Also runnable locally in the sandbox: a precompiled `main.wasm` (name a dir holding it, or the file). The
  submission form/API only lists python, c, cpp though.
- No third-party libraries in any language: vendor pure-Python deps / C/C++ sources into the zip.
- The zip's own directory is on the C/C++ include path. `__DATE__`, `__TIME__`, `__TIMESTAMP__` fail the build.
- The Python entry point must be `main.py` (the sandbox compiles it to `main.pyc` and errors otherwise).
- The toolkit itself needs Python >= 3.11 regardless of bot language.

## 3. Project layout (`unswbc init <python|c|cpp> <dir>`)

```
maps/                 # shared by all your bots (created beside the project, never inside it)
mybot/
  bot.toml
  main.py + helper.py            (Python)
  main.c + helper.h + helper.c   (C)
  main.cpp + helper.hpp          (C++)
  .gitignore                     (ignores .unswbc-build/)
replays/              # `unswbc run` writes .replay files here by default
```

bot.toml as written by init:

```toml
[project]
language = "py"            # or "c", "c++"
include = [ "*.py" ]       # C: [ "*.c" ] (only translation units; headers are #included)
                           # C++: [ "*.cpp", "*.hpp", "*.cc", "*.hh", "*.c", "*.h" ]
```

`include` is a list of glob patterns; everything matched (plus bot.toml) is what gets zipped. Forgetting the
helper in `include` is the classic build failure.

## 4. CLI (`unswbc`)

Install: `uv tool install unswbc` (or `pip install unswbc`, or `python3 -m venv ~/.unswbc && ~/.unswbc/bin/pip install unswbc`).
Upgrade `uv tool upgrade unswbc` / `uv tool install unswbc@latest`; pin `uv tool install unswbc==X`.
The wheel is ~55 MB: it bundles the engine (as `unswbc_engine.wasm`, run through `wasmtime`), the judge's
clang + wasi sysroot, a sandboxed CPython 3.13 + NumPy, the maps and a VS Code replay viewer (.vsix).
It checks PyPI daily for updates (`UNSWBC_NO_UPDATE=1` silences). **An old toolkit = old engine rules**, keep it current.

| Command | What it does |
|---|---|
| `unswbc` | lists commands, checks for Python, C/C++ compilers, VS Code, replay viewer. `--build` also compiles a test program. |
| `unswbc init [lang] [dir] [-f]` | new project (lang c/cpp/python; prompts if omitted; dir defaults to cwd) + installs viewer + seeds `maps/` |
| `unswbc update [dir]` | replaces helper files with the toolkit's (old ones kept as `.bak`), refreshes bundled maps |
| `unswbc maps [dir]` | adds missing bundled maps (default `maps`), does not overwrite |
| `unswbc run <map> <botA> <botB>` | rebuilds both, plays one match, writes replay. Same dir twice = mirror match |
| `  -v` | verbose: every round, each dragon's stdout; with `--sandbox` also points + memory per turn |
| `  --sandbox` | run like the judge: CPU-point metering, 48 MB, log caps. **Only way to check the time budget locally** |
| `  --seed <n>` | fix the game seed (pearl spawns; with `--sandbox` also bots' RNG). Replays show the judge's seed |
| `  -o/--output/--replay PATH` | replay file or folder (default `replays/`); `--no-replay` |
| `  --no-logs --no-indicator --no-draw --no-debug` | strip debug channels from the replay |
| `unswbc vscode` | install replay viewer into VS Code / Cursor / VSCodium |
| `unswbc auth set bc_... / status / clear` | stores key in `~/.unswbc/keys.json` (one per server). `UNSWBC_KEY` env overrides |
| `unswbc submit [dir] [-n name] [-d desc]` | zips bot.toml + included files, POSTs to /api/v1/submissions. Default name `<folder>-YYYY-MM-DD-HHMM` |
| `unswbc log` | errors this machine hit (`~/.unswbc/log`), keys masked |
| `unswbc help <cmd>` | per-command options |

Other env: `UNSWBC_SERVER` (default https://game.battlecode.au), `UNSWBC_NO_VSCODE`, `NO_COLOR`.
Replays: open in VS Code (click the `.replay`) or the web `/visualiser`. The replay shows the full board and every
LOG line, which the bot itself cannot see.

## 5. Wire protocol (version 3.0.0)

Engine -> bot on stdin; bot -> engine on stdout. Blank lines may be skipped. C/C++ helpers strip text after `#`.

### 5.1 Init block (once per process)

```
ID 0            # dragon id, unique in game; also turn order
TEAM A          # A or B
MAP 11 11       # width height
UNIT_LIMIT 64   # max living dragons per team (default 64; a map may set it)
```

Sent at process start, i.e. also to split children and restarted bots — it does not mean "game start".

### 5.2 Round block (once per turn, in this order)

1. Header
```
ROUND 12          # engine counts rounds 0..499 (game.cc loop). Python Game() defaults round_num=1 before first update
DIR N             # head facing
LENGTH 5
UNIT_COUNT 2      # living dragons on my team
NUM_MSGS 1
90210             # NUM_MSGS lines, each an unsigned 64-bit sonar value
ECHOES 0 1 0 0 1  # kelp ally allyHead enemy enemyHead — ONLY after you've replied PROTOCOL 3
```
2. 49 tile lines, 7x7 window row by row; row 0 = 3 north of head, col 0 = 3 west. Each: `x y hasPearl pearlIn`
   (coords already wrapped; `pearlIn` = rounds until the tile next tries to spawn, -1 = never spawns). The centre
   line (index 24) is the head.
3. `DRAGON_BODIES n` then n lines `team id x y facing isHead` for every segment of every living dragon inside the
   window, own included. Head facing = heading; body segment facing points towards the head.
4. Horizontal edges: 8 lines of 7 tokens (north edge of each tile row, then south edge of last row).
5. Vertical edges: 7 lines of 8 tokens (west edge of each column, then east edge of last column).
   Edge tokens: `.` open, `w` kelp, integer = portal id (the other edge with the same id is the far end; ids can be
   multi-digit, so split on whitespace).

### 5.3 Reply (stdout, terminated by `ENDTURN`, then flush once)

| Command | Args | Effect |
|---|---|---|
| `MOVE` | string of N/E/S/W, e.g. `MOVE NNE` | action: move, one step per letter |
| `SPLIT` | int | action: split off that many rear segments |
| `SONAR` | `<N|E|S|W> <u64>` (proto 3) or `<u32>` (legacy: facing direction) | ping after the action |
| `PROTOCOL` | `3` | receive protocol-3 input from next turn (helpers send it every turn) |
| `INDICATOR` | text | label on dragon this turn (cut to 512 chars in judge) |
| `LOG` | text | message attached to this turn in the replay |
| `DOT` | `x y r g b` | replay drawing |
| `LINE` | `x1 y1 x2 y2 r g b` | replay drawing |
| `ENDTURN` | | stop reading |

- MOVE and SPLIT overwrite each other (single action slot). SONAR overwrites earlier SONAR in the same direction.
  INDICATOR overwrites INDICATOR. Last one wins; nothing applied until ENDTURN. LOG/DOT/LINE applied immediately.
- Unparseable lines are skipped (engine log entry) and don't change the action already set.
  Parser is strict: no trailing junk, `MOVE` only accepts N/E/S/W letters with no spaces in between.
- Engine parses only up to the last `\n` of the reply — always terminate lines.
- `\r` line endings tolerated.
- **Default action is suicide.** If you print no MOVE/SPLIT, your dragon dies ("no valid action").

### 5.4 End of game

Engine closes stdin; reading returns EOF and the process should exit. `ENDGAME` is recognised by helpers but the
current engine never sends it. Note: the Python helper's `update()` actually **raises EOFError** on EOF (the C++
helper throws `runtime_error`) rather than returning False, despite the docstring — harmless at game end, but
don't wrap it in something that retries.

### 5.5 Protocol 2 vs 3

Protocol 3 adds directed 64-bit sonar (`SONAR <dir> <u64>`, up to 4 per turn, one per direction) and the `ECHOES`
line. Both SONAR forms work at any version; the version only controls what the engine *sends you*. A protocol-2
dragon never receives values > 4294967295 (they're dropped, not queued) and gets no ECHOES. A split child inherits
its parent's protocol version. The version is stored per dragon in the engine (not per process), so a restarted bot
keeps it; but an original dragon's very first turn is protocol-2 input (no ECHOES) because PROTOCOL 3 only applies
from the next turn — helpers cope by checking whether the line starts with `ECHOES`.
`unswbc update` upgrades old helpers.

## 6. Execution order

Per round:
1. **Pearl tick**: every spawning tile's countdown -1, iterated top row to bottom, left to right. At 0: spawn a pearl
   if the tile is free (no pearl, no dragon), then draw a new countdown uniformly in [minGap, maxGap] either way.
   Mirrored tiles (SYMMETRY) share one countdown.
2. **Each living dragon takes a turn in ascending id order.** Dragons killed earlier this round are skipped. A child
   created by a split this round is appended and takes its turn later **this same round**.
3. Round ends. Game ends if a team has no dragons, or after round 500 (index 499).

One turn:
1. Sonar inbox + echo counts written to input, then emptied.
2. Defaults: action = suicide, sonars = none, indicator = none.
3. Read output lines until ENDTURN.
4. Apply action.
5. If still alive, cast sonars N, E, S, W.

Applying `MOVE d1 d2 ... dk`, per step:
1. If not the first step, must be able to pay: a length-2 dragon can't -> dies (no valid action).
2. Facing := step direction. Destination via the edge now faced: kelp kills; portal exits from the partner edge
   (heading unchanged); else adjacent tile, wrapped (the board is a **torus**).
3. Collision: own body first (tail included — tail hasn't moved yet, so moving onto your current tail kills you),
   then other dragons. Moving into another dragon's **head** kills both (the other dies first). Any other segment kills
   only the mover. Teammates count.
4. Head moves; pearl on destination is eaten; tail advances unless a pearl was eaten; if not the first step, one more
   tail segment is removed. So k pearl-less steps cost k-1 segments beyond normal motion; length L can take at most
   L-1 steps; each pearl eaten buys one.
   A death on any step discards remaining steps and this turn's sonar; steps already taken stand.
   Within a multi-move, step 2 is checked against the body as step 1 left it.

Split `n`: checked before anything moves: n >= 2, parent remaining >= 2, team below UNIT_LIMIT. Any failure kills the
parent (no valid action). Child = rear n segments reversed (child head = old tail; facing = from its 2nd segment to
its head), next id, own process, acts later this round.

Sonar: one ray per direction set, from the head; a ray **opposite** the dragon's facing leaves from the **tail** in the
direction the tail points away from the body. Travels through portals and wraps; stops at kelp or the first living
dragon (including the sender's own body); gives up after width+height steps. Value goes to the hit dragon's inbox,
read at the start of its next turn (higher id: this round; lower id: next round). The sender gets +1 echo count for the
kind it stopped on (kelp / ally / ally head / enemy / enemy head; nothing = no count).

Death sequence: record reason (HitWall, HitSelf, HitOtherBody, HitHeadToHead, NoValidAction); every second segment
(head, skip, next, ...) becomes a pearl, i.e. ceil(L/2) pearls, pearl countdowns unchanged; dragon removed; remaining
steps + sonar discarded. Head-on: other dragon's sequence first.

Turn ends at the first of: ENDTURN printed; bot blocks reading its next turn (output delivered in both cases); bot
exits; bot hits its limit (nothing delivered -> default suicide -> dragon dies, bot restarted as a new process).

Scoring (from `scoring.cc`): a team with zero dragons loses immediately (both eliminated same round = draw). At the
round limit, compare (longest dragon length, then total length) — higher wins, equal = draw.

## 7. Time / compute budget

Local `unswbc run` (no sandbox): no work limit, only 10 s wall per turn. **Says nothing about fitting the judge budget.**

Judge (WebAssembly sandbox, deterministic CPU points, not time):

| Limit | Value |
|---|---|
| Points per dragon per turn | **100,000,000** |
| Memory per dragon | **48 MB** |
| Threads | 1 (`thread_spawn` denied) |
| Backstop | 1 s CPU, 10 s wall (only for bots that evade the meter) |

- Over budget -> no reply -> dragon dies that turn. **First turn is not exempt**: interpreter + NumPy preloaded, but
  your imports and setup are charged. Spread precomputation over turns / do it lazily.
- Budget runs from reading the round to the flush in `end_turn()`. Work done after `end_turn()` but before the next
  read is charged to the next turn (no free "between turns" compute).
- Budget is per turn, not per tile: `MOVE NNE` commits 3 steps on one decision (paid in segments, not points).

Instruction prices (points): consts/locals/globals/select/nop/drop/block/loop/end = 1; comparisons = 1; int/float
arithmetic incl. mul, bitwise, shifts, sqrt, min/max = 1; conversions = 1; loads/stores = 2; `br`, `br_if`, `if`,
`return` = 2; everything else incl. all 128-bit SIMD = 2; div/rem = 3; `br_table` = 3; `call` = 4; indirect calls = 6;
`memory.copy/fill/init` = 10 + 1 per 8 bytes; table ops = 10; `memory.grow`/`table.grow` = 50.

Host calls: **stdout/stderr write = 2,500,000 + 4,000/byte**; stdin/file read = 6/byte; random bytes = 40,000 + 3/byte;
open file / path lookup = 40,000.

Reference costs: parsing one round in the Python helper ~10M points; flood fill of 32x32 ~19M in Python vs ~0.3M in
C++. So Python leaves ~90M/turn but is ~60x slower than C++ for search. SIMD runs as real SIMD at 2 points/instr
(4-16 lanes for ~the price of 2 scalar ops) — worth using in C/C++.

Output buffering gotchas:
- Each write syscall costs 2.5M. Helpers flush once per turn (`end_turn`). Never flush per line.
- The judge's stdout is a TTY (`isatty` true) so C stdio is line-buffered by default; C/C++ helpers call
  `setvbuf(stdout, NULL, _IOFBF, 1<<16)` in init. In C++: don't use `std::unitbuf`, **don't call
  `sync_with_stdio(false)`** (gives cout its own buffer that bypasses setvbuf -> per-line writes), don't
  `cin.tie(nullptr)` unless you flush at ENDTURN yourself; use `std::clog` not `std::cerr`.
- Python stdout is fully buffered already; `print(..., flush=True)` only in end_turn.
- Log caps in judge: 500,000 LOG/indicator/drawing lines and 16 MB text per team per game; excess dropped.
  Indicators cut to 512 chars. The judge (`judge serve`) runs with LOGs and parse complaints **off** — you only see
  logs from local runs. Battle `log` via API explains crashes/timeouts.

Clock and determinism:
- The clock reads 2026-01-01T00:00:00Z at zero spend and advances **1 ns per point** (+ requested sleeps). So
  `time.perf_counter()` / `std::chrono::steady_clock` measure points: 100M points = 0.1 s. `sleep` returns
  instantly. You can budget-check in-bot with perf_counter deltas (0.1 s = full budget).
- RNG: `os.urandom`, `random`, `std::random_device`, etc. draw from one stream per dragon per game (seeded by game seed).
  `PYTHONHASHSEED=0` so dict/set order and `hash()` are stable.
- **Gotcha**: starter bots do `random.seed(0)` / `srand(0)` / `mt19937(0)` -> every dragon gets the same sequence.
  Unseeded `rand()`, default `std::mt19937`, and `srand(time(NULL))` also give every dragon the same sequence. To
  differ, use the sandbox's entropy (`random.seed()` with no arg / `os.urandom`, `std::random_device`) or seed with the
  dragon id.
- Reproduce a judge game: `unswbc run map a b --sandbox --seed <seed from replay>`.

## 8. Sandbox environment / allowed libraries

Both languages: no network (sockets -> ENOTSUP), no fork/exec/spawn/threads, **read-only filesystem**; your files
are at `/bot` (cwd), no writable `/tmp`. Env: five `PYTHON*` vars + `TERM=dumb`; `getpid()` = 1, `cpu_count()` = 1.

Python: stdlib minus network/threads/compression/xml/sqlite etc. Present notable modules: `collections`, `heapq`,
`bisect`, `itertools`, `functools`, `array`, `struct`, `math`, `random`, `dataclasses`, `enum`, `typing`, `json`,
`pickle`, `marshal`, `ctypes`, `time`, `re`, `statistics`, `fractions`, `decimal`, `graphlib`, `copy`, `numpy`.
Not shipped (fail at import): socket/ssl/http/urllib/email..., `asyncio`, `multiprocessing`, `concurrent.futures`,
`zlib`, `bz2`, `lzma`, `gzip`, `xml.*`, `sqlite3`, `dbm`, `plistlib`, `mimetypes`, `importlib.metadata`, curses,
readline, tkinter, turtle, venv, distutils, test, idlelib.
Present but broken: `threading` (Thread.start raises; locks OK), `subprocess`/`os.fork` (ENOTSUP), `shelve`,
`pydoc` (won't import); `zipfile`/`tarfile` only read stored (uncompressed) members.
So: vendoring a precomputed table must be as .py/.npy/raw data, not compressed zips.

C/C++: every libc++ header except `<generator>`; POSIX headers compile but calls fail at runtime (`std::thread`
throws, `std::system` = -1).

## 9. Helper API (Python names; C++ same names in `unswbc::`, C uses `unswbc_*`)

Module: `init() -> (Controller, Game)`; `update(ct, game) -> bool`; `end_turn()` (prints `PROTOCOL 3` + `ENDTURN`, flush).

Template loop:
```python
import helper as unswbc
ct, game = unswbc.init()
while unswbc.update(ct, game):
    execute_turn()      # must call ct.make_move / make_moves / do_split, else suicide
    unswbc.end_turn()
```

- `Constants`: MAX_ROUNDS 500, VISION_RADIUS 3, VISION_SIZE 7, INITIAL_LENGTH 3, MIN_SIZE 2.
- `Direction` (NORTH/EAST/SOUTH/WEST, values "N"...): `value`, `get_direction_list()`, `get_offset()` (dx,dy; y down),
  `get_opposite()`, `get_left()` (anticlockwise), `get_right()`.
- `Team` (A/B): `get_enemy_team()`.
- `Position(x,y)` (hashable, (0,0) top-left, y down): `add_dir(d)` (wraps), `is_in_map()`, `is_in_vision()`.
- `Game`: `get_round_num()`, `get_map_size()`, `get_unit_limit()`.
- `Vision`: `get_tiles()` (49, lazily parsed), `get_tile(pos)` (None if outside window).
- `Tile`: `edges` (dict Direction->Edge), `get_edge(d)`, `get_dragon()` (DragonPart|None), `has_pearl()`,
  `get_pearl_time()` (-1 never), `get_position()`.
- `DragonPart`: `get_position()`, `get_id()`, `get_team()`, `get_dir()`, `is_head()`.
- `EdgeType`: EMPTY, KELP, PORTAL. `Edge`: `is_passable()` (only kelp blocks), `is_portal()`, `get_edge_type()`,
  `get_portal_id()` (-1 if not portal). Note: the portal's far end location is NOT given — you only see the id; you
  must remember/discover where the partner edge is (or read the map file offline).
- `SonarEchoes` namedtuple: kelp, ally, ally_head, enemy, enemy_head.
- `Controller`: `get_length()`, `get_unit_count()`, `get_head()`, `get_id()`, `get_team()`, `get_dir()`,
  `get_vision()`, `get_tiles()`, `get_tile(pos)`, `get_position()`, `make_move(d)`, `make_moves([d...])`
  (no validation; n steps cost n-1 segments), `can_split(n)` (n>=2, length-n>=2, unit_count<limit),
  `do_split(n)`, `output_log(*msg)`, `draw_indicator_dot(pos,r,g,b)`, `draw_indicator_line(a,b,r,g,b)`,
  `set_indicator_string(s)`, `get_sonar_messages() -> list[int]`, `get_sonar_echoes()`,
  `send_sonar(direction, value)` (u64) or legacy `send_sonar(value)` (u32, facing); returns False if out of range.

C equivalents: `unswbc_init(&ct,&game)`, `unswbc_update`, `unswbc_end_turn`, `unswbc_offset/opposite/left/right`,
`unswbc_enemy`, `unswbc_add`, `unswbc_in_map`, `unswbc_in_vision`, `unswbc_round`, `unswbc_unit_limit`,
`unswbc_position/length/unit_count/id/team/facing`, `unswbc_tile_count`, `unswbc_tile_at(ct,i)`,
`unswbc_tile(ct,pos)`, `unswbc_edge(tile,d)`, `unswbc_passable/is_portal/portal_id`, `unswbc_entity(tile)`,
`unswbc_has_pearl`, `unswbc_sonar(ct,&count)` (uint64_t*), `unswbc_sonar_echoes`, `unswbc_move`, `unswbc_moves`,
`unswbc_can_split`, `unswbc_split`, `unswbc_log`, `unswbc_dot`, `unswbc_line`, `unswbc_indicator`,
`unswbc_send_sonar_to(d,u64)`, `unswbc_send_sonar(u64)`. Structs expose fields directly (`tile->pearl_time`,
`edge->present`, etc.).

Helper gotchas:
- On maps narrower/shorter than 7 the window wraps and a tile appears more than once; `get_tile(pos)` maps to one
  slot. All bundled maps are >= 11 wide, so rarely matters.
- Python `update()` raises EOFError at game end instead of returning False (see 5.4).
- Old projects keep their old helper; after upgrading the toolkit run `unswbc update mybot`.

## 10. Map file format (`.map`)

```
MAP 11 11            # required, first
MAP_NAME name        # optional
SYMMETRY xy          # optional: x | y | xy; mirrored tiles share one pearl countdown
UNIT_LIMIT 64        # optional (undocumented on the site but parsed by config.cc)
TILE_COUNT 81
TILE x y minGap maxGap     # countdown drawn uniformly [minGap,maxGap]; maxGap 0 = never spawns
EDGE_COUNT 44
EDGE index kind portalId   # kind 0 open, 1 kelp (portalId -1), 2 portal (exactly 2 edges share id, same orientation)
DRAGON_COUNT 2
DRAGON team segCount x y x y ...  # team 0=A 1=B; head first; adjacent, min length 2; ids assigned in file order = turn order
END                  # optional terminator (parsed)
```
Edge indexing: rows of horizontal edges (a tile row's north side) alternate with rows of vertical edges (its west
side); each row is width+1 long; index < (2*height+1)*(width+1). Only listed edges are non-default. Use the
`/map-editor` in practice.

Bundled maps (wheel 1.1.0): arena 11x11 (2 dragons), Colosseum 16x16, default_small 16x16, default 32x32 (8),
devil 32x16, dilemma 32x16, trophy 25x25, queen_of_spades 25x35, stronghold 48x24, trauma 48x24, autarky 54x18 (12),
schooltime 60x40, big_empty 64x64. Repo also has help, small, queen_of_spades_but_she_ages. The authoritative
list of ranked maps is `GET /api/v1/maps` (needs key).

## 11. Submission

- Via website `/submissions` (zip upload) or `unswbc submit mybot`. Must be on a team first.
- Zip: `bot.toml` at the **top level**, all files in `include` (helper included). **4 MB max. 12 uploads/hour.**
- States: Processing -> Ready / Active / Build failed. A new version goes Active as soon as it builds, replacing the
  previous one (so a broken-but-compiling upload immediately plays ranked!). Any Ready build can be re-activated,
  unlimited times.
- Build failure checklist: bot.toml at zip root; language on form matches bot.toml; include lists every file.
  Unzip into an empty dir and `unswbc run` it; if that fails, the server fails too.
- Language names differ: bot.toml uses `py` / `c` / `c++`; the API/form field uses `python` / `c` / `cpp`
  (the CLI maps it for you).

## 12. Public API (JSON)

Base `https://game.battlecode.au/api/v1`, header `Authorization: Bearer bc_...` (**all** endpoints need a key,
including reads — verified: unauthenticated GET /maps, /queue, /ratings -> 401). One key per member, shown once;
acts as that member. Rate limits: 120 req/min per key; 30/min for `/leaderboard` and `/ratings`; 429 + Retry-After.
Errors: `{"error": "..."}`; unknown paths 404 JSON.

- `GET /me`, `GET /team`
- `GET /submissions`; `POST /submissions` (multipart: name, language[python|c|cpp], description, zip);
  `GET /submissions/:id` (with build log); `GET /submissions/:id/download`; `POST /submissions/:id/activate`
- `GET /battles?limit=50` (max 200); `POST /battles` JSON `{teamId, ranked, mapIds?}` -> `{"ids":[...]}`; ranked =
  5-game series; one pending battle per opponent, 60 games/hour; `GET /battles/:id` (games, queue position, and for
  your own battles a `log` explaining crash/timeout); `GET /battles/:id/replay` -> redirect to signed URL (follow with
  `curl -L`; **do not forward the Authorization header** to the signed host — Python `urllib` does and gets refused).
- `GET /leaderboard`, `GET /ratings`, `GET /teams`, `GET /teams/:id`, `GET /tournaments`, `GET /tournaments/:id`,
  `GET /maps` (maps in play with their text), `GET /queue` (judge capacity/queue length).

Useful automation: pull `/maps` text into `maps/` so local tests use the real ranked maps; pull replays + `log` of
losses for analysis.

## 13. Local dev workflow

```sh
uv tool install unswbc
unswbc init python mybot                     # or cpp / c
unswbc run maps/arena.map mybot mybot        # quick logic test, replay in replays/
unswbc run maps/default.map mybot oldbot --sandbox -v   # judge-accurate points/memory per turn
unswbc run maps/X.map a b --sandbox --seed 0x...        # reproduce a judge game exactly
unswbc auth set bc_...; unswbc submit mybot -n v3 -d "what changed"
```
Keep old versions as separate project dirs to use as sparring partners. Test every bundled map, especially large
ones (64x64, 60x40) where search costs more. The repo's `examples/` has extra test bots (dummy, suicidal, fuzz,
stress, murder, cppbot).

## 14. Gotchas / ambiguities (summary)

1. Default action is **suicide**: every turn must emit a legal MOVE or SPLIT; any exception/timeout = death + restart.
2. 100M points/turn including the first turn's imports; Python round parsing alone ~10M. Local runs without
   `--sandbox` hide overruns entirely.
3. Every stdout write = 2.5M points. One flush per turn. C++: no `sync_with_stdio(false)`, no `unitbuf`, use `clog`.
4. Each dragon is a separate process; no shared memory; split children and restarts start from scratch (init block).
   Any "team strategy" state must be re-derivable or communicated via sonar.
5. Moving onto your own current tail tile is fatal (tail hasn't moved at check time). Multi-step moves cost segments
   and a length-2 dragon can only ever single-step.
6. Head-to-head kills both, even teammates.
7. Turn order is id order; lower-id dragons' sonar to higher ids arrives the same round, the reverse arrives next round.
8. Fixed seeds in starters make all dragons draw identical random sequences.
9. A starting dragon's first turn gets protocol-2 input (no ECHOES line); split children inherit protocol 3.
10. Rounds are 0-indexed in the engine (ROUND 0..499); docs say "round 500" for the last one.
11. Portal ids are visible but not the partner location.
12. New submissions auto-activate on successful build — test in sandbox before uploading.
13. `UNIT_LIMIT` and `END` map directives exist in the engine but aren't documented on the site.
14. Toolkit version matters: it embeds the engine; the repo (1.0.2) lags PyPI (1.1.0).
