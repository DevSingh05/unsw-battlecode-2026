# 11 - How current top-10 teams build the king (Schooltime, Portals, Slithery, QoS)

**Question:** against teams rated ≥1730 we lose these maps on longest dragon at round 500. How do the current top-10 build a king that wins?

## Data and tools
- 44 games played 2026-09-27, 11 per map. Each game was **won by a team currently in the top 10** (leaderboard of 27 Sep: 龙虎豹, Vibing++, 中国必须人能飞, Sabotage-d, SSS, SHINK, Team SKKU, Sponge, bread first search, calc), against an opponent rated ≥1860, which is roughly the top 25.
  - Each (A,B) pairing is used once, and each winner at most 3 times per map.
  - Winners in the sample: Sabotage-d 11, SSS 8, Team SKKU 8, Vibing++ 5, 中国人能飞 5, Sponge 2, 龙虎豹 2, calc 1, SHINK 1, bread first search 1.
- Round-limit games: Schooltime 8/11 (3 eliminations), Portals 11/11, Slithery 11/11, QoS 4/11 (7 eliminations by round 150-276). **All king statistics below use the round-limit games only.**
- Files:
  - Replays and caches: `notes/replays/kings/*.replay`, plus `index.json` and `kings_metrics.json`.
  - `notes/tools/kings_fetch.py`: lists games (GET only, 1.2 s apart) and downloads them.
  - `kings_analyze.py`: per-game metrics.
  - `kings_report.py`: per-game dump.
  - `kings_agg.py`: per-map aggregates.
  - `kings_sonar.py`: sonar bit test and king U-turn context.
  - `kings_thresh.py`: rounds at which the king reaches length 6/10/20/30.
- Definitions:
  - **king lineage:** the winner's longest dragon at the end, traced backwards through splits in which the child took the larger part. Such a split is a reverse split (U-turn), which gives the body a new ID.
  - **feeder:** a winner dragon whose corpse pearls were eaten by the king lineage.
  - **rich tile:** spawn gap max ≤ 50 (Schooltime gap-20 tiles, Portals 1-10 and 1-1, Slithery 1-1/1-5/1-10, QoS 1-50).
  - Pearl gaps come from `notes/maps/*.map`, because replay maps have the gaps zeroed.

## 1. King growth curve (medians over round-limit games)

| map / series | r100 | 150 | 200 | 250 | 300 | 350 | 400 | 450 | 499 |
|---|---|---|---|---|---|---|---|---|---|
| **Schooltime**: winner longest | 4 | 8 | 10 | 10 | 13 | 25.5 | 30 | 43.5 | **56.5** |
| Schooltime: final-king lineage | 0 | 2 | 3 | 4.5 | 8.5 | 19 | 30 | 43.5 | 56.5 |
| Schooltime: loser longest | 3.5 | 3.5 | 4 | 4 | 4 | 6.5 | 12 | 24 | 30.5 |
| **Portals**: winner longest | 5 | 4 | 4 | 4 | 6 | 13 | 24 | 36 | **41** |
| Portals: final-king lineage | 0 | 0 | 0 | 0 | 6 | 8 | 24 | 36 | 41 |
| Portals: loser longest | 4 | 4 | 4 | 5 | 8 | 11 | 15 | 28 | 30 |
| **Slithery**: winner longest | 6 | 9 | 11 | 14 | 21 | 33 | 43 | 55 | **62** |
| Slithery: final-king lineage | 0 | 2 | 3 | 7 | 20 | 33 | 43 | 55 | 62 |
| Slithery: loser longest | 7 | 9 | 11 | 10 | 14 | 16 | 22 | 33 | 40 |
| **QoS** (4 games): winner longest | 3 | 3.5 | 4 | 3 | 4 | 8 | 7.5 | 12 | **21.5** |
| QoS: loser longest | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 7 | 11.5 |

A lineage length of 0 means that dragon was not yet born.

**First round the final king reaches a length** (median, with range):

| map | ≥6 | ≥10 | ≥20 | ≥30 |
|---|---|---|---|---|
| Schooltime | 281 (99-337) | 305 (103-371) | 338 (114-437) | 370 (162-480) |
| Portals | 300 (232-402) | 362 (301-444) | 390 (346-490) | 425 (389-475) |
| Slithery | 228 (1-437) | 269 (1-447) | 297 (1-483) | 331 (313-448) |
| QoS | 406 | 445 | 483 | never |

**Which dragon becomes king.**
- It is **not the starting dragon.** The one exception is SSS on Slithery, which keeps its 25-long starter.
- The king is an ordinary split child born around:
  - Schooltime: rounds 57-316, median about 130.
  - Portals: rounds 220-378, median about 290.
  - Slithery: rounds 66-320, median about 120.
  - QoS: rounds 264-385.
- It then simply **stops splitting** at about length 6 and keeps eating.
- It becomes the team's longest *for good* at a median of round 303 (Schooltime), 352 (Portals), 272 (Slithery) and about 430 (QoS).
- Between round 300 and the end, the final king is the team's longest in only **56-100%** of rounds (Portals median about 0.8). Winners grow **2-3 candidates in parallel**, and the one that ends up biggest wins.
- Final second-longest: Schooltime 34.5 and Slithery 19 (insurance), but only about 10 on Portals.

**Does the king split after it gets big?** Only with **U-turns**, i.e. reverse splits `SPLIT L-2`, which cost 2 length each.
- 83 king U-turns at L ≥ 8 over the 34 round-limit games. SSS does 27 of them, Sabotage-d 13, Sponge 11.
- 60 of the 83 happen with **0-1 free exits**. The median enemy-head distance at the U-turn is 8. So it is the dead-end escape.
- A real halving is almost never done: SHINK once (30 → 15+15 at r351), Sabotage-d once (14 → 7+7).
- Sabotage-d sometimes sheds 2 segments at a time at r404-487 (83→81→79…).

## 2. Where the king's pearls come from

King pearls per round (all sources) and the source mix:

| map | r100-199 | r200-299 | r300-399 | r400-499 | total/game | spawn | own L2-4 | own L5-9 | own L10+ | enemy |
|---|---|---|---|---|---|---|---|---|---|---|
| Schooltime | 0.11 | 0.14 | **0.26** | **0.26** | 78 | **49%** (mostly gap 1-20 tiles: 8 → 10 per 100 rounds) | 25% | 13% | 13% | 1% |
| Portals | - | 0.04 | 0.21 | 0.27 | 52 | 23% (1-10 and 1-1 hot tiles) | **48%** | 18% | 10% | 0 |
| Slithery | 0.04 | 0.09 | 0.24 | 0.28 | 66 | 18% | **57%** | 14% | 8% | 3% |
| QoS | - | - | 0.04 | 0.17 | 21 | 46% | 15% | 18% | 12% | 9% |

- **After round 300 the king eats about 0.25 pearls per round**, which is about 25 length per 100 rounds. That is the whole difference: our king gains about 13 from round 300 (see 09).
- On Schooltime, half the growth is the king **camping the gap-20 spawn tiles**. On Portals and Slithery, 60-70% is own corpses.
- "Own L5-9 / L10+" means **merging**: medium dragons (7-20, and once 27) suicide next to the king.
  - This is 2-4 per game, at dist 2-4, mostly NoValidAction/HitSelf, rounds 380-490.
  - It accounts for 22-31% of king food.
- Enemy corpses are negligible (0-9%).

## 3. King behaviour

Stats per 100-round window from r300 (medians):

| map | unique tiles / 100 moves | revisit | bounding box | net displacement | distance to rich tile | min enemy-head dist | p10 enemy dist | fraction of rounds with enemy ≤ 3 |
|---|---|---|---|---|---|---|---|---|
| Schooltime | 82-95 | 0-0.2 | 31×13 - 30×18 | 13-15 | 2.5-3 | 3-5 | 6-7.5 | **0.00** |
| Portals | 68-83 | 0.1-0.3 | 21×15 - 18×16 (the whole half) | 9-11 | **1** | n/a | n/a | n/a |
| Slithery | 80-99 | 0-0.2 | 15×14 - 19×19 | 11-14 | 4 | 4 | 7-8 | **0.00** |
| QoS | 44-68 | 0.2-0.3 | 10×25 - 25×35 | 10 | 6 | 3 | 5-6 | 0.00 |

On Portals the halves are not connected, so enemy distances are meaningless there.

- **There is no fixed loop.** The king roams a region of about 20×15, moving about 1 tile per round with a net drift of only 10-15 tiles per 100 rounds, staying within 1-4 tiles of rich spawn tiles.
- Two teams camp much tighter: SHINK and Vibing++ on Schooltime (revisit 0.42-0.48, box 10×7 and 13×6 on the gap-20 cluster).
- **The winner's king keeps ≥4 Manhattan from enemy heads**. The p10 is 6-8, and the time spent at ≤3 is about 0-3%.
- **How kings die.**
  - Losers' big dragons (L ≥ 12) on Schooltime and Slithery die **head-on to enemy rammers of length 2-7 at enemy distance 1** (e.g. 龙虎豹's 20/27/20 at r427-457; calc 14/12/17; SSS 12-17 ×5).
  - Winners also lose 1-4 big dragons per game this way (L 10-23 rammed by length 3-4), which is why they keep 2-3 candidates.
  - On Portals nobody gets rammed: the loser just had fewer and later feeders.
  - Other losing-king deaths are the loser's own merges (NoValidAction), not kills.

## 4. Feeders

| map | feeders/game | length | kill method | death round histogram | dist to king at death |
|---|---|---|---|---|---|
| Schooltime | 21 | 2 (57), 3 (49), 4-6 (30), ≥7 (32) | HitSelf 60%, NoValidAction 32% | 200s: 23, **300s: 94**, 400s: 46 | d1 16, **d2 41, d3 33**, d4 23, d5 12 |
| Portals | 25.5 | 2 (106), 3 (90), 4-6 (52), ≥7 (33) | HitSelf 59%, NoValidAction 18%, HitWall 13% | 250: 12, 300: 56, **350: 85, 400: 86**, 450: 39 | d1 33, **d2 60, d3 57**, d4 33 |
| Slithery | 36.5 | 2 (165), 3 (120), 4 (53), 5-6 (27), ≥7 (37) | HitSelf 59%, NoValidAction 34% | 250: 53, **300: 90, 350: 96, 400: 85**, 450: 49 | d1 35, d2 81, **d3 124**, d4 79 |
| QoS | 4.5 | 2-3 | NoValidAction | 450+ | 2-5 |

**Position relative to the king head** (forward, right), where the king's facing is head − neck:
- Schooltime: ahead 44, side 27, behind 14.
- Portals: ahead 106, side 50, behind 39.
- Slithery: ahead 181, side 67, behind 41.
- The top cells are **(1,0)**, (2,0), (0,±1), (1,±1), (3,0), (0,±2) and (1,-2). About 55-60% die in front, 25% beside, and 15% behind.

**Timing and efficiency.**
- The king eats the drop a median **2-3 rounds** later (p75 4).
- 80% of the dropped pearls reach the king: Schooltime 194/234, Portals 334/417, Slithery 456/592.
- Median feeder age at death is 20-47 rounds, i.e. a fresh split child.

**Travel.** The median distance from the feeder to the king head is:
- 20-40 rounds before death: 9-21.
- 10 rounds before death: 10-12.
- 5 rounds before death: 7-9.

The feeder then spends a median of only **2 rounds (p75 4) within 6 tiles** before it dies. So feeders come straight in over about 10 rounds and die on arrival. They do not loiter.

**Death move.** Most deaths are a single step opposite to facing (HitSelf into the neck: 'N', 'S', 'E', 'W' strings). Others are an empty or invalid action (NoValidAction: Vibing++, SSS, 中国人能飞, bread first search), or a 2-step reversal ('NS', 'EW').

**Sonar before feeding.**
- 83-88% of feeders pinged in their last 10 rounds, with a median of 13-24 pings, i.e. **4 directions every turn**.
- That is the whole team's standing relay, not a special "feeding" signal.

**Sonar in general.**
- **The king itself pings in 4 directions every turn from about r300** (king pings/game: 600-1400).
- Most winners send the **same value in all 4 directions**: Sabotage-d, SSS, SKKU, bread first search and 中国人能飞 in 96-100% of turns. Vibing++, calc, Sponge and 龙虎豹 send different values per direction.
- Values are encrypted. The only decodable one is Sabotage-d: 24.5% of its r300+ pings carry the **current king head x,y at bits 0-5 / 6-11** (the format in 05 §5).
- Total pings per game: Sabotage-d 3-10k, SKKU 11-30k, SSS 38-83k. SHINK sends only 1 per turn and still won.

## 5. Units over time (winner / loser, medians)

| map | r100 | 200 | 300 | 350 | 400 | 450 | 499 | winner final units (range) |
|---|---|---|---|---|---|---|---|---|
| Schooltime | 39/17 | 53/20.5 | 53/20 | 53.5/20 | 39/14 | 28.5/8.5 | 16/5.5 | 5-44 |
| Portals | 21/18 | 35/33 | 34/25 | 26/24 | 19/17 | 8/8 | 3/4 | 1-7 |
| Slithery | 63/61 | 64/62 | 60/59 | 58/58 | 45/35 | 30/18 | 15/11 | 1-39 |
| QoS | 11.5/5.5 | 17.5/8.5 | 22.5/8 | 17/8 | 12.5/4.5 | 6/3.5 | 2.5/3 | 2-6 |

The unit count falls from about r350 (Schooltime/Portals) or r375 (Slithery). Winners keep more total length than losers on Schooltime (245 vs 78) but less on Slithery. What wins is the king's share.

## 6. Recipe for our bot

1. **Candidates, not one king.**
   - From `SEED` (Schooltime 200, Slithery 170, Portals 250, QoS 330), exempt the **2 longest dragons** from the length-4 split rule.
   - A dragon keeps candidate status while its length ≥ 6 and it is within the top 2.
   - King = longest candidate. Switch king only if the challenger is +3 longer (hysteresis).
   - Everyone else keeps `SPLIT 2` at length 4 until `STOP` (Schooltime 340, Slithery 370, Portals 360, QoS 420).
2. **The king never splits** except `SPLIT L-2` (U-turn) when it has ≤1 free exit and it is not the last-resort move into an enemy.
3. **King movement.**
   - Greedy pearl path with a BFS on the king's own head. Keep the king within 3 tiles of rich spawn tiles; on Schooltime, camp the gap-20 clusters.
   - Hard constraint: never end a turn at Manhattan ≤3 from a visible enemy head, and ≤4 when L ≥ 15. Prefer free space ≥ 2L (the reachable-area check).
   - Drift is only about 10-15 tiles per 100 rounds, so a local patrol is fine.
4. **Beacon.**
   - The king pings 4 directions every turn from `SEED` with the same value: x (6 bits), y (6), len (6), id (10), hop (2), plus a 16-bit keyed checksum.
   - Allies relay with hop+1 up to 3 hops (and only when the value is new).
   - Feeders keep the last position seen (≤ 20 rounds old).
5. **Feeder dispatch.**
   - From `FEED` (Schooltime 260, Slithery 250, Portals 300, QoS 400), any L2-3 unit (L4-6 after round 380) that is not needed for the reserve paths to the king.
   - It should arrive about 10 rounds later, then die **the same round it reaches a target cell**. Targets in priority order: (fwd1,0), (2,0), (1,±1), (0,±1), (3,0) relative to the king's head/facing, and never behind.
   - Kill: move opposite to facing (HitSelf). For L2 when the reverse is not lethal, use NoValidAction.
   - Throttle: at most 1 death per 2 rounds, and only if no enemy head is within 4 of the drop tile.
   - Targets: 20-35 feeders per game with the peak at r330-430, giving about 0.25 pearls per round to the king.
6. **Merges.** From round 420, candidate #2 (if < king−10 and ≥7) walks to the king and suicides 2 tiles ahead. Do this only if the king leads the enemy's longest by less than 15, otherwise keep it as insurance.
7. **Reserve.** Keep ≥3 units (Portals) and ≥8 (Schooltime/Slithery) at r499.

**Targets for the king** (r300 / 350 / 400 / 450 / 499):

| map | r300 | r350 | r400 | r450 | r499 |
|---|---|---|---|---|---|
| Schooltime | 10 | 20 | 30 | 44 | 57 |
| Slithery | 20 | 33 | 43 | 55 | 62 |
| Portals | 8 | 15 | 25 | 36 | 41 |
| QoS | 5 | 8 | 12 | 20 | |
