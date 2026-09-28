# 04 - Tools (visualiser, map editor) and frontend/engine internals

Research date: 2026-09-26. Read-only (GETs only; no login, no POSTs).
Game internal name: **"battledragon"**: multi-snake ("dragons") on a toroidal grid with kelp walls on edges, portals, and pearls.

## TL;DR
- **Engine source is public**: https://github.com/unswcpmsoc/unswbc ("Public facing repo for UNSW Battlecode 2026"), with `engine/` (C++, ~1.8k lines), `engine/replay.capnp`, `maps/`, `examples/` (cppbot, dummy, murder, suicidal, stress, fuzz...), `pythoncli/` and `packages/visualiser`. A shallow clone is in the scratchpad; clone it into the project if you want it.
- **Local runner**: `pip install unswbc` / `uv tool install unswbc` (v1.1.0, py>=3.11, 55 MB wheel). It ships the **judge engine as `unswbc_engine.wasm`** (run via wasmtime), metered CPython wasm, clang wasm, starter templates (python/c/cpp), 13 bundled maps and a VS Code replay viewer (`replay-viewer.vsix`). `unswbc run maps/arena.map botA botB [--sandbox] [-v]` writes a replay. Use `--sandbox` to get judge-like CPU metering.
- **All 20 maps that have ever been in play are saved** to `notes/maps/` (taken from public replays). Every one of the 13 maps bundled in the wheel is byte-identical to its live version. **Portals** (id 20) and **Slithery Fight** (id 21) are live maps that the toolkit **does not** ship. We only have them because we pulled them out of replays.
- **Replays of any match are public and need no auth**: `GET /api/matches/:id/replay` returns 302 to a signed R2 URL. The file is gzip → **packed Cap'n Proto** `Replay`. A decoder is at `notes/tools/replay_decode.py`.

## /visualiser
- A SvelteKit page (node 65). "Open a replay: choose a .replay file from a local match". With `?match=<id>` it streams `GET /api/matches/<id>/replay` (404 = no replay, 409 = match not finished) and shows a live chat (`/api/matches/:id/messages`, SSE at `/messages/stream`, POST to send, which needs sign-in).
- It is a playback tool only. **There is no client-side game engine or simulator.** State is rebuilt by applying replay events to the initial map (`Match.roundAt(n)` caches a state per round).
- Playback granularity: `round`, `turn` or `event`. Timeline markers: death, split, engine, bot. Settings live in localStorage `battledragon-visualiser:settings` (skins, speed=5, and so on).
- It supports replay formatVersion ≤ 2 (current = 2). v<2 stored the sonar value as u32; v2 uses u64 `value64`.
- Win summary logic (mirrors `engine/src/scoring.cc`):
  - Elimination: a team with 0 dragons loses. Both eliminated is a draw.
  - At round limit (500), compare `(longestDragon, totalLength)` lexicographically. Equal on both is a draw.

## /map-editor
- Draw a map and export a `.map`. Defaults: 16x16, symmetry `xy`, name `new_map_MMDD`, 4 dragons per team of length 4 (rows 0-3, x 0-3, mirrored).
- The pearl brush defaults to `{min 1, max 2n-1}`.
- Size is clamped to 10..64. Imports above 64x64 are rejected.
- Brushes: kelp (edges), portal (pairs of edges with the same orientation; if one end is on the symmetry axis the other must be too), pearl (per-tile min/max respawn gap), dragon (click adjacent cells, min length 2, auto-mirrored to the other team, must not cross its mirror).
- It checks "Kelp would cut a dragon in two", meaning a kelp edge between consecutive body cells.
- Export uses canonical edges only: the wrap-duplicate east/south rows are omitted.

## .map format (docs /docs/map-files + parser in bundle + engine config.cc)
```
MAP w h                 # required, first. Engine: 7 (VISION_SIZE) <= side <= 256; editor/docs: 10..64
UNIT_LIMIT n            # UNDOCUMENTED in docs; default 64 (DEFAULT_UNIT_LIMIT) = max alive dragons per team
SYMMETRY x|y|xy         # x = mirror top/bottom (y->h-1-y), y = mirror left/right, xy = 180deg rotation
MAP_NAME text
ROUNDS ...              # accepted & ignored by the visualiser parser (legacy)
TILE_COUNT n / TILE x y minGap maxGap     # pearl respawn gap uniform [min,max]; maxGap 0 = never spawns
EDGE_COUNT n / EDGE idx kind portalId     # kind 0 open, 1 kelp (id -1), 2 portal (exactly 2 edges share id)
DRAGON_COUNT n / DRAGON team len x y x y ...   # team 0=A 1=B, head first; ids assigned in file order = turn order
END                     # optional terminator
```
Edge index: `row = idx // (w+1)`, `col = idx % (w+1)`.
- Even rows are horizontal edges: the N side of tile `(col, row/2)`. `col == w` is a padding slot, which is invalid.
- Odd rows are vertical edges: the W side of tile `(col, (row-1)/2)`.
- Edges on the east/south border alias the west/north ones (torus).

Initial tiles are all empty. Pearls come only from `TILE` countdowns (the first countdowns are emitted before round 1). Mirrored tiles share one countdown.

## Replay format (packed capnp; schema = engine/replay.capnp)
`Replay { map:Text (full .map text!), botA, botB, events:List(Event), result:GameResult, formatVersion:u32, seed:union{none|value u64} }`

Event union (ordinal: fields):
- 0 roundStart{round}
- 1 turnStart{id}
- 2 pearlCountdown{tile, countdown}
- 3 tileChange{tile, hasPearl}
- 4 dragonAction{id, action: move[List Dir] | split[i32 childSegs] | suicide, instructions{count u64, exceeded}, tle}
- 5 engineLog{id, text}
- 6 dragonLog
- 7 dragonIndicator
- 8 debugDraw{shape line/dot, from, to, rgb}
- 9 dragonUpdate{id, facing, head, tail}
- 10 dragonSplit{parentId, childId, team, childFacing, parentBody, childBody}
- 11 dragonDeath{id, reason: HitWall/HitSelf/HitOtherBody/HitHeadToHead/NoValidAction}
- 12 sonarPing{senderId, direction, value(u32 / value64 u64), origin, end, hitId?, hitKind: unknown/empty/kelp/ally/allyHead/enemy/enemyHead}

GameResult: `terminated`, `endReason` (teamEliminated/roundLimit), `winner` (A/B or none), per-team `{dragonCount, longestDragon, totalLength}`.

Direction enum: N=0 E=1 S=2 W=3. Team: A=0 B=1.

Observations from live ranked replays:
- `instructions` is absent.
- `botA`/`botB` are empty strings.
- `seed` is present.
- Opponents' **dragonLog/indicator text is stripped** from the public replays I checked.
- **sonarPing events (including the 64-bit message value) are present**. You can see opponents' sonar traffic and target squares.

## Engine constants and rules seen in source (engine/include/engine/types.h, src/*.cc)
- PROTOCOL_VERSION "3.0.0". VISION_SIZE 7 (radius 3). MIN_DRAGON_LENGTH 2. DEFAULT_UNIT_LIMIT 64. MAX_ROUNDS 500. MAX_MAP_SIDE 256.
- MAX_TEAM_NOTES 500k. MAX_TEAM_TEXT 16 MiB. MAX_INDICATOR 512 chars. PEARL_RNG_SEED 0x5eed5eed (mt19937).
- **Move**: a list of steps.
  - Each step after the first costs a tail segment. If length ≤ 2 when a paid step is due, the dragon **dies (NoValidAction)**.
  - Stepping onto a pearl grows the dragon: the tail is not popped.
  - Kelp edge → HitWall. Own body (including the current tail cell) → HitSelf.
  - Entering another dragon's head kills **both** (HitHeadToHead). Entering another dragon's body kills only the mover.
- **Split k**: needs `2 ≤ k ≤ len-2` and alive team units < unit limit, or the dragon **dies**. The child is the last k segments reversed (old tail becomes child head) and gets a new id at the end of the turn order.
- **Death** drops a pearl on every other body segment (indices 0,2,4,...).
- **Sonar**: casts from the head. A ping cast opposite to facing is cast from the tail. It travels up to w+h steps and stops at kelp (kind kelp) or the first dragon. The hit dragon gets `value` in its sonar inbox (the message channel), with kind ally/allyHead/enemy/enemyHead.
- **Pearls**: each tile+mirror pair shares a countdown and decrements every round. At 0 it tries to spawn (fails silently if the tile is occupied or already has a pearl) and redraws the gap.

## Maps (notes/maps/, from public replays; id = site map id)
| id | name | size | sym | dragons | bundled in wheel | in recent rotation* |
|---|---|---|---|---|---|---|
|2|Arena|11x11|xy|2|arena.map|-|
|1|Colosseum|16x16|xy|2|Colosseum.map|-|
|5|Default Small|16x16|xy|4|default_small.map|-|
|4|Default|32x32|xy|8|default.map|yes|
|3|Big Empty|64x64|xy|6|big_empty.map|-|
|13|Devil|32x16|y|6|devil.map|yes|
|17|Prisoners Dilemma|32x16|xy|6|dilemma.map|yes|
|20|**Portals**|32x16|xy|6|**no**|yes|
|7|Queen Of Spades|25x35|xy|4|queen_of_spades.map|yes|
|9|Schooltime|60x40|y|6|schooltime.map|yes|
|21|**Slithery Fight**|63x27|xy|14|**no**|yes|
|14|Stronghold|48x24|xy|4|stronghold.map|-|
|15|Trauma|48x24|xy|4|trauma.map|yes|
|11|Trophy|25x25|y|4|trophy.map|yes (most common)|
|19|Autarky|54x18|xy|12|autarky.map|yes|
|18|Autarky (deprecated)|54x18|xy|8|-|old|
|6|Help|64x64|none|12|repo only|old|
|8|Queen Of Spades But She Ages|25x35|xy|4|repo only|old|
|10|Small|16x8|none|6|repo only|old|
|16|stronghold|48x24|xy|4|-|old|

\*From the last 150 public games: Trophy 66, Devil 21, Slithery Fight 12, Queen Of Spades 11, Schooltime 10, Portals 10, Prisoners Dilemma 7, Trauma 5, Default 5, Autarky 3. Roughly 2/3 of those were ranked.

Also saved: `notes/maps/docs-demo.replay` (the docs overview demo, format v0, Default Small).

## Endpoints the frontend uses / documents
Public, no auth (verified with GET):
- `GET /api/matches/:id/replay` → 302 to a signed R2 URL (`replays-prod...r2.cloudflarestorage.com/replays/<id>.replay.public`). The body is gzip. 404 = none, 409 = unfinished.
- `GET /replays/docs-demo.replay` returns a static demo replay (not gzipped).
- `GET /games/__data.json?page=N&maps=<id,...>` is the SvelteKit data for the Games list (devalue-encoded). It has 10 per page, `total` (~333k), each match `{id, ranked, status, winner, hasReplay, mapName, a/b {id, name, elo}}`, and the full `maps` list `{id, name}`. Other pages expose `__data.json` in the same way (`/leaderboard`, `/battles`, `/teams/:id`, and so on).
- `/_app/version.json` (SvelteKit version poll).

Chat:
- `GET /api/matches/:id/messages`
- `GET /api/matches/:id/messages/stream` (SSE)
- `POST /api/matches/:id/messages` (auth)

Auth: better-auth at `/api/auth/*` (e.g. `POST /api/auth/get-session`).

SvelteKit form actions (all POST, auth):
- `/teams/:id?/challenge`, `/teams/:id?/star`
- `/submissions?/setActive`
- `/team?/revokeKey`, `?/uploadImage`, `?/removeImage`, `?/respondRequest`, `?/withdrawOffer`
- `/teams/:id/availability` (fetch)
- admin `?/requeue`, `?/cancel`, and so on

Public REST API `https://game.battlecode.au/api/v1` (Bearer `bc_...` key per member; 120 req/min, 30/min for leaderboard/ratings; unauthenticated calls give 401):
- `GET /me`
- `GET /team`
- `GET|POST /submissions` (multipart: name, language python|c|cpp, description, zip ≤4 MB; 12 uploads/hour)
- `GET /submissions/:id`
- `GET /submissions/:id/download`
- `POST /submissions/:id/activate`
- `GET /battles?limit=50` (max 200)
- `POST /battles {teamId, ranked, mapIds?}` (ranked = 5-game series; 1 pending per opponent; 60 games/hour)
- `GET /battles/:id` (includes crash/timeout `log` for your own battles)
- `GET /battles/:id/replay` (redirect; do not forward the auth header)
- `GET /leaderboard`
- `GET /ratings`
- `GET /teams`
- `GET /teams/:id`
- `GET /tournaments[/:id]`
- **`GET /maps` (maps in play, with full text)**
- `GET /queue`

## Mismatches / gotchas vs docs
1. `UNIT_LIMIT` directive exists (default 64) but is undocumented in /docs/map-files. Splitting at the limit **kills** the dragon.
2. Map size: the docs say 10..64. The engine accepts 7..256, and the live Arena map is 11x11.
3. /docs/map-info says "edges along the east and **north** border are equivalent to their west and north counterparts". It should read "east and **south**".
4. The visualiser tile enum has `Wall`, but no map directive can create wall tiles. Only kelp edges block movement (the death reason is still named HitWall).
5. Portals and Slithery Fight are in live rotation but are not bundled with `unswbc` 1.1.0 or the repo's `maps/`. Use `notes/maps/Portals__id20.map` and `Slithery_Fight__id21.map`.
6. Public replays leak opponents' full action streams and sonar message values. Their logs are stripped.

## Useful for local bot development
- Install `unswbc`, run `unswbc init python mybot`, then `unswbc run <map> mybot other`. Copy our 2 extra maps into `maps/`.
- Mine top teams' public replays (`/games/__data.json` → `/api/matches/:id/replay`) and decode them with `notes/tools/replay_decode.py` (`python3 replay_decode.py file.replay`; it handles gzip). This gives opponent openings, split timing, sonar protocols, and death stats.
- In one Default game, deaths were mostly HitHeadToHead and NoValidAction. Almost all moves were single-step.
