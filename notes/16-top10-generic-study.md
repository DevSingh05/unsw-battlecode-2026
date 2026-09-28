# 16 - What the current top-10 do better than us (whole game, map-agnostic)

**Question.** Which behaviours of the current top-10 (Cutlery, cheji bt, forgot to mention, 中国必须人能飞, calc, Sabotage-d, SSS, Sponge, Team SKKU, 龙虎豹) beat mid-table bots, and which of them carry over to unseen maps?

**Short answer (ranked by estimated impact).**
1. **We forget portal warnings.** On Default and Schooltime our blind portal crossings die twice as often as the top teams' crossings, even with the same number of own heads near the exit.
   - 80% of our "crossed into an ally body" deaths hit the neck of an ally that stood on the exit tile the round before.
   - In about 1/3 of them, that ally's PORTAL_WARN sonar had already reached the crosser 1-3 rounds earlier. The crosser discarded it, because warns only count in the turn they arrive.
   - Fix: remember warns for the sender's length (§5.1).
2. **Endgame feeding throughput.** In round-limit games the top king eats 21.7 own-corpse pearls after r350; ours eats 13.0.
   - The top teams use 12.1 feeders per game, 70% of them length 2-3. We use 7.5, only 52% length 2-3.
   - Their feeding starts earlier (r350-399: 3.3 vs 0.9 own-corpse eats by the final king).
   - Final king: **35.9 vs 28.2**.
3. **They keep splitting after r350.** Normal 4→2+2 splits in r350-449: 14.6 vs 4.5 per game.
   - Result: more heads harvesting and more small feeders.
   - Total team length r350→500: 105→98 for them, 96→77 for us.
4. **Our bodies linger on portal mouth tiles.** Our share of segments on mouth tiles, relative to how much of the map those tiles cover, is 1.4-2.6× the top teams' ratio. These parked bodies are what blind crossers hit.
5. **King safety.** The team's longest dragon (L≥10, r300+) dies 0.57 times per game for us vs 0.22 for them.
   - Causes: trapped 0.17, rammed 0.23, blind crossing into an ally 0.11.

**Not different (don't chase):**
- the early game (rounds 1-60): split timing, unit growth, spread;
- trapped/pump death totals;
- head-on trade counts;
- small-dragon spacing.

## 1. Data and tools

- **Top-10 games:** 85 games from 28 Sep 18:14-18:51 UTC (`notes/replays/top10b/*.replay`, `index.json`).
  - Each is a current top-10 team against an opponent rated **1780-1940** (the "peer" group, around our 1850).
  - Covers all 10 ranked maps: 12 each on Default, Autarky and Prisoners Dilemma, 7 each on the others.
  - Teams: Cutlery 15+, cheji bt 14+, 龙虎豹 12, Sabotage-d 7+, forgot to mention 5+, plus others.
  - **No top-10 game against us** was found in our last 250 games (`vs_us.py`).
- **Our games:** 103 v16 games (`replays/v16`, 28 Sep 16:38-18:42; 30 ranked, 73 A/B challenges against peers rated 1650-1950, median about 1850).
  - Skewed to Autarky 20, Default 24 and Prisoners Dilemma 20; only 3-7 games on each other map.
  - Our Schooltime, Portals, Trauma and QoS games run our per-map modules.
- **Groups:** `top`, `peer` (the top team's opponent), `us`, `usopp`. "Map-avg" means the mean over maps, each map weighted equally.
- **Tools** (`notes/tools/top10b/`; all GET-only, with 1.2 s between API requests):
  - `fetch.py`, `fetch_maps.py`, `vs_us.py`: listing and download.
  - `analyze.py`: per (game, team) metrics, written to `metrics.pkl`; `agg.py overview|deaths|portals|early|end` aggregates them.
  - `events.py`: every death, sprint and split with context, written to `events.pkl`.
  - `crossing.py` + `xreport.py`: context of every portal crossing (exit occupant, own heads near the exit, blocker segment index, mouth-tile occupancy).
  - `warncheck.py`: whether the blocker's sonar reached the crosser.
  - `endgame.py`: king lineage, sources of king pearls, feeders.

## 2. Headline numbers (map-avg over 10 maps)

| | win | units r100/200/300/400/500 | longest r300/400/500 | deaths r1-60 / 61-350 / 351-500 | eats r1-60 / 61-350 / 351-500 |
|---|---|---|---|---|---|
| **top** | **0.77** | 24 / 33 / 35 / 26 / 16 | 6.6 / 14 / **25** | 17 / 157 / 45 | 65 / 501 / 145 |
| peer | 0.23 | 19 / 23 / 23 / 16 / 6 | 5.1 / 9.1 / 17 | 18 / 156 / 60 | 61 / 445 / 163 |
| **us** | 0.54 | 23 / 31 / 31 / 23 / 14 | 6.4 / 11 / **18** | 27 / **239** / 48 | 89 / 649 / 152 |
| usopp | 0.46 | 19 / 24 / 24 / 21 / 16 | 6.6 / 9.4 / 15 | 16 / 134 / 45 | 56 / 379 / 136 |

**How games end.**
- **top:** 85 games. Round limit W34 / L11; elimination W31 / L9, so **11% of games are elimination losses**.
- **us:** 103 games. Round limit W27 / L21; elimination W31 / L24, so **23% are elimination losses**.
  - The elimination losses are concentrated on Default (8/24; top 0/12) and Trophy (5/7).

**Mid-game deaths per game (r61-350, map-avg).**

| | head-on vs enemy | head-on vs ally | into ally body | self | wall | no valid action | trapped (0 free nbrs) |
|---|---|---|---|---|---|---|---|
| top | 33 | 13 | 10 | 15 | 49 | 36 | 98 |
| peer | 33 | 3.5 | 17 | 36 | 55 | 11 | 116 |
| **us** | 35 | 4.4 | **54** | **143** | 1 | 0 | 167 |
| usopp | 35 | 6.2 | 12 | 20 | 35 | 27 | 86 |

- Our huge "self" column isn't a gap. Over the whole game, trapped deaths are 116 per game (top) vs 119 (us).
  - These are mostly deliberate pump or feed suicides.
  - We die into our own neck; the top teams die into kelp or with an unpayable sprint.
  - Our trapped deaths into an ally body (all free=0, e.g. Slithery 182 per game) are the same trapped suicides pointed at an ally, so they drop the same pearls.
- **The real outlier is portal collisions** (section 3): into an ally body **54 vs 10**.

## 3. Collision and congestion discipline (Q1)

### 3.1 Portal crossings (whole game)

| map | group | crossings/g | fatal % | fatal/g | re-cross ≤4 rounds | exit held by ally *body*/g | own segs on mouth tiles ÷ map share |
|---|---|---|---|---|---|---|---|
| Default | top | 330 | **9.0** | 30 | 23% | 12.8 | 2.46 |
| Default | peer | 69 | 11.7 | 8 | 11% | 2.5 | 1.03 |
| Default | **us** | 401 | **16.8** | **67.5** | 30% | **45.6** | **3.34** |
| Default | usopp | 151 | 10.2 | 15.5 | 19% | 5.5 | 1.77 |
| Schooltime | top | 232 | 10.0 | 23 | 5% | 10.6 | 1.87 |
| Schooltime | **us** | 430 | **17.9** | **77** | 15% | **53.3** | **3.28** |
| Trophy | top | 9 | 4.5 | 0.4 | | 0.4 | 1.66 |
| Trophy | **us** | 31 | **29.3** | 9.0 | | 6.6 | **4.31** |
| Slithery | top | 32 | 8.1 | 2.6 | | 1.1 | 0.95 |
| Slithery | **us** | 82 | **25.9** | 21 | | 10.0 | 2.11 |
| Portals | top | 498 | 9.8 | 49 | 12% | 13.7 | 0.79 |
| Portals | us | 669 | 30.8 | 206 | 14% | 68 (+115 into *own* body: Portals-module neck suicides) | 1.03 |
| Trauma | top / us | 128 / 156 | 6.9 / 6.8 | 9 / 11 | | | 1.17 / 1.04 |
| Autarky | top / us | 112 / 34 | 7.7 / 11.1 | 8.7 / 3.8 | | | 1.28 / 0.85 |

- **Every** fatal crossing was onto an exit tile that was already occupied when the move was made. The engine resolves moves strictly in order, so nothing else can kill a crossing.
- **Blind crossings are most of them.** The exit is outside the Chebyshev-3 view in 84% of top crossings on Default (93% of ours) and 100% on the other maps.
- The top teams cross about as often as we do: 4.1% of moves on Default against our 7.1%. They simply land on occupied exits half as often.

**Fatality of blind crossings, by the number of own heads within 3 of the exit** (the bot can't see these):

| | 0 | 1 | 2 | 3+ |
|---|---|---|---|---|
| Default top | 2.6% | 8.9% | 11.6% | 15.5% |
| Default **us** | 5.8% | **15.7%** | **24.6%** | **31.3%** |
| Schooltime top | 4.8% | 9.6% | 11.6% | 19.9% |
| Schooltime **us** | 11.0% | 13.9% | 18.8% | 25.3% |
| Portals top | 0.5% | 8.4% | 19.8% | 19.8% |
| Portals **us** | 2.8% | **30.1%** | **44.6%** | **47.9%** |

At the same local density we still die about twice as often. So the difference isn't how many of our dragons are near the exit; it's **where their bodies are** and **whether the crosser knew about them**.

### 3.2 Who blocks the exit (Default, 1,095 of our fatal "ally body" exits over 24 games)

**Where the blocker's body sits.**
- **80%**: the blocker's **segment 1 (neck)** is on the exit, and its head is 1 tile away. It stood on the exit last round and has just stepped off.
- 14%: segment 2 is on the exit.
- The blocker is usually length 2-3 (88%). In 91% of cases its head is no longer on a mouth tile.
- Classification: "resident" (hadn't crossed in the last 8 rounds) 22 per game; recently crossed a different portal 17 per game; convoy (crossed this same portal just before) 6.6 per game.
  - Top: 8 / 3.8 / 1.0 per game on ally *bodies*.
  - The top teams' exit deaths are more often head-on with an ally head: 12 per game, where both die.

**`warncheck.py`: did the blocker's sonar reach the crosser?**
- Default: in **349 / 1,095 (32%)** the blocker's own sonar hit the crosser in the 3 rounds before the crossing, but **never in the same round**.
- Schooltime: 123 / 376 (33%). Trophy: 13 / 46.

This matches the code:
- `emitSonar()` sends PORTAL_WARN when our head is on a `portalExit` tile.
- `readMessages()` only honours it if `round - rnd <= 1`, and only for the current turn (`WARN_FREE_T 2`). `occId`/`freeT` are rebuilt every turn in `analyse()`.
- A higher-ID crosser gets the warn in the same round it's sent, while the blocker's head is still on the exit, so it waits one turn.
- The next round the head has moved on but the neck (and, for L=3, the tail after that) still covers the exit. By then the warn is forgotten and the crosser walks in.
- **So the missing piece is warn memory, not warn delivery.**

### 3.3 Why it matters beyond Default

- In our 8 Default elimination losses, 35 of our dragons per game die crossing into ally bodies, against about 40 lost in enemy head-on trades. That is what collapses our unit count (12 → 3 units from r150 to r400).
- On unseen maps we currently treat portals as kelp (LEARN_PORTALS=0), so we forfeit portal mobility that the top teams use on every map (1-6% of their moves).
- LEARN_PORTALS lost 0.31-0.45 because of door jams. Safer crossing is the prerequisite for turning it back on.

## 4. Early game (r1-60, Q2): no generic gap

| map-avg | first split round | units r30 / r40 / r60 | total length r60 | eats r1-60 | deaths r1-60 | round reaching 16 units | mean nearest-own-head distance at r60 | 4×4 map cells occupied at r60 |
|---|---|---|---|---|---|---|---|---|
| top | 4.7 | 9.9 / 12 / 16 | 40 | 65 | 17 | 76 | 4.8 | 7.2 |
| **us** | 2.1 | 11 / 13 / 17 | 41 | **89** | 27 | 79 | 3.6 | 6.7 |

- We split as early as the top teams, grow as fast, and eat more.
- Our extra early deaths are pump/trap deaths straight after a split on Slithery, Portals and Autarky. The top teams have the same deaths as HitWall.
- We are slightly more clumped: nearest own head 3.6 vs 4.8. That fits notes/14 (SPREAD_GENERIC has low value).
- **Exceptions.**
  - **Trophy:** 17.9 units / length 44 at r60 for the top teams, against 10.4 / 27 for us.
  - **QoS:** 8.7 early deaths for us vs 1.9.
  - Both are tied to specific maps, not general behaviour.

## 5. Endgame (r350-500, Q3): round-limit games only (top 45, us 48 team-games)

| | king r350 / 400 / 450 / 500 | king eats r350+: spawn / own corpse / enemy corpse | feeders per game (L2-3 share) | units at 500 | second-longest | total length r350→450→500 | normal splits r350-449 | non-king sprints r350+ |
|---|---|---|---|---|---|---|---|---|
| **top** | 7.8 / 14.7 / 25.0 / **35.9** | 9.0 / **21.7** / 1.2 | **12.1** (70%) | 5.3 | 16.1 | 105 → 97 → 98 | **14.6** | 10.3 (2.6 eat, 2.1 kill, 5.9 die) |
| peer | 6.1 / 11.1 / 20.1 / 27.7 | 15.3 / 23.6 / 1.1 | 16.7 | 5.7 | 10.5 | | 20.6 | 6.4 |
| **us** | 6.0 / 11.2 / 19.3 / **28.2** | 12.9 / **13.0** / 1.0 | **7.5** (52%) | 7.9 | 16.7 | 96 → 80 → 77 | **4.5** | 0.8 (all rams) |

- **Own-corpse pearls eaten by the final-king ID, per 50 rounds** (top vs us): r300 1.3 vs 0.2; r350 **3.3 vs 0.9**; r400 7.4 vs 3.4; r450 7.0 vs 4.0.
  - The top teams start feeding earlier and feed about twice as fast, with a similar number of allies within 6 of the king (2.2 vs 1.9 at r360).
- **Losing big dragons late** (L≥10, r300+; the team's longest at the time of death):
  - us 0.57 per game: trapped HitSelf 0.17, rammed by a small enemy 0.12, rammed by a larger enemy 0.11, blind crossing into an ally 0.11, others;
  - top 0.22 per game.
  - The top teams' non-king L≥10 deaths are mostly voluntary merges into the king, with free exits (1.26 per game; us 0.66).
- **King exposure is the same.** Moves with an enemy head within 2: top 4.4, us 3.8, peer 10.8. So "avoiding our rams" is just the normal distance keeping we already have.
- **Killing enemy kings is rare for everyone:** 0.20 per game (top) vs 0.16 (us). Top wins by out-growing, not by assassination.

## 6. Head-to-head: what beats mid-table bots (Q4)

- Top teams beat 1780-1940 peers 77% of the time (65/85), 31 of them by elimination.
- **Head-on trades are symmetric** (33 vs 33 per game in r61-350), so the unit gap comes from *growth* and *self-inflicted losses*.
  - Units at r200: top 33 vs peer 23 (Default 26 vs 16, QoS 19 vs 6.6, Trophy 36 vs 11, Devil 30 vs 9).
  - Mid-game eats: Default 311 vs 154, QoS 241 vs 122, Autarky 267 vs 202.
- Once ahead on units, the top teams keep trading 1-for-1 until the peer runs out (Default: peers go 11.6 → 1 units from r100 to r400).
- In round-limit games the top king ends 36 vs 28, built from own-corpse feeding.
- **We already match the top teams on the economy side** (units r200 31, mid-game eats 649).
  - Against peers, what we lack is (a) not killing our own dragons at portals, which lets peers survive or eliminate us, and (b) turning our length into one king in the last 150 rounds.

## 7. Proposals (all new `#define`s, default 0; ranked by estimated impact)

### 7.1 `PORTAL_WARN_MEMO` (remember portal-exit warns for the sender's length)
- **Functions.**
  - `encodeWarn()` / `decodeWarn()`: add the sender's length, `min(myLen,15)`, in 4 bits taken from the 43-bit checksum (bits 21-24; checksum 39 bits).
  - `readMessages()`: push each decoded warn into a new member `std::vector<std::array<int,2>> warnMem` as `{tile, untilRound = rnd + len}`. Drop entries with `untilRound < round`.
  - Re-apply every remembered warn each turn, after `computeFreeTimes()` in `analyse()`:
    - `occId[tile] = 1<<20`, `occTeam = myTeam`, `occHead = (round == rnd)`;
    - `freeT[tile] = freeOther[tile] = max(.., untilRound - round + 1)`.
  - Relax the expiry check `round - rnd > 1` to `round - rnd >= len`.
- **Optional sub-flag `PORTAL_WARN_KING_VETO`:** if `myLen >= 10`, the candidate loop in `decide()` rejects any step whose destination is a `portalExit` tile with a live `warnMem` entry, even if `freeT` would allow it.
- **Evidence.** 32-33% of our fatal ally-body exits had a delivered and then forgotten warn. The block lasted exactly the neck/tail rounds.
- **Expected effect.**
  - About −20 own deaths per game on Default and −15 on Schooltime; a few on Trophy and Slithery.
  - Units +5-8 at r300 on Default, and fewer elimination losses there.
  - No effect on portal-free maps, and it never makes a move less safe.
  - A prerequisite for re-testing `LEARN_PORTALS` on unseen maps.
- **Test.**
  - Mechanism: rerun `crossing.py` + `warncheck.py` on local Default/Schooltime replays. The "warned_by_blocker" fatal count should go to about 0.
  - Then server A/B on Default + Schooltime against the peer set.
  - Local self-play under-reports this: crossings killed only about 5 per game locally, against 60 on the ladder.

### 7.2 `FEED_EAGER` (more, earlier, smaller feeders)
- **Functions.** `shouldFeed()` and the feeding block at the top of `decide()`.
- **Changes when on.**
  - L2-3 dragons may feed from `RP.feedStart` whenever `kingLen >= myLen + 4`.
    - Drop the `units > RP.feedReserve` gate for L≤3 as long as ≥ `FEED_RESERVE` dragons of length ≥4 exist, or r ≥ 450.
  - The `dieNow` spot becomes any free tile at Chebyshev ≤2 of `kingTile` that isn't behind the king.
  - `enemyNear` uses radius 3 instead of 4.
  - Accept a sonar-fresh king position (`round - kingRound <= 1`) instead of requiring `kingVisible`.
- **Evidence.**
  - Own-corpse king eats: 21.7 vs 13.0. Feeders: 12.1 vs 7.5, 70% L2-3.
  - r350-399 own-corpse eats: 3.3 vs 0.9. Final king: 35.9 vs 28.2. Similar ally density around the king.
- **Expected effect.** King +5-8 at r500 in round-limit games.
- **Risk.** Earlier tests (FEED_MAX_LEN=5, FEED_START ±50) were neutral in self-play, and self-play can't measure king races. Test on the server on Schooltime, Slithery, Trauma and Default.

### 7.3 `LATE_SPLIT_ROUND` (default 0 = off; try 440)
- **Function.** The normal-split condition in `decide()` (`round < RP.splitStopRound`).
- **Change.** When on, non-king dragons with no `kingSelf`, and while a king is known (`kingId >= 0`), keep doing the 4 → 2+2 split until `LATE_SPLIT_ROUND`.
- **Evidence.**
  - Normal splits r350-449: 14.6 vs 4.5.
  - Team length holds at about 97-105 until r500 for them, but falls 96 → 77 for us.
  - Their endgame eats: 236 vs 204 (round-limit games).
  - v3 found 350 better than 300 (26-14), which suggests the trend continues.
- **Expected effect.** More r350-450 harvest (+20-30 eats) and a larger pool of L2 feeders for 7.2. Pair it with 7.2.

### 7.4 `MOUTH_CLEAR` (don't park on portal landing tiles)
- **Function.** The per-direction candidate loop in `decide()`, next to the existing `if (portalExit[t])` block.
- **Change.** When not crossing, subtract `MOUTH_CLEAR_PEN` (start at 3.0, 0.3 pearl) for a destination `t` with `portalExit[t]` that has no pearl. Also subtract 1.0 per own body segment that would still lie on a `portalExit` tile next turn.
- **Evidence.** Our segment share on mouth tiles relative to map share is 3.34 vs 2.46 on Default, 3.28 vs 1.87 on Schooltime, 4.31 vs 1.66 on Trophy, and 2.11 vs 0.95 on Slithery. Those bodies are the blockers in 3.2.
- **Expected effect.** Complements 7.1 for the 65% of blocked exits where no warn reached the crosser.
- **Check.** Mouth ratio and fatal crossings should drop without a fall in crossings. (PORTAL_ALLY_COST cut crossings and *raised* deaths, probably because dragons then waited at mouths.)

### 7.5 `KING_TRAP_UTURN` (king escapes dead ends before it's sealed in)
- **Function.** `decide()`, before the split block, for `iAmKing() && myLen >= 10`.
- **Change.** If `surviveDepth()` for every move is < `myLen/2` and there are ≤1 free exits, use the reverse split `SPLIT myLen-2` now, instead of waiting until trapped.
- **Evidence.**
  - Our longest dragon dies trapped 0.17 per game after r300 (top 0.04).
  - Top kings do 83 U-turns at L≥8 in 34 games, 60 of them with 0-1 exits (notes/11).
- **Expected effect.** Small but decisive when it fires: 0.1-0.15 kings per game saved.

### 7.6 `PORTAL_PROBE` (experimental; lowest confidence)
- **Function.** `emitSonar()` and the candidate loop.
- **Change.** When the head ends its move on a portal entry tile facing the portal, and it isn't sending king or relay messages, cast a single ray in the facing direction. Next turn, if `ECHOES` shows ally, ally-head, enemy or enemy-head > 0, add `PORTAL_PROBE_PEN` (20) to the crossing move.
- **Why.** Sonar passes through portals; vision doesn't. Almost every top team sends 4 rays per dragon per turn: 20k sonars per Default game, against our 2k. Their payloads are encrypted; "forgot to mention" puts `y*W+x` at bit 25. They clearly have far more positional information than we do.
- **Risk.** The echo has no range, so it over-blocks: anything along the line past the exit counts. Only try it after 7.1 and 7.4.

## 8. Caveats

- Samples are small: 7-12 top games per map, and 3-7 of ours on 7 maps.
- Our map mix is skewed (Default/Autarky/Prisoners Dilemma) and our Schooltime/Portals/Trauma/QoS games run map modules. Portals "self" exits are module neck suicides and are excluded from the conclusions.
- The time windows differ by about 1-2 h.
- notes/14 measured top Default crossings at 71 per game (r60-320, a different top-10 mix). This sample (Cutlery, cheji bt) crosses 330 per game (whole game) at 9% fatality. The conclusion "cross safely, not less" is stronger here than in 14.
