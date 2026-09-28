# 10: v7 on its weak maps (Schooltime, Queen Of Spades, Trauma, Prisoners Dilemma)

Data: all v7 games in `replays/v7` on these maps (ranked and unranked). Schooltime 6-7, QoS 7-6, Trauma 12-4 (2-3 ranked), Prisoners Dilemma 10-5.
All numbers are **per-game means** unless marked. "L" = our losses, "W" = our wins, "them" = the opponent in those games.

Tools:
- `notes/tools/weakmap_diag.py`: builds `replays/v7/weakmap.pkl`, about 2 minutes, single process.
- `notes/tools/weakmap_report.py <map...>`: prints the tables below.
- One-off probes were run from the scratchpad: portal-adjacent deaths, pocket raids, king sonar delivery, and the geometry of enemy rams on our big dragons.

Definitions:
- **ram**: head-to-head where we moved. **rammed**: an enemy moved into our head.
- **self_neck**: moved into our own neck. For small dragons this means trapped. For L≥10 after r330 it is usually a feed suicide.
- **stub**: a split child that dies within 3 rounds.
- **pocket**: a dead-end tile, found by iteratively pruning tiles with ≤1 open neighbour.
- **feed**: a death into our own neck, kelp or no-action at r≥200, within 5 tiles of a longer own dragon of L≥8.

**Main finding:** on every one of these maps our behaviour is almost the same in wins and losses. The result is set by how strong the opponent is, plus a few single events that decide the game. The fixes below raise our ceiling rather than "do what we did in wins".

---

## Prisoners Dilemma (10-5)

| round | 25 | 100 | 200 | 300 | 400 | 499 |
|---|---|---|---|---|---|---|
| units us / them, L | 7 / 4.4 | 6.6 / 5 | 9.2 / 8 | 10.8 / 8.5 | 8.3 / 8.3 | 4 / 9.3 |
| longest us / them, L | 2.8 / **9.2** | 3.0 / 9.8 | 3.0 / 9.2 | 2.8 / 10.8 | 8.3 / 13.7 | 12 / 13 |
| longest us / them, W | 3.1 / 6.2 | 3.0 / 6.2 | 3.2 / 6.9 | 3.0 / 9.0 | 9.7 / 10.0 | 20 / 9.7 |

**Harvest (L).**
- We eat 133 pearls per game (4 hot); they eat 405 (**125 hot**).
- Their pocket "pump" makes 359 pocket eats and 162 pocket deaths per game. Each death comes right after a split: eat, split, the head dies, and the corpse is eaten.
- They make **80 feeds per game, 99% eaten by their king**. We make 2.6.

**Deaths (L).** Few, and not what decides these games: self_neck 27.8, ally body 15.4, rams 3.0 / 3.6.

### Mechanisms
1. **We shred the starting length-11 dragon.** Each team starts with an L11 dragon whose head is in the hot tunnel (A at (14,2), B at (17,13)).
   - We split it on rounds 0-5 (12→9→7→4…), so our longest is ≤3 until r350.
   - The factory opponents (okbro, Gavin Min, JJYA, goblin gooners) keep a 13-14 dragon all game. It eats the hot tiles and splits off a 2-long piece every 2 rounds, which is fed back to it.
   - In 9 of 15 games **our 7 dragons ate 5 pearls in the first 100 rounds**; the factory side ate about 100.
   - The three round-500 losses were decided by 1-2 length: **401433 12 v 13, 380708 11 v 13, 367694 13 v 13** (lost on total, 44 v 59). Our PD wins against the same factory bots were just as close: 399541 15 v 13, 380698 20 v 13.
2. **No hot harvest at all:** 4-5 hot eats per game against 36-125. This follows from (1): the only dragon standing in the tunnel is cut up.
3. **Early suicide rams (1 game).** 354504: 8 of our rams by r100 left us with 1 unit at r80, and we were eliminated at r290. The ram guard lets a ram through when `theirs >= myLen+2`.

### Proposed changes
- **(P1) Keep the starter, and make it a factory.**
  - Add `RP.keepLen` (default 1000; **PD = 8**).
  - In `decide()`: `bool bigLate = (...existing...) || myLen >= RP.keepLen;`
  - Then allow a normal `SPLIT 2` from a keeper only when `myLen >= RP.keepLen + 4`, so it pumps out 2-long units while staying ≥10.
  - A cheaper first test is `PM_DIL_KS=0`. But with it, the 2%-per-turn `kingSelf` declaration fires from round 0 on small dragons and stops their splitting, so `keepLen` is cleaner.
  - Expected: our longest ≥11 from r0 instead of 3. That flips most of the 3 close round-limit losses (about +2-3 wins per 15).
- **(P2)** With P1, try `PM_DIL_FS=300`, so feeders feed the starter-king.

## Queen Of Spades (7-6)

| round | 25 | 50 | 100 | 150 | 200 | 300 | 400 |
|---|---|---|---|---|---|---|---|
| units us / them, L | 3.8 / 3.7 | 4.5 / 7.7 | 4.5 / **12.7** | 3.8 / 16.3 | 4.6 / 18.4 | 7.0 / 21.8 | 3.5 / 17 |
| units us / them, W | 4.7 / 3.3 | 6.4 / 4.9 | 7.5 / 8.2 | 9.2 / 11.8 | 10.3 / 13.7 | 15.4 / 16.8 | 10.8 / 14.2 |

- 5 of 6 losses were eliminations (r157-495).
- Eats per dragon-round are higher for us than for them (0.156 vs 0.078 in rounds 0-100). **We don't lack food. We lose units.**

### Mechanisms
1. **Early attrition from our own mistakes.**
   - By r150 in the losses we have split 25-41 times and eaten 59-98 pearls, about the same as the opponent. But **20-34 of our dragons have died HitSelf or on an ally's body**, so we have 2-5 units against their 10-24.
   - Over the whole game in losses: self_neck 39.2, ally body 18.7. **Stubs: 27 of 84 splits (32%)**, against 20% for them.
2. **Raids into the "spade" pockets lose length.** The 16 depth-1 pockets (the `|o|` tiles at y 1-3 and 31-33) plus the wrap row are where the deaths cluster: cells (8-11, 32-35) 109, (16-19, 0-3) 107, (12-15, 0-3) 81 deaths over 6 losses.
   - Per loss: 11.3 pocket eats (**9.7 of them corpse bait** left by the previous victim) against 11.7 pocket deaths costing 30 length. That is **net -19 length per game**. 6.5 of those deaths come right after an ESCAPE_SPLIT.
   - `surviveDepth()` treats "eat to 4, then split" as a safe escape (`escapes()`). The head half is still stuck in the pocket and dies. On a non-hot pocket this is a pure loss.
3. **A late king ram decided a game.** 397225 (ranked): our L26 king was rammed at **r484** by an L2 enemy standing next to it at (22,5), and we lost 14 v 16. 391117 r495: L14 king rammed by L4.

### Proposed changes
- **(Q1) ESCAPE_SPLIT only for hot pearls.** In `surviveDepth()`, count an escape only if the eaten tile had `gmin==gmax==1` (or add a per-map `RP.escapeSplit`, off on QoS and Schooltime).
  - Leave it on for Trauma: its hot pockets are net positive, with 175 pocket eats against 126 length lost.
- **(Q2)** Per-map `SPLIT_NEEDS_EXIT=1` on QoS only. It was rejected globally (0.446), but the QoS stub rate is 32%.
- **(Q3)** King anti-ram; see **K1** below.

## Trauma (12-4; ranked 2-3)

| round | 100 | 150 | 200 | 300 | 350 | 400 | 450 | 499 |
|---|---|---|---|---|---|---|---|---|
| units us / them, L | 9.5 / 4.8 | 20.8 / 8.2 | 32 / 16 | 40.8 / 14.2 | 39.2 / 15 | 28.2 / 12.8 | 25.8 / 4.5 | **19 / 3.2** |
| longest us / them, L | 3.2 / 5.0 | 3.5 / **7.2** | 3.5 / 8.8 | **4.0 / 11.0** | 7.2 / 12.8 | 9.2 / 14 | 11.5 / 19 | 13 / 21.5 |
| longest us / them, W | 3.2 / 3.3 | 3.6 / 3.2 | 3.6 / 3.6 | 4.2 / 4.1 | 6.5 / 5.9 | 13.8 / 7.5 | 18 / 10.4 | 21.1 / 12.3 |

- Harvest in losses: we eat 629 pearls (48 hot) against 219 (0 hot). We out-eat them 3:1.
- Feeding: 5.8 feeds per loss (8 pearls dropped, 3 reach the king) against 10.7 per win (19 dropped, 9 to the king).
- Big-dragon deaths are rare (0.2 per loss).

### Mechanisms
1. **We never consolidate.** In 3 of 4 losses we finished with **21 / 24 / 26 units and total length 110 / 106 / 83**, against the opponent's 38 / 29 / 28. Our king was **19 / 9 / 8 against 30 / 29 / 9**. Feeds in those games: 15 / 3 / 1.
   - 355732 (ranked, ANON_TOKYO): lost **8 v 9** with 26 dragons alive. Our longest dragon sent only 48 king pings after r300: it was never the king. A randomly declared short `kingSelf` held the crown, and no one was 2 shorter than it, so nobody fed.
   - Our longest is ≤4 until r300 (seed round 275). The winners in notes/08 have ≥10 by r307.
2. **King sonar dies on kelp.** 75-80% of the king's pings after r300 hit kelp on this maze, so few allies hear the king. Feeding also needs the king in view, 2-4 tiles away.
3. **A late king ram.** 397223 (ranked, NP hard): L19 king rammed at **r478** by an L4 that sprinted WSS from (28,10) to (27,12). We lost **16 v 18**.

### Proposed changes
- **(T1) Params.** `PM_TRA_KS 275→200`, `PM_TRA_FS 330→300`, `PM_TRA_SS 350→325`. These are the notes/08 values; FS and SS were never tested.
- **(T2) Code, in `updateKingship()`.** Only declare `kingSelf` if `myLen >= 4`. On hearing a king, compare `kingLen > myLen` (not `+2`) so the longest takes over.
- **(T3) Code: end-game all-in.** From `round >= 470`, `shouldFeed()` drops `units > FEED_RESERVE`, and the feed trigger in `decide()` allows `dk <= 6`. Make `KING_RELAY_HOPS` per-map (6 on Trauma and Schooltime).
  - Expected: 2-3 of the 4 losses were short of the win by less than their idle length.

## Schooltime (6-7)

| round | 100 | 150 | 200 | 250 | 300 | 350 | 400 | 450 | 499 |
|---|---|---|---|---|---|---|---|---|---|
| units us / them, L | 44 / 17 | 54 / 29 | 56 / 33 | 55 / 39 | 55 / 43 | 51 / 45 | 17 / 44 | 13 / 28 | 8.5 / 20 |
| longest us / them, L | 3.7 / 7 | 7.3 / 11 | 18 / 11.7 | **19.7** / 14.6 | **13.6** / 16.1 | 15.7 / 20.4 | 19.9 / 24.3 | 27.5 / 30.2 | **30.2 / 43.5** |
| longest us / them, W | 3.8 / 3.5 | 5.5 / 3.3 | 11.2 / 8 | 15.7 / 4.2 | 18.8 / 7.7 | 23 / 6.3 | 24.5 / 9.2 | 28.8 / 14.5 | 41.2 / 19.7 |

**Harvest.** We eat 1785 pearls per game (885 spawn, 796 own corpses); they eat 904. We have **no hot tiles** on this map.

**Deaths per loss, us:**
- rams 65.7, rammed 24.3
- ally body 179
- self_neck 189, self-trapped 7.9
- feed 11.7
- stubs 80 of 494 splits

This is the same in wins. Our churn is huge but not what differentiates.

**Big dragons are the leak.**
- L≥10 deaths per loss: **20.0, costing 334 length**, of which 6.1 were the current king (139 length), and 6.4 were before r300.
- In wins: 16.3 deaths (273 length), 3.3 kings.
- The opponent in our losses loses only 7.0 (120 length).
- Causes, per loss (length lost in brackets): self_neck 6.9 (108; about 3.9 of these are deliberate big feeds after r330), ally body 5.4 (96), self-trapped 3.4 (60), enemy ram 3.0 (46).

**Feeding.** 11.7 feeds per loss dropping 28 pearls: the king gets 9, other allies 16, the enemy 2.

### Mechanisms
1. **Big dragons die at portals on ally bodies.**
   - About 8% of tiles are within 1 of a portal, yet **9.6 of our 27.3 deaths per game at L≥8 happen there**, 6.1 of them by hitting an ally's body. Vision doesn't pass through portals, so the far side is blind.
   - Clusters: (19-20,19), (39-40,19), (1-2,11), (57-58,11), (1,21).
   - Examples:
     - **402409 r294: an L66 king hit an L4 ally's body** at (22,23). Our longest fell from 59 at r250 to 15 at r300, and we lost 35 v 37.
     - 380694 r484: L37 at (20,19) on an ally body, then r496 L38 self-trapped at (20,19). Final 26 v 84.
2. **Kings live in the maze band (y 8-20).**
   - 76% of big deaths happen there (self-trapped, or boxed in by our own 50+ swarm).
   - For rounds ≥200 with L≥10, our king is in the maze in **51% of rounds in losses** against 35% in wins; the opponents' kings are there 15% of the time.
   - 380694 alone lost about 50 L≥10 dragons: r233 L32 self-trapped at (14,38), r452 L32.
3. **Enemy rams on big dragons.**
   - Over the 4 maps, 61 of our L≥8 dragons were rammed. 60 came from a **visible** enemy head at Chebyshev distance 1-3, with no portal. 37 were sprints; the ramming enemies were L2-6.
   - 387620 (Akatsuki) alone had 13 from r311 on. Example: r473 L28 at (37,22), rammed by an L3 after a 6-step sprint.

### Proposed changes
- **(S1) Big dragons near portals.**
  - Make `KING_PORTAL_PENALTY` a runtime param and set it to about 100 on Schooltime only. The global 40 was neutral, 0.49.
  - Also extend `PORTAL_WARN` so any of our dragons with a **body segment** on a portal-exit tile warns, not just heads that are about to exit.
- **(S2) Code: allies yield to the king.** In the `decide()` scoring loop, for non-feeding dragons with `myLen < 8`: `score -= 40` for each visible allied head with `enemyVisibleLength(id) >= 10` (the helper counts any id) and `wrapDist(o.tile, t) <= 1`.
- **(S3) Code: kings avoid corridors (per-map flag, Schooltime).**
  - Precompute each tile's open degree from the known map.
  - For `myLen >= 10`, `score -= 1.5*myLen` if `deg(t) <= 2`, and use `need = 2*myLen` in the area term.
  - Try per-map `KING_SURVIVE_DEPTH=24` here too.

---

## Cross-map: K1, the king anti-ram (all maps)
In `decide()`, for `myLen >= 10`:
- the threat penalty becomes `100 + 8*myLen`, instead of `25 + 4*myLen`;
- add a buffer term: `-(20 + myLen)` for each visible enemy head with `wrapDist(head, t) <= reach+1`.

The evidence:
- The 61 visible rams above.
- Two ranked losses were decided by one late ram (397225 QoS r484 L26, 397223 Trauma r478 L19).
- Schooltime loses 3.0 L≥10 dragons per game to rams.
- `tryRam()` already refuses rams for kings, so this only changes movement.

## Ranked changes

| # | change | where | evidence | expected |
|---|---|---|---|---|
| 1 | P1 keep the L11 starter (+ factory split) | PD `RP.keepLen=8` | longest 3 vs 9-14 for 350 rounds; 3 losses by ≤2 length | +2-3 wins/15 PD |
| 2 | T1+T2+T3 Trauma consolidation | Trauma params + `updateKingship` / `shouldFeed` | 3/4 losses held 3x the opponent's total length, king 8-19 | +2 wins/16 Trauma, likely also Slithery |
| 3 | K1 king anti-ram | `decide()` all maps | 61 visible rams on L≥8; 2 ranked games lost to one ram | +1 game per ~20 on growth maps |
| 4 | S1 king portal penalty + body warns | Schooltime | 35% of big deaths at portal tiles; L66 king 402409 | +1-2 wins/13 Schooltime |
| 5 | Q1 ESCAPE_SPLIT only on hot pearls | `surviveDepth()` | pocket raids -19 len/g QoS, -44 len/g Schooltime; +49 on Trauma, kept | QoS unit survival |
| 6 | S2 yield to king, S3 corridor avoidance | `decide()` | 5.4 ally-body + 10 trapped big deaths/g Schooltime | Schooltime king +10 |
| 7 | Q2 SPLIT_NEEDS_EXIT on QoS | params | 32% child stubs vs 20% | uncertain |

Test each one alone with `tools/arena.py --maps <map>` against v7 (one batch at a time, `--jobs` ≤ 8).
