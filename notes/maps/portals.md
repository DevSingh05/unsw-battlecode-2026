# Portals (ranked map id 20): map-specific plan

Data used:
- 55 of our real games: v7 ladder 21, ch1 5, ch2 5, ch3 1, ch5 5, ch6 15, ch8 3. Record 38-17. Every game went to round 500; an elimination is impossible on this map.
- 21 top-team games: `notes/replays/permap` 10 and `notes/replays/kings` 11. That is 42 team-samples; Sabotage-d appears 5 times.
- About 1,300 local games of a prototype module against the current bot.

Scripts are in `notes/tools/portals/`. `por_load.py`, `por_an.py` and `por_geo.py` are the shared loaders. The reports are `por_rep1` (ours), `por_rep2` (top), `por_big`/`por_loc`/`bigcat` (deaths), `por_king`/`kingsrc`/`curve`/`feedeff` (king), and `prun.py`/`variants.sh` (local A/B runs). The prototype module is `notes/maps/portals_proto.hpp`.

## 1. The map

- Size 32x16, `SYMMETRY xy`: 180° rotation, so B's tile is (31-x, 15-y).
- Starts (head first). A: (0,5)↓, (1,11)↑, (12,1) facing W. B: (31,10), (30,4), (19,14).

**The two halves are separate components.** There are exactly 2 components of 240 tiles (plus 16 unreachable 2-tile boxes).
- No enemy can ever reach us. There are no rams and no threats; `threatAt` is always 0 here.
- Enemy pearl timers are shared with ours (mirror tiles), but their play cannot block our spawns.
- So **Portals is a solo race: the only thing that matters is our own longest length at r500.** Local self-play measures it exactly. Each game gives 2 independent samples, one per side.

**All 36 of a team's pearl tiles are physically in the other half and reached only through portals.** Our 7x7 vision never shows them until we are inside. A's structures:

| structure | enter from (main tile, dir) | 4 pearl tiles [1,10] | exit (main tile) |
|---|---|---|---|
| tube T1 | (12,13) E | (19,0) (19,1) (18,1) (18,0) | (13,13) |
| tube T2 | (3,15) N | (27,0) (26,0) (26,1) (27,1) | (3,14) |
| tube T3 | (8,11) E | (23,6) (23,7) (22,7) (22,6) | (9,11) |
| tube T4 | (12,5) E | (19,8) (19,9) (18,9) (18,8) | (13,5) |
| tube T5 | (3,6) S | (27,9) (26,9) (26,8) (27,8) | (3,7) |
| tube T6 | (8,2) E | (23,14) (23,15) (22,15) (22,14) | (9,2) |

- Every tube is two-way: entering from the exit tile in the opposite direction runs the same 4 tiles in reverse.
- **A tube is a detour spliced into one main-area edge.** Walking straight E from (11,5) you go (12,5) → 4 pearl tiles → (13,5) → (14,5). That is 5 moves for 4 pearls, and it is safe for any length when done in a straight line.
- **The U-turn trap.** Entering from e when you arrived there from the exit tile x is fatal. You eat 4 pearls, so the tail does not move, and x is still your body when the head comes out. Our survival DFS doesn't see this: it only "eats" visible pearls and [1,1] tiles, and tube tiles are never visible from outside.

**Pockets (8 per team) are dead ends.** Each is one [1,10] pearl tile behind a portal with no way out. The entry pairs are (4,1)/(5,1), (8,6)/(9,6), (4,9)/(5,9) and (12,9)/(13,9): stepping E from the left tile or W from the right tile of the pair drops you into the pocket.
- Diving costs about 1 mass. For example, an L3 eats (L4), splits 2, and the parent L2 dies, leaving 1 pearl in the pocket.

**The sock (1 per team)** is a 1-wide dead-end corridor of 9 tiles with 4 hot [1,1] tiles.
- A enters at (14,0)→E (15,0), runs S along x=15 to (15,7), then E to the dead end (16,7). The hot tiles are (15,1), (15,3), (15,5), (15,7).
- B enters at (17,15)→W (16,15), runs N along x=16 to (16,8), then W to (15,8). The hot tiles are (16,8), (16,10), (16,12), (16,14).
- The inner starter A (12,1) is 5 moves from the first hot pearl, and top teams eat it at r4.

**Income ceiling.** 32 tiles at [1,10] give about 5.8 pearls/round and 4 hot tiles give 4/round, so roughly 9.8/round if everything were harvested instantly. Tiles that hold a pearl block their own respawn. The best observed team (Sabotage-d) harvests about 2.2/round.

## 2. How we lose (our 55 real games)

**Record 38-17. Every loss is on longest at r500:** in losses we are at median 21 and they are at 27.

| (medians) | us | opponent |
|---|---|---|
| first pearl eaten (round) | **160** (43/55 games ≥ r100; 2 games never ate) | **4** |
| units @100 / @200 | **3 / 6** | 18 / 26 |
| spawn eats r0-100 / r100-200 | **0 / 8** | 58 / 146 |
| spawn eats, whole game | 333 (hot 73, tube 260) | 531 (hot 136, tube 395) |
| longest @400 / @450 / @499 | 14 / 21 / 27 | 9 / 15 / 19 |

(The opponents here are ranks 16-76.)

**Root cause 1: the first 150-200 rounds are wasted.**
- The inner starter wanders around x 9-12, y 1-7 (trace of ch8 416124). It never enters the sock or a tube, and all 3 starters stay at L3 with 3 units until about r150.
- From the move-score dump (`BOTDBG`, local seed 1, dragon 4), there are two reasons:
  - `pearlValue` values an unseen tile at `0.5*min(1, since*rate)`, which caps at 0.5. Tube tiles are never seen from outside, so a tube that is certainly full (4 pearls) is worth about 2 at 0.5 each.
  - The BFS sums such values over all 36 tiles with γ=0.82, so the pearl score is flat (about 1.9-2.8 for every direction), which gives no gradient.
- The first eats happen only by accident when a dragon walks through a splice edge, at median r160.

**Root cause 2: big dragons die in tubes.**

| per game, L≥8 | us (all 55) | top teams |
|---|---|---|
| big deaths | 5.3 (62.8 length) | 3.2 (34.2 length) |
| in tubes | 1.4: HitSelf 0.71 (the U-turn trap) + ally at the exit 0.71; 1.9 in ch5-8 | 0.7 |

Examples:
- 411161, r407: L20 at (18,8), move E, the exit (13,5) holds an ally.
- 411169, r395: L11 at (18,0), move S into its own body.
- Pocket kings: 411157 r415 L17 at (19,12); 416124 r464 L21 at (27,5).

The rest are HitSelf in the main area. About 3.4 per game of these are deliberate merges within 4 of the king.

**Not a cause.**
- Once the king exists, our king's diet from r300 matches the top teams: spawn 24 and corpse 42 (theirs 21 and 46). Its location split is also similar: 83% main area, 16% tube.
- **The late-game shape differs.** We consolidate earlier (longest 14 at r400) and they consolidate later (7 at r400, 24 at r450, 33 at r499).
- Our 2nd-longest at r499 is large. See §4 P2.

## 3. How top teams play Portals (21 games, 42 team-samples)

- **Opening.** 35 of 42 team-samples eat their first pearl by r9, and 32 at exactly r4. Sabotage-d (407118) moves straight to the sock and the tubes:
  - The inner starter goes N, E, E, E, S into the sock and eats (15,1) at r4, then splits 2 inside the sock at r5 (1 exit).
  - The other two starters walk into T5 (3,6)S and T2 (3,15)N at r5 and split 2 at L4 inside the tube.
  - The parent (head part, L2) keeps eating through the tube while the child (the rear 2) is born outside and walks off. In the sock, the last parent dies at the dead end (HitWall), and its corpse is eaten on the next pass.
  - Result: units 20-26 at r50, 31-41 by r100 (ours: 3).
- **Income** (winners, median spawn eats per 100 rounds): 76, 140, 133, 125, 46; hot 154 and tube 369 per game. Sabotage-d: 193, 207, 191, 135, 48.
- **Pockets.** Pocket dives are frequent: 98 deaths per game, almost all L2-3. That is about neutral in mass (−1 per dive); do not copy.
- **Kings.**
  - Final: winners 33 median, all 34; Sabotage-d 41-55.
  - Sabotage-d's king is an ordinary split child (born r260) that stops splitting at about r275. It is L10 at r300, 24 at r400, 46 at r499.
  - The team keeps 21-26 units farming until r400, and total mass stays 84-100 until r425.
  - Only one big dragon survives: the final 2nd-longest is about 10. Ours is 23 in local runs; see P2.
  - King food after r300 is mostly corpses (Sabotage-d: 51 corpse, 5 spawn; winners: 46 corpse, 22 spawn).
- King location r300-499: main area 81%, tubes 7%, sock 7%. Nobody is ever rammed.

## 4. Proposed behaviours

### P1. Tube and sock pull (POR_PULL): the main fix. TESTED, recommended.

**Hook:** `portalsScore(t,d)`. The geometry is built once with `step()` from the known map in `porInit()`:
- For every main tile e and direction d whose `step(e,d)` is a [1,10] tile, follow the chain to the 4 tube tiles and the exit x, or detect a pocket (0 onward exits).
- The two socks are hard-coded: A enters at (14,0) going E and B at (17,15) going W, with the 9 tiles listed in §1.

**Value model** `porP(t, r)`, the chance of a pearl when our head reaches t on round r:
- hot tile: 0.9 if unseen; if visible, 1 when a pearl is shown, else 0.95 for future rounds.
- never-seen [1,10] tile: `min(1, (r+1)/gmax)`, i.e. certain after round 10.
- seen with a pearl: 0.9.
- known countdown (`spawnAt > lastSeen`): 0.9 once `r >= spawnAt`, else 0.
- otherwise: `0.9*min(1, (r - lastSeen)/gmax)`.

**Pull.**
- Run a BFS from t over main-area tiles only, honouring `freeT`.
- For each entry, `dist = bfs[e]+1`, or 1 if this move enters. Compute `v = Σ porP(tile_i, round+dist-1+i)`.
- Multiply by 0.4 if a visible ally head is nearer the entry, and by `POR_G^(dist-1)` with `POR_G = 0.88`.
- Add `POR_W * max v`, with **POR_W 12-16** (see the sweep below).
- The sock only counts for `myLen <= 3`: those dragons can escape by splitting at 4, which the DFS already allows.
- No pull while `shouldFeed()`, so feeders still go to the king.

**Exit guard (POR_EXIT).** When this move enters a tube (`myHead==e && d==dir`), subtract 300 if the exit x holds our own body at any index (the U-turn trap), an ally head, or an ally segment with `freeT[x] > 5`.

**Local results (per-side final longest, same games, 120 samples):**

| metric | prototype P1 | current bot |
|---|---|---|
| mean final (median) | **31.9** (33) | 27.3 (27.5) |
| "wins" (X longer than Y) | **81/120 = 0.68** | |
| spawn eats/game | 747 (hot 203, tube 544; Sabotage-d level) | 382 |
| units @100 | 32 | 6 |
| total mass @300 | 90 | 77 |

- Both sides improve: as A, 32.8 vs 27.2; as B, 31.1 vs 27.5.
- Tube U-turn deaths drop (far/tube/HitSelf 0.56 → 0.38 per game, king tube HitSelf 0.23 → about 0).

**Weight sweep** (30 seeds = 60 samples each, vs POR_W 8):

| variant | score |
|---|---|
| W5 | 0.38 |
| W12 | 0.58 |
| W16 | 0.53 |
| W24 | 0.55 |
| W16 vs W12 | 0.61 |
| γ 0.80 (vs 0.88) | 0.48 |
| sock pull off | 0.52 (hot eats 150 instead of 208; the base bot already uses the sock once it knows the timers) |

**Expected effect on the ladder.**
- We lose Portals with finals of 20-31 against 21-42. +4.6 mean moves most of those.
- Against the top 25 (winners about 33, Sabotage-d about 46), P1 alone reaches parity with a median winner, not with Sabotage-d.

### P2. One king (POR_ONEKING). TESTED, weak positive; optional.

**Hook:** `portalsOverride()`, which has a side effect and returns false.
- From r400, if `kingSelf` and a fresh (≤8 rounds) king broadcast from another id has `len ≥ myLen+2`, set `kingSelf=false`.
- The dragon then becomes a feeder or merger through `shouldFeed()`: any length from `KING_V2_MERGE_ROUND` 420.

**Why.**
- KING_V2 keeps 2 candidates as ram insurance, and a candidate steps down only if 2 fresh kings are longer (`freshKings(myLen+2) >= 2`), which almost never happens.
- On Portals there are no rams, and our 2nd-longest ends at 23 in local runs (top winners 11, Sabotage-d 10).

**Result, 120 samples vs P1:**
- 32.3 vs 31.2 mean, 0.55.
- The 2nd-longest drops to 14, but the merges lose half the mass (total at the end 61 vs 65).
- Not significant. Try it together with P1 and keep it only if a larger run confirms it.

### P3. Tube-exit collisions with allies: OPEN; the obvious guard is rejected.

With P1, tube traffic doubles, and **an ally stepping onto the exit tile while we are blind inside the tube** becomes the top accidental big-death cause:

| per game, L≥8 | P1 | current bot |
|---|---|---|
| non-king deaths at the exit | 1.52 (16.9 length) | 0.59 |
| king deaths at the exit | 0.82 (11.3 length) | 0.45 |

The colliding ally is usually passing through x: the hit segment index is 1-5, and the ally is L2-8.

Guards tested (120 samples unless noted):
- **No tube entry for L≥8 if an ally head is within 4 of x:** 0.36 vs P1 (29.2 vs 31.7). **Rejected.** Exit deaths only fell from 2.3 to 1.8 per game, and the king lost tube food.
- Ally head within 3 for L≥6 (30 samples): 0.43. Rejected.
- **No tubes at all for L≥8 or L≥10** (30 samples): 0.52 / 0.42. Rejected. Dragons still reach L≥8 inside a tube, since they enter at L5-7 and eat 4.

Ideas not yet tested:
- **(a) Keep splice tiles clear.**
  - The 12 splice tiles per team are the e and x of each tube: A's are (12,13), (13,13), (3,15), (3,14), (8,11), (9,11), (12,5), (13,5), (3,6), (3,7), (8,2), (9,2).
  - Penalty about 4 for stepping onto one unless the next move enters that tube; this cuts passers-by on x.
- **(b) One-way tubes.**
  - Only enter in the canonical direction (the table in §1, e.g. T4 only from (12,5) going E). The exit tile is then never another dragon's entry tile.
  - Costs some pull.
- **(c) Sonar probe before stepping out** (stretch goal).
  - On the last tube tile, ping toward the exit. Sonar passes portals; check the ECHOES ally count before stepping out, and reverse-split (`SPLIT L-2`) if it is blocked.
  - Only reliable where the ray's next edge after x is kelp.

### P4. RP settings: leave as they are (v2: seed 250, split stop 360, feed 300, reserve 3; crowd 3)

Each tested with P1 + P2, 30 samples, vs P1 + P2. All are inside the noise (per-sample sd is 7-10):

| setting | score |
|---|---|
| seed 200 | 0.40 |
| feed start 270 | 0.58 |
| reserve 2 | 0.57 |
| split stop 320 | 0.55 |

Per-game sd of the final is 7-10, so a real +2 needs about 200 samples.

## 5. Integration notes

- The prototype module is `notes/maps/portals_proto.hpp`. It is a drop-in for `bot/maps/portals.hpp` and uses only Bot members. It sets `RP.*` in `porInit()` only when the `POR_KS/SS/FS/RES` macros are ≥0, and they default to -1.
- Recommended defaults: `POR_PULL 1`, `POR_EXIT 1`, **`POR_W 12`**, `POR_G 0.88`, `POR_SOCK_MAXLEN 3`, `POR_ONEKING 0` (or 1 after a confirming run). Leave every other guard at 0.
- `porInit()` only runs once `w.known` is set. Unrecognised split children get no pull until they recognise the map.
- **Cost:** one ≤240-tile BFS per candidate move (4 per turn), which is negligible. I did not check it with `--sandbox`, because the tool refused a prebuilt binary; run it from the source dir before submitting.
- **Validation:**
  - `notes/tools/portals/prun.py NAME binX binY --seeds 60` gives per-side finals.
  - Also run `tools/pool.py` with guard maps, to be sure nothing else changes. Only the Portals branch is affected, since `mapScore`/`mapOverride` dispatch on the map.
