# Slithery Fight (ranked map id 21): map-specific plan

Data used:
- **Our games:** 45 real games. v7 ladder 11 (9-2), ch1/ch2 10 (v4-v5, 2-8), ch3 1, ch5 5 (v7, 2-3), ch6 15 (v8, 12-3), ch8 3 (v10, 2-1). The current generation (ch6 + ch8, v8/v10 with KING_V2) is **18 games, 14-4**. Every loss is at round 500 on longest dragon; none is an elimination.
- **Top-team games:** 21 unique games in `notes/replays/permap` (10, 05:36-05:45 UTC) and `notes/replays/kings` (11, 15:52-16:08 UTC). Winners include zitian, STAR, Shannon, Sabotage-d, SSS, Team SKKU, Vibing++, 中国人能飞, bread first search and dev test 1. I did not fetch more.
- **Local practice games:** about 1,000 self-play games with a prototype module (scratchpad copy of `bot/`, nothing in `bot/` changed), against `variants/v8` and `variants/v10h`.
- **Scripts:** `notes/tools/slithery/`. They are read-only over the replays; `common.py` holds the map, gaps, A-frame helper and zones.
  - `games.py` builds `meta.pkl`, our games and our side.
  - `an.py` gives per-game timelines.
  - `deaths.py`, `bigcls.py` and `bigdeath.py` classify big-dragon deaths.
  - `trapage.py` and `childdoom.py` check the U-turn-child bug, and `deepcheck.py` / `dfslib.py` are the perfect-information survival DFS.
  - `kinggrow.py` gives king eats per window, `feed.py` feeder counts and pearl fate, `suicides.py` deliberate suicides per 25 rounds, `deathwin.py` deaths by reason per window, and `churn.py` small-dragon deaths by zone.
  - `eats.py` and `hotwin.py` give eats by zone.
  - `kingpos.py` gives king residency, and `ramrisk.py` ram and trap rates per zone.
  - `opening.py` traces the first 50 rounds.
  - `trap.py` is an ASCII trace of one death (it takes a replay path too).
  - `usplit.py` counts U-turn splits.
  - `localcls.py`, `localcurve.py` and `localbig.py` do the same for local arena replay dirs.
  - `grid.py` renders the map at 2x resolution with walls.
- Prototype module: `notes/maps/slithery_fight_proto.hpp`. The `surviveDepth` patch (TRAIL_FIX) is `notes/maps/slithery_trailfix.diff`.

## 1. The map

- 63x27 with `SYMMETRY xy`, which is a 180° rotation. B's tile is (62-x, 26-y), and N<->S and E<->W swap. **All coordinates below are in A's frame.**
- The border is kelp, so nothing wraps. Unit cap 64.
- Starting dragons, 7 per team, head first:

| slot | body | note |
|---|---|---|
| L7 | (8,10)..(8,16), head facing N | head sits inside hot pocket P1; the tail reaches into P2 |
| L4 | (18,7)..(21,7), facing W | head in hot pocket R7W |
| L25 | coil at (1..5, 20..24), head (3,22) | bottom-left room; only SSS keeps it as king |
| L5 | (33,2),(33,3),(33,4),(33,5),(32,5) | head in hot pocket P3; the tail sits on P4 |
| L2 | (15,13),(16,13) | left field |
| L2 | (26,23),(25,23) | bottom middle, which is **B's** feeding ground |
| L2 | (20,4),(20,5) | top left, next to the comb |

- **Pearl tiles:** 164 rare (gap [1,2559]), 36 at [1,100], 52 at [1,10], 56 at [1,5], and 31 hot [1,1].
- **The "comb" (the richest zone):** (20..31, 0..1) is 24 tiles at [1,5], about 8 pearls/round when harvested.
  - It is three 4x2 cups (x 20-23, 24-27, 28-31).
  - Row 0 is split into 2-tile nooks. Each cup opens south only, through 2 tiles: (21,1)/(22,1), (25,1)/(26,1) and (29,1)/(30,1).
  - Row 2 below it is half-walled: (19,2) and (20,2) have degree 2, and (23,2), (24,2), (27,2) and (28,2) have no N edge.
  - A dragon longer than about 3 can only do the 2-tile U (in (21,1), out (22,1)). Anything deeper is a dead end.
  - B's comb is (31..42, 25..26).
- **Hot [1,1] pockets:** all are 1-wide dead ends.
  - P1: (8,8),(8,9),(8,10). Mouth (8,11), dead end (8,8).
  - P2: (8,16),(8,17)h,(8,18)h. Mouth (8,15).
  - P3: (33,0),(33,1),(33,2). Mouth (33,3).
  - P4: (31,5),(32,5). Mouth (33,5).
  - R7W: (16..18,7). Mouth (19,7).
  - R7E: (21..23,7), hot (22,7),(23,7). Mouth (20,7).
  - Centre (31,13) is a single hot tile in the [1,10] cluster (30..32,12..14).
- **[1,10] clusters:** (41..44,0..1), (39..40,3..6), (25..27,9..12), (30..32,12..14), (35..37,14..17), (22..23,20..23) and (18..21,25..26).
- **Portal tube:** (4,14) E -> (58,13), (58,13)-(58,14)-(57,14)-(57,13), then (57,13) E -> (5,14).
  - It is a 4-tile blind loop of [1,5] pearls in B's half, entered from our left field. (4,14) and (5,14) are not adjacent to each other.
  - The mirror tube (4..5,12..13) belongs to B.
- **Diagonal staircase wall** from (14,6) to (20,2). It leaves a row of degree-2 corner tiles: (18,3), (19,3), (19,2), (20,2), (16,4), (17,4) and (15..16,5). This is where big dragons coil and die ((19,3) three times, (18,6), (20,1)).
- Halves: the x ≤ 30 half is ours. The bottom band y ≥ 19 with x ≥ 18 is B's feeding ground: their L5 pocket at (29,24..26) and their comb at (31..42,25..26).

## 2. How we do on Slithery

Current generation: 14-4. The 4 losses, all at round 500:

| game | opp | final (us v them) | what happened |
|---|---|---|---|
| ch6 411166 | Codehammer 40K | 33 v 49 | L24 (r348, (39,1)) and L33 (r395, (30,4)) rammed head-on by enemy L3/L5 in the top-middle |
| ch6 411170 | Deer Park | 42 v 51 | L32 king self-trapped r353 at (18,6), a U-turn child born r335; L19 r315 and L20 r431 also trapped |
| ch6 411179 | SilverSamurai | 48 v 57 | no big blunder; they surged 35 -> 57 in the last 50 rounds (merges) |
| ch8 416135 | Maccas | 34 v 43 | L37 self-trapped r485 at (21,16), a U-turn child born r477 |

Older losses repeat the pattern: ch5 403809 usagi, **L41 king self-trapped r483** (final 17 v 27, would have won); ch5 403829, L24 trapped r483.

**Big-dragon (L≥12) deaths per game** (`bigcls.py`):

| | trapped by own body | rammed by enemy | merge / other |
|---|---|---|---|
| us (18 games) | **2.45** (1.56 + 0.89 of them were the team's longest) | **1.50** | 1.4 |
| top winners (21) | 0.72 | 1.00 | 1.0 |
| top losers | 0.62 | 1.95 | 1.3 |

### Finding A: the self-traps are mostly a body-memory bug in U-turn children

- **38 of our 51 trapped L≥12 deaths** (current + v7 challenges) are children of a reverse split (`SPLIT L-2`, k ≥ 8) that died **younger than their own length** (`trapage.py`).
- 29 of 39 were escapable at birth under perfect information (`childdoom.py`). They walked into their own coil later.
- **Cause (confirmed in a debug run):**
  - A child is a new process. `updateTrail()` rebuilds its body only from the chain it can see: 7 tiles of a 44-long body in the traced case (dragon 1790, seed 3).
  - `surviveDepth()` then simulates a body of length `trail.size()` = 7. It thinks its tail frees 35 moves early and happily enters its own coil.
  - Its own visible but unchained segments get freeT 1000000+, which is correct but not enough.
  - Unseen segments are invisible to the DFS.
  - `tailHasExit()` returns false for an incomplete trail, so a child can never U-turn again. The next trap is always fatal.
- Top teams do 27-34 U-turns of L≥12 dragons per game (we do 10.4) and lose only 0.7 big dragons to traps. Their children survive.
- **Why the parents get trapped in the first place** (debug trace, parent 1660, seed 3):
  - The king (L42) stepped N from (25,3) to (25,2) at R431. The 12-deep DFS and area (1210) looked fine.
  - An allied body at (26,2) didn't free, because allies eat constantly in the comb, so their tails stall.
  - One round later it was in the (25..26,1) cup with area 3-4. It U-turned, and the child died 13 rounds later.
  - 10 of our 16 trapped-king deaths are in the box x 18-33, y 0-6: (19,3)x3, (24,1), (25,0), (23,2), (18,6), (31,1), (20,1), (29,0)/(30,0).
  - Our non-ram death rate for L≥12 there is 9.7-13.3 per 1000 dragon-rounds; winners' is 2.3-3.6 (`ramrisk.py`).

### Finding B: the r250 feeding burst empties the swarm

- Deliberate suicides per 25 rounds (`suicides.py`):
  - Us: 0.3 before r250, then **33.8 (r250), 28.3 (r275)**, 20, 14, 13, 11, 10, 6, 4, 2.
  - Top winners: about 1 per 25 rounds before r250, then 5, 12, 10, 11, 16, 14, 14, 15, 10, 8.
- Units:

| | r250 | r300 | r350 | r400 | r450 |
|---|---|---|---|---|---|
| us | 62 | 39 | 33 / 28 | 22 / 15 | 11 |
| top winners | 63 | 59 | 55 | 44 | 28 |

- **King eats per 50 rounds** (`kinggrow.py`, "king" = current longest):

| | r250 | r300 | r350 | r400 | r450 |
|---|---|---|---|---|---|
| us | **11-14** | 8-9 | 5-7 | 4-8 | 6-8 |
| top winners | 8 | 11 | 13 | 13 | 13.5 |

- King length:

| | r300 | r350 | r400 | r450 | r499 |
|---|---|---|---|---|---|
| ours | about 20 (ahead of winners) | 26-29 | 27-30 | 34 | 40 |
| winners | 15.6 | 23.5 | 33 | 43 | about 62 |

  Our king forms early and then starves.
- Only 37% of pearls dropped by feeders reach the king (winners 41%). 58% are eaten by our other dragons.

### Finding C: rams on big dragons happen in B's territory

- Our L≥12 ram rate per 1000 dragon-rounds:
  - Bottom band x 18-26: 3.9. x 27-35: 7.7. x 36-44: **15.0**. The top-middle is 1.5-3.0.
  - x ≤ 17, all y: 0-1.2.
- 15 of our 27 rams on L≥12 are at y ≥ 19 with x ≥ 16, or at x ≥ 34. The rammers are enemy L2-5 at distance 1.
- Winners' kings are at enemy-head distance ≤ 3 in 6.2% of rounds; ours in 5.1%. Proximity isn't the difference; the zone is.

### Finding D: we skip the hot pockets

Own hot-pocket eats per game: us **36** against top winners 183 and our opponents about 200 (P1 42 vs 2.6, R7W 41 vs 8.6, R7E 24.5 vs 7.4). The comb we harvest fine (498 vs 450). The pockets are a +150 pearls/game gap, but they are small dead ends. Top teams use them as eat-and-die spots: HitWall deaths of L2 at the dead ends, about 10 per game per pocket in r150-399.

### Opening

Ours is already the same as the top teams' (`opening.py`). At r0:
- The L7, L4 and L5 pocket starters split. The head part eats the pocket and dies at the dead end by r4-5.
- The L25 coil splits (0,23,2) or (0,2,23) and is L3 by r15.
- Nobody except SSS keeps a starter as king.

No change needed.

## 3. Local practice (self-play, scratchpad prototype)

All of these are vs pool v8 + v10h on slithery_fight only. Self-play is a coin flip between near-identical bots, so ±0.15 is noise at 40 games.

| variant | games | score | note |
|---|---|---|---|
| baseline (current bot) | 40 (seeds 25500+) | 0.525 | |
| baseline | 80 (26500+) | 0.487 | |
| TRAIL_FIX | 40 | 0.500 | correct fix, but self-play can't see it: the v10h opponent has the same bug |
| SLI_FEED=1 (reserve 56/50/40/26/12/4 by round) | 40 | 0.475 | arena vs v10h 5/16; units 56 at r300 but king smaller all game |
| SLI_FEED=2 (keep burst, ration r300-450) | 40 | 0.450 | |
| SLI_FEED_MINK=12 (no feeding until the king is ≥12) | 40 | **0.075** | the r250 burst is what creates the king: do NOT delay it |
| SLI_DEEP=32 + TRAIL_FIX | 16 arena | 7/16 | trapped children unchanged (39 vs 33) |
| SLI_ZONE=40 (comb + ram zones) | 40 | 0.425 | ram zones hurt in self-play (v10h doesn't hunt kings like ladder teams) |
| SLI_ZONE=40, comb only (y ≤ 2, x 19-33) | 40 | 0.500 | |
| SLI_ALLYGAP=30 | 40 | 0.500 | |
| **split stop 420** (`SLI_SS=420`) | 40 + 80 + 16 | **0.575, 0.613 [0.503, 0.712], 7/16**; pooled **79/136 = 0.58** vs baseline 68/136 = 0.50 on the same seeds | |
| split stop 450 | 80 | 0.588 | |
| split stop 400 | 80 | 0.475 | |

With split stop 420 we hold 30 units at r400 vs the opponent's 20 (arena curves). That matches the top teams' "never really stop splitting".

## 4. Proposed behaviours (ranked)

Helpers: `sliA(t)` maps tile t to A's frame: x = t % 63, y = t / 63, and if `w.myTeam == 'B'` then x = 62 - x, y = 26 - y. Directions mirror as (d+2)%4. All flags go in `bot/maps/slithery_fight.hpp` except S1, which is a `main.cpp` change behind a flag.

### S1. TRAIL_FIX: U-turn children must not forget their own body

**Fixes:** the #1 measured big-dragon loss cause, 2.1 deaths/game. The traps include L41, L37, L36, L35, L32 and L31 kings, and 2-3 of our 6 recent losses.

1. In `surviveDepth()`, when `trail.size() < myLen`, simulate a body of length `myLen`. Pad the ring with unknown entries (-2) that never block and never free. The known trail tiles then free only after `myLen - i` moves, which is correct. Patch: `notes/maps/slithery_trailfix.diff`, tested to compile and run.
2. The DFS still can't see off-screen own segments. So for a child with an incomplete trail and `myLen ≥ 12`:
   - (a) Require `area ≥ myLen + 3`, and add the survival penalty scaled to the missing depth, using `min(myLen, 24)` as depth. The penalty is -150 - 40·(want - depth), the same as the base.
   - (b) Treat the parent's side as blocked: the parent's trail was the child's body reversed, and the child's unseen segments lie behind its visible chain. Penalise any tile not visible and within Manhattan 2 of the last known chain tile by -60 for `myLen - trail.size()` rounds.
3. In the parent, before `SPLIT myLen-2`, run the DFS from the old tail with the reversed body. If both the parent and the child are doomed, prefer a halving split (`SPLIT myLen/2`), so at least one half with a complete trail survives. 10 of 39 children were doomed at birth.

**Test on the ladder / challenges, not self-play.** The v8/v10h pool has the same bug, so it can't show the gain. Guard all maps, since the bug is global: Schooltime, Portals and Trauma kings U-turn too.

### S2. RP: split stop 370 -> 420 on Slithery

- Change `v2("Slithery Fight", 170, 370, 250, …)` to `v2("Slithery Fight", 170, 420, 250, …)`. Also valid from the hook with `RP.splitStopRound = 420` (prototype flag `SLI_SS`).
- Evidence: local 0.58 over 136 games vs 0.50 for the baseline on the same seeds, with 450 also at 0.59 and 400 at 0.475. Top winners keep 55 units at r350 and 44 at r400 (ours 29-33 and 15-22). They keep splitting to about r480 and feed steadily 8-9 per 50 rounds through r450, while ours drops to 1.4 then 0.4.
- Keep FEED_START 250 and the r250 burst: FEED_MINK=12 scored 0.075.

### S3. Comb and staircase exclusion for big dragons (score hook)

- For `myLen ≥ 12`, in A frame: -40 for stepping onto any tile with y ≤ 2 and 19 ≤ x ≤ 33 (the cups plus the half-walled row 2).
- Add -40 for the staircase corner tiles: (18,3), (19,3), (17,4), (16,4), (15,5), (16,5), (14,6), (19,2), (20,2).
- Add -80 for the pockets P1-P4, R7W, R7E and the portal tube entries: (4,14) moving E and (5,14) moving W, which lead to the 4-tile blind loop.
- Uniform penalties only act at the boundary, so a king already inside still leaves.
- Evidence:
  - 10/16 of our trapped-king deaths are in x 18-33, y 0-6. Our L≥12 trap rate there is 9.7-13.3/1000 vs winners 2.3-3.6.
  - The parent-trap trace entered (25,2) and then the cup.
  - The portal tube killed L29, L16 and L15: 0.17/game.
- Local, comb only: 0.50 (neutral, so it costs nothing in self-play).
- The comb is still harvested by small dragons: 498 eats/game, better than the top teams.

### S4. King rammed-zone avoidance, soft (score hook), ladder-test only

- For `myLen ≥ 15` or `kingSelf`, in A frame: -15 for tiles with x ≥ 34, or with y ≥ 19 and x ≥ 18.
- Optionally `RP.kingKeepExtra = 1` on Slithery (keep 5 tiles instead of 4 from enemy heads for L≥15).
- Evidence: L≥12 ram rate 3.9-15/1000 in those zones vs 0-1.2 at x ≤ 17. 15/27 of our big-dragon rams happen there, including the 411166 loss: L24 at (39,1), L33 at (30,4), which is next to the P3/P4 pockets that enemy L3-5 raid.
- At weight 40 together with S3 it scored 0.425 in self-play. v10h doesn't raid like Codehammer/Deer Park, so use a small weight and validate with challenges vs ranks 40-75 on Slithery (the ch6 set: 12/15 baseline).

### Not recommended

- **Throttling feeding (SLI_FEED 1/2):** keeps units but not king growth. The king's eat rate is the bottleneck (1 pearl/move; 58% of drops go to other allies), not feeder supply.
- **Delaying feeding until the king is big (FEED_MINK):** 0.075.
- **Deeper plain DFS (SLI_DEEP=32):** no change; the traps come from wrong body memory and stalled ally tails, not horizon.
- **Hot-pocket factory:** a +150 pearls/game potential, but the pockets are 2-3 tiles deep (Trauma's cycle needs 8), and spawn-pearls are only 18% of king food on this map. Revisit only after S1-S3.

## 5. Suggested test order

1. S1 on all maps vs the pool, as a guard.
2. S1 + S2 + S3 on Slithery vs v8,v10h, 20 seeds, base 26500.
3. Submit and run Slithery challenges vs the ch6 opponents (ranks 45-72). Judge by our king at r450/r499 and big deaths per game (`an.py`, `bigcls.py`), not just W/L.
