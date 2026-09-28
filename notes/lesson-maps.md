# Lesson maps (maps/lesson/)

24 hand-designed-style maps written by `tools/lessonmaps.py`, built to prepare for the devs' later
"each map teaches a lesson" / adversarial / autarky-dilemma-style macro maps (notes/12 section 2) and the
unseen Sprint/qualifier pool. Each map isolates one strategic idea; most lessons come in 2-3 variants
that change size and symmetry.

- Regenerate: `python3 tools/lessonmaps.py [OUTDIR]` (default `maps/lesson`; existing files are skipped,
  never overwritten; output is deterministic, each map is seeded from its name).
  `python3 tools/lessonmaps.py --list` prints stats + lesson without writing anything.
- Preview: `replays/lesson_maps.html` (`python3 tools/maps_html.py replays/lesson_maps.html maps/lesson/*.map`),
  or `python3 tools/showmap.py maps/lesson/<name>.map` for ASCII.
- Construction: every tile, kelp edge, portal pair and dragon goes through a mirror-aware builder, so the
  engine checks in `engine/src/config.cc` hold by construction: mirrored tiles share gaps, portal pairs have one
  orientation (and a mirror pair, unless the pair is its own mirror), no overlapping dragons. `validate()` also
  rejects kelp/portal edges between consecutive dragon segments, boxed-in heads, and pearl tiles unreachable from
  team A (walking + portals). Dragons are listed A, B, A, B... (B is A's mirror), as on the ranked maps.
- Engine check (28 Sep): every map ran to completion with
  `unswbc run maps/lesson/<m>.map variants/v15 variants/v14 --seed 1 --no-replay`, with no map error.
- Pearl bands follow the ranked maps: HOT [1,1], RICH [1,5], FOUNT [1,20], MID [1,100], SPARSE [20,200],
  SLOW [1,600], LATE [150,250], VLATE [480,490].

| map | size | sym | dragons/team | lesson |
|---|---|---|---|---|
| vault_a | 32x20 | y | 3x4 | **Private vault behind one portal door.** Kelp-sealed [1,20] room with 4 hot tiles. The only entry is walking west through a lone portal edge at (12,3), since direction is preserved through the portal. Own and guard your vault; the enemy's vault is a raid target. |
| vault_b | 40x40 | xy | 3x4 | Two vaults per team, each behind a one-edge door. The second vault is in a far corner, so its door is near your spawn but the room is out towards the enemy. Scouting through doors, and knowing which heading enters. |
| vault_c | 24x48 | x | 2x4 | The vault sits beside your spawn, but its door is in the contested middle behind a kelp shelf, 6 rows from the enemy's door. Guard the door, not the room. |
| fountain_a | 24x24 | xy | 2x3 | Open central fountain (4 hot + 12 rich) on a sparse board. Contest vs yield, and danger zones around a food cluster. |
| fountain_b | 48x32 | x | 3x4 | Fountain on the symmetry line inside a kelp ring with narrow gates (1-wide N/S, 2-wide sides). Chokepoint fighting; a body parked in a gate walls it off. |
| fountain_c | 30x30 | y | 3 (4,4,3) | Two fountains on the mirror line, north and south, equidistant from both teams, with kelp bars through the middle. Split forces or concentrate. |
| pockets_a | 32x16 | y | 3x4 | **Factory.** 48 one-wide dead-end pockets (devil-style), each with a hot [1,1] tile at the closed end and [1,20] inside. You can only get out by splitting (the tail becomes a new head facing out). |
| pockets_b | 40x24 | xy | 2 (5,3) | Factory, rotated: horizontal pocket banks opening east/west plus vertical banks. Pocket entry direction; split one long dragon to farm several pockets. |
| maze_a | 32x32 | xy | 2 (4,3) | Wrapping symmetric maze (2x2 cells, thin kelp walls, 12% extra loops), sparse pearls, cleared 4x4 spawn rooms. Whole-map pathfinding, dead ends, getting cut off in corridors. |
| maze_b | 48x24 | y | 3 (4,4,2) | Maze of 3-wide passages with 20% loops and slow pearls everywhere. Patience: a pearl you can reach safely beats the one you can see. |
| islands_a | 32x32 | xy | 2 (4,3) | **Islands joined only by portals.** 4x4 grid of sealed 8x8 islands; the portals sit in shared walls, so one pair links four islands. Two islands per side have a small fountain. Blind crossings and portal memory. |
| islands_b | 48x30 | y | 3 (4,4,3) | 4x3 archipelago of 12x10 islands, 16 portal pairs (8 plus mirrors), one rich island per side. Route planning over a portal graph. |
| open_a | 60x60 | xy | 1x4 | **King race.** Huge empty board, sparse pearls, one dragon each. Foraging efficiency, timer-aware routing, when to split into foragers and when to feed a champion. |
| open_b | 64x40 | y | 2x4 | Largest board (64 wide), small solid kelp pillars, sparse pearls, spawns far apart. Expansion speed, then protecting a champion late. |
| brawl_a | 12x12 | xy | 3x3 | **Pure swarm fight** on the smallest torus with nowhere to hide. Ramming, danger zones, turn-order kills. |
| brawl_b | 12x12 | x | 2 (4,3) | 12x12 with [1,20] everywhere and 4 kelp pillars; heads start 3 apart. Fast growth straight into combat; body-blocking around pillars. |
| famine_a | 24x24 | xy | 2x6 | **Starvation.** 8 pearl tiles on [150,250] for the whole board. Growth is impossible, so kills, corpses and elimination decide the game. Don't die; harvest drops. |
| famine_b | 40x20 | y | 3 (10,3,3) | Starvation with a length-10 flagship and two length-3 minnows each; 6 pearl tiles (4 fire about once a game). Protect the flagship for the tiebreak; use minnows to ram. |
| peel_a | 32x32 | xy | 4 (25,3,3,3) | **Peeling.** A length-25 5x5 serpentine coil plus three minnows. The coil must unwind or split pieces off its outside while enemy minnows go for its head. |
| peel_b | 40x24 | y | 1x36 | One length-36 coil and nothing else: a king with no army. Peel off foragers, or keep the king whole for the tiebreak. |
| webs_a | 32x32 | xy | 2x4 | **Asymmetric-looking portal web.** 16 random-looking pairs plus scattered kelp, 180-degree symmetric underneath. Blind crossings; infer the far end from symmetry and memory. |
| webs_b | 36x24 | x | 2x4 | Portal web with top/bottom mirror: every portal you find has a twin on the enemy half. Your shortcut is also theirs. |
| rush_a | 24x16 | y | 3x4 | **Early rush.** Heads start 7 steps apart, facing each other over a rich patch. Round-1 danger zones, turn order (lower id moves first), ram vs retreat. |
| rush_b | 30x30 | xy | 2 (4,3) | Both teams spawn in the centre about 6 apart; the food is a 10-wide band at the board edge. Disengage and farm, or fight first? |

Notes / caveats
- Pearl tiles inside solid kelp pillars (open_b, brawl_b) are set to never spawn, so "reach" below 100% in
  `--list` only counts those sealed pillar interiors.
- The HTML page header comes from `tools/maps_html.py`, which still says "unseen test maps / of the 80
  generated maps". Only the header text is wrong; the renders are correct.
- Single games at `--seed 1`, v15 (A) vs v14 (B): v14 won 10 of 24. It won brawl_a, fountain_b, fountain_c,
  maze_a, open_b, pockets_a, pockets_b, rush_b, vault_c and webs_b. Treat these as lesson candidates to
  investigate, not as a benchmark.
