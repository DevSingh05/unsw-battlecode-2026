# Our bot (v2), 26 Sep 2026

C++20, `bot/`. Submission zip: `bot-submission.zip` (140 KB). Snapshots: `variants/v1`, `variants/v2`.

## How it works
- **Built-in maps**: `tools/genmaps.py` compiles every known map (all 10 ranked + 10 others) into `bot/maps_data.hpp`: walls, portal destinations, pearl spawn gaps, starting dragons. A dragon recognises the map from its size, id and start tile (or from the edges it sees, for split children), and double-checks each turn against its view. Unknown map → learns edges as it goes (much weaker).
- **Memory**: each dragon remembers pearls and spawn countdowns it has seen (mirrored tiles share countdowns), and tracks its own full body even outside its view (portals).
- **Moves**: every safe direction is scored on:
  - pearl value (time-aware BFS that knows when each body segment will move out of the way);
  - room (tiles we reach before any other head);
  - a 12-move look-ahead that simulates our own body so we don't walk into dead ends;
  - enemy heads that could ram us;
  - not boxing in teammates, and boxing in enemies.
- **Splitting**: 2+2 at length 4 until round 300. A trapped dragon reverse-splits so the bulk escapes backwards.
- **Combat**: small dragons (≤5) ram enemy heads at distance 1–2, including 2-step sprint rams.
- **Endgame**: from round 250 our longest dragon (≥8) broadcasts its position by sonar (checksummed, relayed up to 3 hops). From round 330, smaller dragons walk to 2 tiles ahead of the king and kill themselves so it eats their pearls. 4 reserves are kept alive.
- **Compute**: 5–9M of the 100M points per turn.

## Test tools
- `python3 tools/arena.py bot variants/v1 --seeds 3`: parallel games on the 10 ranked maps, sides swapped. Variants via flags, e.g. `bot:-DSPLIT_LEN=6`.
- `tools/deaths.py replay...`: death causes and dragon counts over time.
- `tools/showmap.py maps/x.map`: ASCII map.
- Debug: `BOTDBG=<dir>` env var (local only) writes each dragon's view and move scores.

## Self-play results (60 games each)
- Split at 4 beat split at 6 (49-11); split at 6 beat split at 14 (58-2).
- Feeding the king vs not: 35-25, and 6/6 on Portals.
- v2 vs v1: 38-22.
- Look-ahead cut self-collisions by about 20%.

## Next ideas
- Hot-tile "factories" (1-wide corridors with pearl every round).
- Better unknown-map mode (infer symmetry, portals).
- Tune feeding timing and king safety against real opponents' rams.

## v3 (submitted 27 Sep 2026, server version #2)
Param sweep of 16 single changes vs v2 (40 games each), then combos (60 games each).
- Winners: SPLIT_STOP_ROUND 300→350 (26-14), RAM_MAX_OWN_LEN 5→3, AREA_WEIGHT 120→60.
- Combined v3 vs v2: 38-22 (63%).
- Clearly worse: PEARL_GAMMA 0.9 (10-30), SPLIT_STOP_ROUND 250 (15-25).
- About neutral: FEED_START 280/380, FEED_AHEAD 1/3, FEED_RESERVE 2/8, KING_MIN_LEN 6, KING_THREAT_REACH 2, SURVIVE_DEPTH 8.

## v4 (27 Sep, local; from the first ladder loss)
Ladder after v2/v3: 12-1. The one loss was Queen of Spades vs EternalWisdom (eliminated).
- About 9 pairs of OUR dragons died head-on to each other, all through portals. Vision doesn't pass through portals, so a dragon stepping through can't see an ally standing on the exit tile.
- Portal penalties (blind crossing, exit-tile, no split on an exit) were tested and all hurt overall: Portals and Slithery 1/10. Left OFF (PORTAL_* params = 0). A real fix needs sonar coordination.
- Real bug fixed: look-alike maps (Trauma/Stronghold share size and starts; QoS/"QoS But She Ages" share walls but not pearl gaps). Live v3 dragons on Trauma started out believing Stronghold's walls. Now ranked maps are tried first, and visible pearl countdowns reject wrong variants.
- v4 vs v3 self-play: 50-50 over 100 games (expected: the fix only matters against teams without the bug).
