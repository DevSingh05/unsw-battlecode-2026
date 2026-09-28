# 08 - Per-map strategy (strong-vs-strong replays, 27 Sep 2026)

**Question:** do the top teams play each map differently, and what should our bot change per map?

**Short answer:** yes. On five of the ten maps the winner is decided by the unit count by round 100-200, and the game ends in elimination (Trophy, Devil, Queen of Spades, Prisoners Dilemma, and in part Default). On the other five nobody gets eliminated and it is a king race (Portals, Trauma, Schooltime, Slithery, and in part Autarky). The main things that change between maps are:
- when the swarm stops splitting;
- when one king emerges;
- when feeding starts;
- whether to build a king at all.

## Data and tools
- 97 unique games, all played 2026-09-27 between 05:35 and 06:10 UTC. Both teams had Elo ≥ 1850 at game time. Draws are excluded.
  - Ten games per map. The exception is Prisoners Dilemma: 8 unique games (see the note on determinism below).
  - Teams in the sample: zitian 38, dev test 1 34, 龙虎豹 24, 中国人能飞 21, STAR 18, Peanut Butter 16, Vibing++ 14, calc 11, Shannon 7, Sponge 7, Sabotage-d 4, and others.
  - **Caveat:** zitian vs dev test 1 appears in many games, so a few teams dominate the medians.
- **Replays are deterministic.** The same pairing on the same map gives a byte-identical game: 352700, 352845 and 353020 are the same game, and so are 352788 and 352862. The scripts dedupe these.
- Files:
  - Replays: `notes/replays/permap/*.replay`, with `index.json` and `permap_metrics.json` (per-game metrics).
  - `notes/tools/permap_fetch.py`: lists and downloads the games. Read-only GETs, 1.2 s apart.
  - `notes/tools/permap_analyze.py [--rows]`: per-game rows and per-map winner/loser medians.
  - `notes/tools/permap_curves.py`: median curves every 25 rounds.
  - `notes/tools/permap_ours.py`: the same metrics for **our** games in `replays/ch1`. These are 50 challenge games of v4 against ranks 16-20; we went 16-34.
- Definitions:
  - **split stop:** the first round after which the team makes fewer than 3 more small (L ≤ 5, k = 2) splits.
  - **feeder:** our dragon of L ≤ 4 that dies at round ≥ 200 within Manhattan distance 4 of a king of L ≥ 8.
  - **ram:** a head-to-head death where the mover and the victim are on different teams.
  - **hot:** a spawn eat on a tile with gap [1,1].
  - **startdist:** walking distance, through portals, from A's start to B's start.

## 1. Per-map evidence (medians, winner W vs loser L)

| map | class | elim / games (rounds) | units W/L @100 | units W/L @300 | longest W/L @300 / 400 / 499 | W split stop | W longest ≥10 / ≥20 | W feeding (first / median) | rams W/L | hot eats W/L | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Trophy** 25×25 | combat | 10/10 (55-422, median 165) | 30 / 9 | 38 / 15 | never above 5-9 | never stops (swarm until win) | - | none | 22 / 10 | 0 | pure swarm, peak 57 units |
| **Devil** 32×16 | combat | 10/10 (106-375, median 137) | 35 / 4.5 | 56 / 2 | never above 4-5 | never stops | - | none | 14 / 6 | **126 / 21** | winner eats 6x the hot pearls; startdist 31 |
| **Queen of Spades** 25×35 | combat | 9/10 (170-449, median 304) | 11 / 8 | 30 / 3 | 3.5 / 7 / 10 | ~300-320 (still splitting when the enemy dies) | 181 / 434 | ~0 (1 game had 25 from round 393) | 15 / 8 | 0 | the only round-500 game was won 10 vs 9 on longest |
| **Prisoners Dilemma** 32×16 | combat early | 6/8 (46-318, median ~104) | 12 / 2.5 | 32 / 9 | 6 / 10.5 / 29 | ~195 | 215 / 444 | none | 5.5 / 1 (first ram at round 8) | **75 / 7.5** (92% of spawn eats) | the 2 round-500 games were 龙虎豹 vs 中国人能飞, 1-1 |
| **Default** 32×32 | mixed | 3/10 (110-270) | 18 / 10.5 | **58 / 9** | 6 / 9 / 39 | 345 (last small split 492) | 385 / 430 | 384 / 423 | 25 / 12 | 0 | startdist **2**: the teams start in contact, rams from round 2 |
| **Autarky** 54×18 | mixed | 5/10 (226-448) | 21.5 / 16.5 | 54.5 / 15.5 | 5.5 / 7 / 28 | 315 (last 386) | ~400 / 455 | 420 / 431 | 28 / 18 | **204 / 60** (52% share) | winner holds 55-59 units until round 400, then consolidates |
| **Schooltime** 60×40 | growth with heavy combat | 2/10 | **52 / 39** | 63 / 62 (cap) | 14 / 27 / **58** vs 12 / 21 / 46 | **380** vs loser 430 | **140** / 279 | **249** / 340 | 64 / 67 (the most combat of any map) | 0 | winner at the 64 cap by round 125; units fall 63→38→12 over rounds 325-450; king/second at 450 is 1.7 vs 1.16 |
| **Slithery Fight** 63×27 | growth | 0/10 | 61.5 / 58.5 | 62.5 / 62.5 (cap) | 13 / 21 / **37** vs 7.5 / 16.5 / 25.5 | ~480 (never really stops) | 112 / 232 | 248 / 386 | 41 / 44 | 251 / 218 | units stay at the cap until 375, then fall to 55→26→17; winner makes 25 feeders vs 11.5 |
| **Trauma** 48×24 | growth | 0/10 | 18.5 / 14 | 32.5 / 35.5 | 6 / 14 / **31.5** vs 4.5 / 7 / 18 | 470 (factory splits); swarm units fall from **~300** | **307 / 356** vs L 332 / 338 | **308** / 402 | 11 / 10.5 (first ram at round 133; startdist 98) | 205 / 187 | earliest consolidation of the growth maps; king/second at 450 is 2.26 vs 1.4; 16 feeders vs 8 |
| **Portals** 32×16 | pure growth | 0/10 | 12.5 / 10.5 | 31 / 28.5 | 5 / 6 / **25.5** vs 4 / 7 / 17.5 | 400 | 374 / 448 | 363 / 411 | **0 / 0** | 123 / 144 | **the two halves are not connected**: no enemy contact at all, and every head-on death is between allies (about 400 over 10 games) |

**Kill methods.** Feeder kills (winners) are mostly HitSelf, then NoValidAction and HitWall. Feeders die at distance 1-4 from the king:
- Schooltime winners: d1 33, d2 28, d3 27, d4 19.
- Trauma winners: 69 / 64 / 53 / 17. That is closer than the loser (24 / 33 / 28 / 18).

**Winners consolidate harder.** At round 450 the winner's longest is 1.4-2.3 times its second-longest; the loser's is 1.16-1.4 times. On Schooltime and Slithery the loser ends with **more total length but a shorter king** (Schooltime total length 166 vs 235, king 58 vs 46). Growth maps are won by sacrificing total length for one dragon.

## 2. How our bot (v4, `replays/ch1`) compares with ranks 16-20, per map

| map | our record | us vs them |
|---|---|---|
| Schooltime | 0-5 | Our longest at 300 is **3 vs 13**; longest ≥10 at round 369 vs 161; final 24.5 vs 48.5. We have 40 units at 300 vs 53: we never reach the cap, so nothing grows. We make **148 rams/game** (they make 45) and have **52 ally head-on deaths/game** (they have 7). |
| Trauma | 1-4 | **0 hot eats vs 131.** Our longest ≥10 comes at 466 vs 185. Final king 11 vs 13 (their king is small too, but ours is smaller). |
| Slithery | 1-4 | **Hot eats 29 vs 508**; longest ≥10 at 382 vs 212; final 24 vs 34. |
| Autarky | 2-3 | **Hot eats 4 vs 138.** They start feeding at 311, we start at 412. |
| Portals | 3-2 | Fine: final 21 vs 10. But **hot eats 35 vs 228**, and 24 ally head-on deaths/game vs 6. |
| Default | 1-4 | Eliminated in 4 of 5 (rounds 95-405). They have 33 units at round 300 vs our 1.5, and their king is 14 by round 300. We lose the opening brawl. |
| Queen of Spades | 1-4 | All eliminated. At round 300 they have 24 units vs our 2. |
| Trophy | 3-2 | 17 ally head-on deaths/game. |
| Devil | 2-3 | Hot eats 6 vs 37. |
| Prisoners Dilemma | 2-3 | |

**The two biggest gaps are not about timing.**
1. **Hot-tile harvesting.** We are near zero on every hot map; the top teams take 130-500 per game.
2. **Allies killing each other head-on** on the portal maps: Schooltime 52/game, Portals 24.

The per-map timing changes below matter mostly on the growth maps, where we form the king about 150-300 rounds later than winning teams.

**A structural point.** With `KING_DECLARE=0` and `SPLIT_LEN=4`, every dragon of length ≥4 splits until `SPLIT_STOP_ROUND`. So no king can form before 350 unless the unit cap blocks splitting. The top teams let one dragon grow while the rest keep splitting. That needs `KING_DECLARE=1` (the declared king and big-late dragons are exempt from splitting), with `KING_SEED_ROUND` set per map.

## 3. Recommendations: per-map parameter table

The params are compile-time globals now. Make them a runtime `struct Params` chosen by the recognised `KnownMap` name, with the current defaults for unknown maps. Then A/B test each row with `tools/arena.py --maps <map> --seeds 5` against v4/v5 before shipping.

| map | class | SPLIT_STOP_ROUND | FEED_START | KING_DECLARE / KING_SEED_ROUND | KING_MIN_LEN | RAM_MAX_OWN_LEN | SPLIT_LEN | other |
|---|---|---|---|---|---|---|---|---|
| Trophy | combat | **500** | **500 (off)** | 0 | - | **4** | 4 | Swarm only: winners never grow past 5 and have 3x the enemy's units by round 100 |
| Devil | combat | **500** | **500 (off)** | 0 | - | **4** | 4 | Hot-tile harvest first (winners 126 vs 21) |
| Queen of Spades | combat | **450** | **440** | 0 | **6** | 3 | 4 | Keep swarming; a late mini-king only as a tiebreak insurance (the round-500 game was won 10 vs 9) |
| Prisoners Dilemma | combat early | **450** | **420** | 1 / **350** | 8 | 3 | 4 | Hot corridor is 92% of spawns; rams start at round ~8, so fight from turn 1 |
| Default | mixed | **375** | **380** | 1 / **350** | 8 | 3 | 4 | Opening brawl decides it (winners 58 vs 9 units at round 300); keep reserves, no early king |
| Autarky | mixed | **400** | **400** | 1 / **380** | 8 | 3 | 4 | Hold about 55 units to round 400, then consolidate; hot tiles are 52% of spawn eats |
| Schooltime | growth + combat | **350** | **250** | 1 / **150** | 8 | 3 | 4 | Hit the 64 cap by round ~125; king ≥10 by 140, about 27 by 400, target 55-60; consider KING_THREAT_REACH 5 (winners lose 4.5 L≥10 dragons/game head-on) |
| Slithery Fight | growth | **400** | **350** | 1 / **250** | 8 | 3 | 4 | Stay at the cap to 375; about 25 feeders; hot tiles 250/game; target king 37+ |
| Trauma | growth | **325** (factory stubs exempt) | **300** | 1 / **275** | 8 | 3 | 4 | Earliest consolidation: king ≥10 at about 307, ≥20 at 356, target 30+. Build the hot-corridor factory. |
| Portals | pure growth (no enemy) | **400** | **360** | 1 / **330** | 8 | irrelevant | 4 | FEED_RESERVE **2**, KING_THREAT_REACH **1** (no enemy can reach); the only risk is ally portal collisions; target king 25+ |

**Why these values.**
- **SPLIT_STOP_ROUND** is the round at which the winners' unit count starts to fall:
  - Schooltime 325-350, Trauma 300-325, Slithery/Portals/Autarky about 400, Default about 425.
  - On combat maps winners never stop splitting before the enemy is dead.
- **FEED_START** is the winners' first feeder round:
  - Schooltime 249, Slithery 248, Trauma 308, Portals 363, Default 384, Autarky 420.
  - It is shifted slightly where the median sits much later (Slithery median 386, so we use 350).
- **KING_SEED_ROUND** is about 30-50 rounds before the winners' longest reaches 10:
  - Schooltime 140, Slithery 112 (tied to the cap), Trauma 307, Portals 374, Default 385, Autarky about 400.
  - Losers on every growth map reach 10 later: Schooltime 179, Trauma 332, Portals 400, Default 469.
- **RAM_MAX_OWN_LEN.** Ram counts don't separate winners from losers on the growth maps: Schooltime 64 vs 67, Slithery 41 vs 44. On the elimination maps they do: Trophy 22 vs 10, Devil 14 vs 6, QoS 15 vs 8. So we only loosen it (4) on Trophy and Devil.

**Not a parameter, but the biggest win.**
1. **Hot-tile factory / camping.** Priorities are Trauma, Slithery, Autarky, Portals, Devil and Prisoners Dilemma. We are at 0-35 hot eats per game against 130-500.
2. **Ally head-on avoidance through portals.** Schooltime has 52 ally deaths per game.

v5's portal warnings target (2). Re-measure with `permap_ours.py` on `replays/ch2`.
