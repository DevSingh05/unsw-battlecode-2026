# 15: Why v16 loses on Default and Trauma (28 Sep 2026)

**Data.** Every v16 game on Default (24: 11 W / 13 L) and Trauma (6: 1 W / 5 L) in `replays/v16`, ranked and unranked. For comparison I used v15 (`replays/v15`: Default 16, Trauma 5) and `replays/ab_base` (Default 15).
- Ranked only: Default 1/5 (the losses are 510732, 507199, 514263, 513624), Trauma 0/3 (512103, 514261, 507201).

**Scripts** (read-only over the replays; all in `notes/tools/v16diag/`):
- `diag.py` builds `games.pkl`.
- `report.py [src=v16] [map=Default]` prints per-game timelines, eats, deaths and crossings.
- `phases.py` gives per-phase aggregates for losses vs wins.
- `layouts.py <dir>` compares replay start lines with the reference map files.
- `tra_king.py GAME` traces Trauma starters and our king in A-frame.
- `bigdeaths.py [minL]` shows how our L≥8 dragons died.
- `portal_follow.py` sorts portal deaths into follow, opposite and standing.
- `newborn_portal.py <dir>` counts the birth-turn portal-neck bug.

**Death categories** (from `sim2` plus the `nbrs` field):
- `ram_enemy`: we moved into an enemy head.
- `rammed_by_enemy`: an enemy moved into our head. Both dragons die either way.
- `ally_body` / `enemy_body` / `self`: the head hit that body.
- `_trapped`: all 4 neighbours were blocked.
- `P`: the fatal step crossed a portal.

---

## TL;DR: loss mechanisms ranked by games cost

| # | mechanism | games it explains | general? |
|---|---|---|---|
| 1 | **Trauma module uses the wrong frame when the server swaps team starts.** It uses the team letter, not the start position. | **All 5 v16 Trauma losses (3 ranked).** Since the module shipped (v13-v16): swapped layout 0-9, standard layout 10-0. | Trauma-specific bug. The underlying cause (start layout swap) is general: it happens on ~half of games on every map. |
| 2 | **Default endgame collapse.** Splits stop at r350 and the team is fed down to 4 reserves while the opponent keeps splitting. Our 1-5 big dragons then get rammed by L2-3 kamikazes, or the team is eliminated. | **5 of 13 Default losses** (1 ranked: 513624) were even or ahead at r300 | general |
| 3 | **Self-inflicted portal deaths** keep our Default swarm from growing. About 1.1-1.4 non-ram deaths per 100 dragon-rounds, against 0.16-0.8 for opponents (7× in r0-100). It includes a clear **bug**: split children born straddling a portal step back into their own neck on their first turn (8.9/game on Default, 63/game on Portals). | Main driver of the 8 early swarm-race losses (3 ranked), together with #4 | general (any map with portals) |
| 4 | **Early swarm race lost to strong swarm teams.** By r150-200 we are at 3-9 units against 23-35. Ram trades are even; they out-split and out-eat us from r100. | 8 of 13 Default losses (510732, 507199, 514263 ranked) | general, mostly opponent strength |
| 5 | POCKET_PUMP (v16's change) | **0 games.** It does nothing measurable on Default (same as v15). On Trauma it adds churn only in games already lost to #1. | n/a |

---

## 1. Trauma: the module runs in the wrong frame on the swapped layout

### What the replays show
- The server's Trauma map text puts team 0 at (4,15)/(4,2) in some games (the "standard" layout, same as `notes/maps/Trauma__id15.map`). In other games team 1 is there (the "TEAMSWAP" layout). `layouts.py` finds the same swap on Default, Devil, Portals, Schooltime, Trophy and QoS, in roughly half of all games.
- `bot/maps/trauma.hpp:109` `traInit()` sets `traIsB = w.myTeam == 'B'`. On the swapped layout the A-frame is therefore mirrored: the module's pen, factory and king tile are the **enemy's**. As a result:
  - The pen king is never declared: `A(myHead)` is never (4,15).
  - Both starters split at r0.
  - The scripted factory never runs.
  - `facBorn` feeders never exist.
  - `PM_TRA_KS = 450` stops any generic king until r450.
- `identifyByStart()` (`bot/main.cpp` ~563) also requires `team == myTeam`, so on a swap the map is only identified later, from edges.

| src | game | opp | R? | layout | res | our/their max at r100 r200 r300 r400 r500 | total r500 | units r300 | our first L≥8 |
|---|---|---|---|---|---|---|---|---|---|
| v16 | 512103 | Drago et al | R | SWAP | L | 3/3 3/3 3/3 7/7 11/26 | 64/62 | 42/51 | r460 |
| v16 | 514261 | Quaker Qubits | R | SWAP | L | 4/3 4/9 4/17 7/31 17/35 | 123/35 | 59/9 | r404 |
| v16 | 507201 | python.io | R | SWAP | L | 3/3 4/3 4/3 6/10 15/20 | **131/20** | 62/7 | r264 |
| v16 | 508515 | ComTamSuonNuong | u | SWAP | L | 4/5 4/6 3/8 7/8 15/18 | 94/97 | 41/58 | r419 |
| v16 | 507943 | Bhole Chature | u | SWAP | L | 3/4 4/4 4/4 10/3 13/14 | 91/31 | 50/24 | r383 |
| v16 | 510146 | y | u | std | **W** | 7/8 16/24 25/42 33/10 20/17 | 160/19 | 50/14 | **r24** |
| v15 | 476433, 468339, 465089 | | | SWAP | L L L | our max 3-4 until r300 | | | r409-never |
| v15 | 471718, 491354 | | | std | W W | 7-8 at r100, 26/20 at r300 | | | r23-24 |
| v13 | 440161 | | | SWAP | L | | | | |
| v13 | 438340-438435 (6), 446532 | | | std | 7 W | | | | |

- In every swapped game **we out-harvest the opponent**. Totals at r500: 131 v 20, 123 v 35, 91 v 31. Eats per game: 909 v 293, 985 v 50.
- But our longest dragon stays at 3-4 until r400. Units sit at the 64 cap, so the length is spread over ~60 small dragons, and we lose on the longest dragon by 1-24.
- With the right frame the plan works: king L7-8 at r100, 16-19 at r200, and 10-0 so far.

### Is the Trauma plan beaten by real opponents? No.
- Enemy heads inside our pen: 0 head-rounds in 510146, 471718 and 491354.
- No king was killed by an enemy. The one pen-king loss was self-inflicted: 510146 r479, L33 king in the pen corner (47,0), boxed in by kelp on N/E, its own body on W, and an ally L11's body on S (`ally_body_trapped`). The final score was 20 v 17, so it nearly cost the game.
- Minor follow-up: TRA_KDEPTH is already in code, default 0. Test it at 20, plus a pen-crowding cap (no second L≥6 dragon within 3 of the king).

### Fix
1. **`TRA_FRAME_BY_POS`** in `bot/maps/trauma.hpp` `traInit()`:
   - For a starter (round 0, `myId < 4`): `traIsB = (myHead x >= 24)`. Our starts are at x=4 for the left side and x=43 for the right.
   - For a split child, use its birth tile: A-frame x ≤ 12 means the left team, x ≥ 35 the right. Pens are never invaded, and the factory is 1-wide per side. This covers every child the module scripts: the rusher, the factory cycle and the feeders.
   - For maze-born children, send the frame bit by sonar at split time. Send the parent's sonar opposite to its facing: it leaves from the tail, and the next tile is the child's head, which acts later the same round. Or keep the team letter XOR a `w.startSwapped` bit carried in the existing checksummed king message.
2. **`MAP_ID_TEAMSWAP`** in `bot/main.cpp` `identifyByStart()` (~line 563):
   - Also accept a start that matches the *other* team's entry in `KNOWN_MAPS[c].dragons`.
   - Set `w.startSwapped = true`.
   - Map modules should use `w.startSwapped ^ (w.myTeam=='B')` for any side-specific frame.
   - The same bug is in `bot/maps/queen_of_spades.hpp:117`: the opener picks `myId == (myTeam=='A' ? 0 : 1)`, and on a swap that id belongs to the enemy.
   - Checking the other modules: Schooltime, Portals and Slithery use `myTeam` only for ally/enemy tests, so they are unaffected.
- Expected effect: Trauma goes from ~50% to ~100% on this evidence (10-0 in standard layout). That is about +0.5 win per Trauma game, or roughly +0.05 wins per ranked game (1 map in 10).
- It is a map-specific fix, but `MAP_ID_TEAMSWAP` hardens every future hand-scripted module.

---

## 2. Default: the numbers

### Timelines (means; eliminated games count as 0 after the end)

| | r100 units | r200 | r300 | r400 | r500 | total r200 | total r400 | max r400 | max r500 |
|---|---|---|---|---|---|---|---|---|---|
| **losses (13)** us / them | 12.2 / 15.2 | 12.5 / 26.8 | 10.8 / 34.7 | 3.1 / 36.8 | 0.7 / 29.8 | 31 / 66 | 18 / 110 | 7.0 / 7.2 | 7.5 / 15.2 |
| **wins (11)** us / them | 20.2 / 8.5 | 31.5 / 7.8 | 32.7 / 7.3 | 23.6 / 6.7 | 18.8 / 3.8 | 76 / 20 | 80 / 24 | 7.5 / 4.4 | 18.5 / 9.5 |

- How the games ended: losses were 8 eliminations (r190-r489) and 5 on longest at r500 (23v26, 43v52, 15v23, 4v20, 12v17). Wins were 5 eliminations and 6 on length.
- Default wins and losses are decided by the swarm race. In losses we trail by r100-200; in wins the opponent was already small (≤8 units at r200). Whoever has more heads at r200 wins almost every time.
- v15 (16 games) and `ab_base` (15 games) have near-identical Default profiles:
  - v15 losses have 12.0/16.3/13.0 units at r100/200/300; v16 losses have 12.2/12.5/10.8.
  - Portal crossings: 359 and 356 per game in those losses, 320 for v16.
  - **v16 did not change Default.**

### Per-dragon rates, losses, r0-100 (per 100 dragon-rounds; `phases.py` + inline)

| | eats | splits | non-ram deaths | ram deaths |
|---|---|---|---|---|
| us | **6.1** | 2.8 | **1.12** (almost all through portals) | 0.82 |
| them | 4.4 | 2.0 | **0.16** | 0.77 |

- Per dragon we eat and split *more* than they do. We still fall behind because we kill ~7× more of our own dragons.
- In r100-200 our non-ram rate is 1.16 against 0.55. Our net growth drops to ~0 while theirs stays at ~0.6.
- Deaths per game in losses, r0-100: us 18.2, them 9.3. Of ours, 10.9 are portal deaths: 5.7 ally-body, 2.2 self, 1.2 enemy-body. Ram trades are even at 3.9 vs 3.8.

### Our death causes, Default, per game (v16)

| r0-200 non-ram deaths | losses | wins |
|---|---|---|
| ally body, through a portal | 15.2 | 26.7 |
| self, through a portal (≈ the newborn bug below) | 4.3 | 5.4 |
| enemy body, through a portal | 2.2 | 1.8 |
| trapped (self/ally) | 2.2 | 6.6 |
| ally head-on | 1.4 | 3.4 |

All portal deaths on Default, 24 games (`portal_follow.py`), per game:

| cause | per game |
|---|---|
| total | 67.5 |
| hit an ally whose **neck** is on the blind exit tile (the ally is walking past the exit, not crossing) | 21.2 + 2.5 |
| **HitSelf** (newborn bug) | 9.5 |
| head-on | 7.6 |
| followed an ally through the same portal | 11.8 |
| opposite-direction traffic | 10.2 |
| enemy body | 4.7 |

### The newborn portal-neck bug

**What happens.** When a dragon splits while its tail segment and the one before it straddle a portal, the child's head is on one side and its neck on the other. The child is a fresh process. `updateTrail()` (`bot/main.cpp` ~1247) rebuilds the body only from *visible* segments, so the neck is invisible and `trail = [head]`. The portal step back into the neck looks free, and the child takes it and dies HitSelf **on its birth turn**.
- 99% of these deaths are age-0 children of length 2 moving into `body[1]` with 2-3 free exits available.
- Example: 510732 r36, child at (24,7), neck (4,4) through the (24,8)↔(4,4) portal, moves S and dies.

`newborn_portal.py`, deaths per game:

| map | v16 | v15 | opponents |
|---|---|---|---|
| Default | 8.9 | 11.2 | 0.1-0.5 |
| **Portals** | **63.2** | 57.1 | 6-12 |
| Schooltime | 5.0 | 4.2 | |
| Slithery | 4.0 | 3.3 | |
| Trophy | 1.1 | 0.8 | |
| Trauma | 1.0 | 0.8 | |

**Fixes:**
- **`NEWBORN_NECK_GUARD`**, in `updateTrail()` after the rebuild. If `trail.size() < 2 && myLen >= 2`, append `step(myHead, (myDir+2)%4)`. That is where the engine's facing says the neck is; if in doubt, mark every portal-crossing neighbour of the head as occupied (`freeT = myLen`).
- **`SPLIT_NO_STRADDLE`** (parent side), in the split branch (`bot/main.cpp` ~1986), the trapped reverse split (~2096) and the pump split. Refuse the split when the new child's head and neck, `trail[L-1]` and `trail[L-2]`, are not plain-adjacent.
- Both are pure bug fixes with no downside. Expected gain: about +9 units/game on Default in r0-330, compounding. On Portals it saves around 60 deaths/game. Check first that this isn't a deliberate Portals-module behaviour; it doesn't look like one.

### Blind exits (the other ~50 portal deaths/game)
- The victim cannot see the exit.
- The obstacle is usually an ally loitering near the exit inside Default's 4-wide kelp-walled centre rooms. Only ~12/game are "followed an ally in", which would have been visible.
- PORTAL_ALLY_COST was already rejected (notes/14, journal 16:45).
- Candidate, **experimental**: **`PORTAL_PROBE`**. When the chosen move crosses a portal and no threat forces it, send a *single* sonar ray that turn in the crossing direction, and take the best non-portal move instead. The ray passes through portals. Next turn, cross only if the echo shows no ally or enemy hit, meaning the ray reached kelp or nothing.
  - On Default the exit side is a small walled room, so "no hit" really means empty.
  - It costs 1 turn per crossing and only makes sense where the bot crosses far more than opponents (us 320-500 per game, them 90-200). Test it as a mechanism first (deaths per crossing).
- Also cheap and general, **`PORTAL_FOLLOW_GUARD`**: don't cross a portal edge that an ally segment was seen entering within the last `allyLen+1` rounds. That ally's body is still trailing out of the exit. It covers ~12/game.

---

## 3. Default endgame: consolidating into a swarm that keeps splitting

These 5 losses were **even or ahead at r300-330**:

| game | r330 units us/them, total | r400 units, total, max | r450 units | how it ended |
|---|---|---|---|---|
| 508508 | 29/8, T69/20 | 17/17, 83/39, 12/4 | 3/27 | Lost L13, 10, 9, 10, 15 and 21 to enemy L2-3 rams (enemy head 1-2 away the round before); eliminated r489 |
| 506742 | 27/15, 63/36 | 9/19, 51/52, 12/5 | 5/8 | L13 rammed r464 by an L5 sprint EEES; lost 23 v 26 |
| 506754 | 24/26, 58/63 | 3/42, 19/101 | 0 | eliminated r411 |
| 506775 | 11/26 | 3/32, 35/89, 17/6 | 1/19 | king L17 hit an enemy body through a portal (r406); lost 15 v 23 |
| 513624 (R) | 14/19 | 4/33, 25/86, 15/6 | 2/20 | king L15 rammed r403 by an L4 (enemy head 5 away); lost 12 v 17 |

- **We stop replacing units.** Splits in r330-420 are 5.4/game for us and 24.2/game for them (losses). Only 0.3 more for us after r420.
  - `SPLIT_STOP_ROUND` is 350 and `FEED_RESERVE` is 4. Normal attrition keeps running: portal self-kills and 1-for-1 rams.
  - So the team drops from 11-29 units to 1-5 by r400-450, while the opponent holds 17-42.
- **Our big dragons die to rams.** 9 of 11 L≥8 deaths in these losses were enemy head-ons, mostly by L2-3 dragons whose head was 1-2 tiles away the round before (`bigdeaths.py`).
  - In wins the same consolidation is harmless, because the opponent had ≤8 units.
- Feeding is not the main drain: late `self` deaths in losses are only 1.0/game in r330-420. Portal/ally collisions and rams are.

**Fixes (general):**
- **`SPLIT_STOP_ADAPT`**, at `bot/main.cpp` ~1987 (`round < RP.splitStopRound`).
  - After `splitStopRound`, a non-king dragon still does the L4 → 2+2 split when the team is outnumbered.
  - Use `units < ENEMY_EST` (see below), capped at `round < 460`.
- **`FEED_RESERVE_ADAPT`**, in `shouldFeed()` (~1547/1550). Use `reserve = max(RP.feedReserve, ENEMY_EST/2)`, so we don't feed down to 4 into a 30-unit enemy.
- **`ENEMY_EST`.** A per-dragon estimate of the enemy count: the maximum distinct enemy head ids seen in the last 30 rounds, times (map tiles / tiles seen). Or simply the `ECHOES enemy_head` rate. A coarse "many / few" bit is enough.
- **`KING_SWARM_KEEP`**, in the KING_V2 keep-distance block (~2036). When `ENEMY_EST` is high, raise the king's keep distance from enemy heads to `3 + 1` per sprint step available to them (reach ≈ enemy len−1), and treat enemy **tails** of L≥4 as heads (TAIL_THREAT for all kings, not just the last 3).
- Expected effect: 2-3 of those 5 games flip (508508, 506742 and 506754 were won or level positions at r330).
- The risk is king length vs weak opponents. Consolidation starts later, but in wins our r500 max was 18.5 against 9.5, so there is margin.
- **Test on the server.** Self-play can't show this, because v16 vs v16 both stop splitting. Use unranked A/B on Default against the swarm teams that beat us (PPP, python.io, Quaker Qubits, y, Heartbreaker, w daniel ma, ComTamSuonNuong).

---

## 4. Default early swarm race (8 losses: 510732, 507199, 514263, 506794, 510235, 506757, 506788, 506769)

- r150 units: 3-9 v 23-35 in the fast collapses (506794, 507199, 510732, 510235, 506788, 506757), and 14-22 v 19-26 in the slow ones.
- Rams are traded evenly (sums match on both sides). In the fast collapses our r0-150 ram deaths are 17-25, against 9-16 in the slower games. Strong opponents trade early and win the corpse race by having more heads nearby.
- Our r100-200 eats are 77/game against their 101.
- The only mechanical gap we control is our own non-ram death rate: the portal issues in section 2. RAM_MIN_UNITS=8 is already in v16.
- Beyond that, these opponents are just stronger swarms, and there is no single flag to fix it.

## 5. POCKET_PUMP (v16's change): not the cause

- **Default.**
  - Splits with ≤1 exit: v15 31.2/game, v16 29.5/game.
  - Children dead within 3 rounds: 5.5 vs 5.1.
  - Trapped deaths: 17.6 vs 14.1.
  - No change; Default has no kelp pockets.
- **Trauma.** v16 raises churn: trapped deaths 216 → 289/game, splits 277 → 365. That happens because the generic pump dives into our own real factory while the scripted factory is off (wrong frame). It gives HitSelf deaths at the dead end instead of HitWall: 41-54/game at our factory. The dragons are not wasted: we still out-eat the enemy by 3×. The length just never consolidates, because of bug #1.

---

## Proposed flags, in order of priority

1. `TRA_FRAME_BY_POS` (`bot/maps/trauma.hpp` `traInit`) + `MAP_ID_TEAMSWAP` (`bot/main.cpp` `identifyByStart`, ~563; also `bot/maps/queen_of_spades.hpp:117`).
   - Fixes all Trauma losses.
   - Test locally by editing a copy of `maps/trauma.map` with the DRAGON team fields swapped, then check that the king forms by r100 on both sides.
2. `NEWBORN_NECK_GUARD` (`updateTrail`, ~1247) + `SPLIT_NO_STRADDLE` (split branches ~1986, ~2096, pump split).
   - A bug fix on every portal map.
   - Mechanism check: `newborn_portal.py` on local replays should drop to ~0. Default units at r200 should go up.
3. `SPLIT_STOP_ADAPT` + `FEED_RESERVE_ADAPT` + `KING_SWARM_KEEP` (with `ENEMY_EST`).
   - Default endgame against swarms.
   - Server A/B only.
4. `PORTAL_FOLLOW_GUARD` (cheap), then `PORTAL_PROBE` (experimental).
   - Blind-exit ally collisions, ~50/game on Default.
5. Trauma polish: `TRA_KDEPTH=20` and a pen-crowding cap near the king (510146, L33 king trapped by an ally at r479).
