# "dev test 1 :P" (team 545): why it is so strong, and what we can copy (5 Oct)

Written 5 Oct ~08:30 UTC (04:30 EDT). Read-only: nothing in `bot/` or `variants/` changed, nothing submitted, no challenges, no Discord or browser.

## TL;DR
- **No new DEV build since 4 Oct 09:04 UTC is visible.** The climb from 2297 to 2527 came from batches of ranked challenges that DEV launched itself. Its win rate and mechanisms are the same in every window.
- **Against us, DEV does not out-eat us. It wastes less.**
  - Fresh pearls eaten are equal, and we even re-eat more corpses.
  - But we lose about 127 more length per game to self-inflicted deaths: units boxed in by ally bodies (+79) and children that die in their first round (+54).
  - That is the whole r300-r400 mass gap (r300 total 130 vs 98, r400 153 vs 104). It turns into 28 losses on longest dragon.
  - The waste is concentrated on Around UNSW, Australia, Devil, Tower Defense and Schooltime.
- **Eliminations (40 of 84 losses) are the lane maps:**
  - Trophy 7/7, Stripes 6/7, Tower Defense 5/7, Queen Of Spades 5/7, Autarky 4/7, Devil 4/7, Prisoners Dilemma 3/7, Default 3/8, weakhold 2/7.
  - Our L4-7 queen is rammed between r13 and r160.
  - DEV keeps its queen at L2-3, close to home, on those maps.
- **Two moves DEV and Vibing++ make at scale that we barely make:**
  - Tip reversal: a unit walks into a dead end to eat, splits its bulk off the tail (k = L-2) and leaves. DEV does 87 per game, Vibing++ 126, we do 25.
  - Pearl-funded lunges (3-step kills that only reach because a pearl is eaten on the way): DEV 5.6 per game, we do 0.

## 1. Rating history, builds, record

### Rating
Source: `GET /api/v1/teams/545`, 161 history points.

| time (UTC / EDT) | rating | what happened |
|---|---|---|
| 1 Oct 12:31 → 4 Oct 09:04 UTC | ~1800-1870 | flat |
| 4 Oct 09:04-10:26 UTC (05:04-06:26 EDT) | 1810 → 2185 | new build (the one in TOP1_VIBING_OCT4.md) |
| 4 Oct 23:28 UTC (19:28 EDT) | 2297 | slow drift up |
| 5 Oct 03:20-03:22 UTC (23:20-23:22 EDT 4 Oct) | 2321 → 2340 → **2382** | 30 ranked challenges vs forgot to mention (FTM), Vibing++ (VIB) and SSS within 2 minutes. Swings of ±30 per battle, then 2412 → 2320 by 04:09. |
| 5 Oct 05:33-06:02 UTC | 2398 → 2413 | |
| **5 Oct 06:09:20-06:12 UTC (02:09-02:12 EDT)** | **2413 → 2436 → 2457 → 2472 → 2488 → 2499 → 2517** | **30 ranked games vs Vibing++ in 4 minutes, DEV won 30-0** (plus 2 vs SHINK AI) |
| 06:26 UTC | 2527 (peak) | |
| 06:42 UTC | 2515 | |

**Is there a new build? No sign of one.**
- DEV's win rate over its whole schedule (listing since 23:00 UTC 4 Oct, 3,681 games) is flat: 1444/1742 (83%) before 03:20, 1238/1510 (82%) between 03:20 and 06:08, 337/429 (79%) after 06:08.
- Our 120 loop games show the same mechanisms before and after 06:00: 43/60 vs 41/60 DEV wins; r300 total 136 vs 130; kills 33 vs 39 per game; 3-step kills 5.0 vs 6.6; stillborn children 22 vs 27.
- The only thing that changed is the result vs Vibing++: 8/17 → 17/27 → **42/47 (30/30 ranked) after 06:08**. Either VIB uploaded something weak against DEV, or DEV picked the maps for those battles.

**Side finding (answers open question #3 in RULES).** Vibing++ lost 30 ranked games to DEV at 06:08-06:14, but its rating went 2374 (06:04) → 2362 (06:21) → 2386 (06:42). Ranked games against a dev team appear to move only the dev team's rating. Our unranked loop against DEV costs us nothing.

### DEV record since 23:00 UTC 4 Oct (listing; DEV wins / games; ranked in brackets)

| opponent | all windows | 23:00-03:20 | 03:20-06:08 | 06:08-06:45 |
|---|---|---|---|---|
| Vibing++ | 67/91 (rk 36/40) | 8/17 | 17/27 | 42/47 |
| SSS | 51/89 (rk 33/55) | 10/17 | 13/25 | 28/47 |
| forgot to mention | 72/117 (rk 17/30) | 28/36 | 33/64 | 11/17 |
| Sponge | 12/22 (rk 3/5) | 9/17 | 3/5 | - |
| **us** | **88/125** (rk 4/5, the b1 games of 4 Oct) | 4/5 | 47/65 | 37/55 |
| bread first search | 312/405 | | | |
| everyone else | 2392/2801 (85%) | | | |

**Our builds.**
- f1 (02:45-04:24 UTC) never met DEV.
- All 120 loop games (05:04-06:39 UTC) are h1 = f1 + LATE_HUNT + QKILL_KING. h1 plays like f1 except when a lone enemy queen is left, so read "us" below as f1/h1.
- Our loop record: **36/120 (30%)**.

## 2. Data and tools
- **Listing:** `replays/devtest/games_545.json`, 3,692 games since 23:00 UTC 4 Oct, crawled with `fetch_dev5.py`.
- **Replays: 161 in `replays/devtest/`** (`sample.json`):
  - all 120 dev-loop games vs us (7 per map, Default 8; ids from `replays/auto_dev/launched.jsonl`);
  - DEV vs VIB 12, vs FTM 12, vs SSS 12, vs Sponge 5. All of these are after 03:20 UTC and spread over maps.
- **Scripts** in `notes/top5/new_rules_tools/` (all reuse `notes/tools/midgame/sim2.py`); rows are in scratch `dev5/prof.pkl`. Run them from that directory.

| script | purpose |
|---|---|
| `prof_dev5.py` | per-game, per-side profile |
| `agg_dev5.py SIDE OPP [--since/--until/--maps]` | team tables |
| `ledger_dev5.py` | mass ledger |
| `feed_dev5.py` | anatomy of feeding deaths |
| `selfcause_dev5.py` | self-death causes |
| `forced_dev5.py GID..` | were self-deaths forced? |
| `allybody_dev5.py` | deaths into ally bodies |
| `crowd_dev5.py` | crowding |
| `ambush_dev5.py` | kill anatomy |
| `permap_dev5.py` | per-map table |
| `h2h_dev5.py [L\|W\|all]` | decisive moment per game |
| `trace_dev5.py GID [--ids/--team/--from/--to/--kills/--snap]` | the turn-by-turn tracer |
| `dl_dev5.py` | id-list downloader |

## 3. Profile (DEV vs us, 120 games, medians or per-game means; "DEV | us")

### 3.1 Opening (first 60 rounds)
Even or in our favour on most maps. Per map at r60 (units / total, DEV vs us):
- **Ours ahead:** Australia 14/36 vs 22/60, Schooltime 11/27 vs 26/60, Portals 16/44 vs 25/62.
- **Even:** Around UNSW 34/90 vs 37/96, Islands 30/77 vs 35/84, Maze 17/44 vs 17/46.
- **DEV ahead, lane maps only:**
  - Trophy 20/49 vs 1/5 (eliminated by r39-100);
  - Stripes 14/30 vs 5/11 (our queen dives into the vault at r13 every game);
  - Tower Defense 5/12 vs 3/6.

**DEV's opening pattern:**
- Mostly L4→k2 splits.
- On Around UNSW (10 per game), Autarky (18) and Slithery Fight (42) it also makes many bulk splits in r0-60; we make 2-3.
- More of DEV's heads sit in our half at r60 on Trophy (8 vs 1), Around UNSW (7 vs 2) and Stripes (4 vs 0). On other maps it is about even.

**DEV queen, first split:**
- Median r12 (ours r27); never splits in 22/120 (ours 27).
- Per map, from r0 (spawned L5: Devil, Maze, Schooltime, Trauma, weakhold) to late or never (Around UNSW r117, Autarky r292, Portals r195).

### 3.2 Unit length distribution (share of unit-rounds)

| rounds | DEV: L2 / L3 / L4-7 / L8+ | us: L2 / L3 / L4-7 / L8+ |
|---|---|---|
| r0-49 | 60 / 29 / 10 / 0 | 63 / 25 / 11 / 0 |
| r100-199 | 56 / 34 / 8 / 2 | 60 / 32 / 7 / 0 |
| r200-299 | 53 / 33 / 11 / 3 | 58 / 33 / 8 / 2 |
| r300-399 | 49 / 32 / 12 / 6 | 55 / 33 / 7 / 5 |
| r400-500 | 32 / 24 / 23 / 21 | 45 / 30 / 14 / 11 |

- Fresh eats per game by eater class: DEV L4-7 87, L8+ 50; us 34 and 22. We make up for it with L2/L3 eats (406 vs 329), so **total fresh intake is equal**.

### 3.3 How it splits
- **Per game:** DEV 294 splits, us 346. Children dead within a round: DEV 24.6, us 54.1.
- **Child sizes (per game):**
  - DEV: L4→k2 187, L5→k3 31.5, L6→k4 15, L7→k5 7.5, L8→k6 5.5, L12+→k10+ 13.4.
  - Us: L4→k2 302, L5→k3 15, L12+→k10+ 4.9.
- **Bulk splits (k ≥ L-2, L ≥ 5): DEV 87 per game, VIB 126, SSS ~67, us 25.**
  - Of DEV's bulk splits, 65% are made with 0 free exits at the head and 27% with 1. 67% are at L5-7, 22% at L8-14, 11% at L15+.
  - This is a **tip reversal**: the head is in a dead end, the bulk leaves as the child from the old tail, and the 2-long parent dies next turn.
  - Example: 1112500 r202, an L15 at 0 exits splits k13, and the parent dies by NoValidAction at r203.
  - Late king bulk splits (L12+ → k10+) run at 13 per game, mostly r400-500.

### 3.4 Feeding
- **DEV feeds with an illegal `SPLIT 1` or an explicit suicide.** The unit dies in place; this is the NoValidAction reason. There are no timeouts (`tle` is 0).
- Our feed is a move into our own neck (HitSelf). The effect on the board is identical.
- **Self-inflicted deaths, non-queen, length lost per game (`selfcause_dev5.py`):**

| cause | us: deaths (length) | DEV: deaths (length) | excess for us |
|---|---|---|---|
| all | 270 (663) | 205 (536) | **+127** |
| stillborn child (age ≤ 1) | 50 (105) | 20 (51) | **+54** |
| fed to king (king within 3) | 19 (52) | 18 (54) | 0 |
| boxed in by ally bodies (no free tile) | 116 (283) | 84 (204) | **+79** |
| boxed by own body / kelp | 48 (123) | 62 (159) | -36 |
| had a free tile | 34 (91) | 20 (64) | +27 |

- Most feeding deaths on both sides are **not** king feeding: the median distance to the own king is 14-16.
- **DEV feeds at the unit cap.** 59% of its feeding deaths happen with ≥ 56 units alive; ours 29%. DEV's first-round child deaths are deliberate (NoValidAction 16.8 per game); ours are accidental (HitSelf 37 + ally body 13).
- **Who eats the pearls from feeding deaths** (40-game sample, within 15 rounds):
  - DEV's go to L4+ units and its king 93 per game, small units 124.
  - Ours go to L4+ and king 59, small units 230. That is churn: an L2 dies → 1 pearl → an L3 eats it → splits → ...
  - About 90% of the pearls are re-eaten on both sides.
- **Crowding** (r100-300): ally heads within 3 of each head, DEV 1.19 vs us 1.54; heads with exactly one free tile 19.8% vs 23.7%.

**Mass ledger, r100-399 (per game):**

| | eats | death losses | of which head-on | of which self-inflicted | net |
|---|---|---|---|---|---|
| DEV | 619 | 545 | 165 | 378 | about +74 |
| us | 632 | 616 | 146 | 467 | about +16 |

- **The whole gap is self-inflicted waste.**

**Per map, length lost to self-inflicted deaths per game (us / DEV):**

| map | all | stillborn | boxed by ally | crowd penalty set? |
|---|---|---|---|---|
| Around UNSW | **1744 / 930** | 298 / 63 | 762 / 328 | no |
| Australia | **1209 / 451** | 188 / 63 | 506 / 117 | no |
| Devil | **444 / 124** | 129 / 17 | 269 / 80 | no |
| Tower Defense | **170 / 32** | 25 / 3 | 81 / 20 | no |
| Schooltime | **855 / 491** | 102 / 25 | 449 / 184 | crowd 3 |
| Trauma | 778 / 563 | | 362 / 290 | crowd 3 |
| Islands | 917 / 774 | 176 / 37 | 270 / 271 | no |
| Maze | 1167 / 1037 | | | crowd early |
| Portals | 1258 / 1203 | | | crowd 3 |
| Slithery Fight | 2271 / 2552 | | | no |
| Default | 136 / 156 | | | no |
| Queen Of Spades | 50 / 78 | | | crowd 3 |

### 3.5 Queen
- **DEV queen, all games vs us:**
  - Median length 3 all game. Alive at the end 56/120 (ours 25/120). Crowned (L ≥ 15 and king at the end) 19 (ours 12).
  - Death median r155 (ours r89).
  - Deaths: head-on 54 (12 before r100, 25 at r100-299, 17 late); NoValidAction 8, early, on Stripes and Queen Of Spades (she is fed).
- **DEV's queen policy is per map:**
  - **Lane maps: stays small and near home.**
    - Tower Defense: L2, 3-4 tiles from spawn, nearest enemy head 12-14; alive 8/10.
    - Trophy: L2, alive 6/10. Prisoners Dilemma: L3, alive 6/7. Schooltime: L3 on the spawn, alive 10/10. Devil: L2.
    - Ours, by contrast, is L4-7 and roams 8-15 tiles out (TD 8-14, PD 14-15).
  - **Big maps: she works as an economy unit.**
    - Around UNSW: L6 at r50, L10 at r100, 22 tiles out. Islands: L7 → L14.
    - She dies mid or late (alive 1/10 on Around UNSW, 0/9 on Australia, 1/10 on Islands). DEV wins those maps on longest dragon anyway.
  - **Crowned:** Maze 6/10, Portals 7/11, Trauma 8/9.
    - On Portals her repeated L12+→k2 peels (9 per game) look like our QBOX K2 shedding.
- **DEV kills our queen in 62/120 games.**
  - Median r112; she is L4-6 in 44 of them and L10+ in 9.
  - Killers: L2 18, L3 24, L4 8, L9+ 6. Steps: 1 → 18, 2 → 22, 3 → 10, 4 → 6, 5-6 → 6.
  - Approach: median distance 7 → 6 → 5 → 5 → 3 over the last 6 rounds.
- We kill DEV's queen in 51/120 games (median r191).

### 3.6 Kings
- **DEV is later, but builds more big units:**
  - First L10: r241 vs our r237. First L20: r371 vs r323. First L30: r400 vs r361.
  - Units of L ≥ 10 at r300: 1.23 vs 0.76. At r400: 2.87 vs 1.55.
- **In the 41 round-limit games decided on longest dragon:**
  - **Losses (28):** DEV's total is 208 vs our 118 at r350. Its longest climbs 22 → 33 → 48 → 56 (r350/400/450/499); ours stalls at 26.
  - **Wins (13):** our total leads 145 vs 125 at r350, and our longest goes 28 → 52.

### 3.7 Kills
- **Per game:**
  - DEV 36.1 head-on kills. Steps: 1 → 13.6, 2 → 16.1, 3 → 5.8, 4-5 → 0.6. 22 are paid; 7.4 are paid and ate a pearl.
  - We make 29.5. Steps: 1 → 16.7, 2 → 12.6, 3+ → 0.2. 12.7 paid; 1.3 paid and ate.
- **5.6 DEV kills per game reach further than plain free + paid steps allow, only because a pearl was eaten on the path.** We have 0.
  - Example: Trophy 1115904, `WNW ate1` and `EEN ate1` from L3 units.
- **Kills of newborn units** are minor on both sides (1.5 vs 1.2 per game). One ambush is notable: Trophy 1115904 r35, our L4 queen was killed by a child born that round from an enemy tail.
- **Big units are traded about evenly:**
  - DEV kills 1.1 of our L ≥ 8 units per game (21.5 length); we kill 1.4 of theirs (21.8 length).
  - DEV does it with 3-5 step lunges (r400+: 3 steps 26, 4 steps 15, 5 steps 5); we do it with 1-2 step rams by L2-3.
  - Approach to our L10+ units: median distance 9 → 8 → 6 → 5 → 3 over the last 6 rounds. The hunter closes over about 4 rounds.
- Paid moves without a kill: DEV 19.6 per game (8.1 ate a pearl); us 0.

### 3.8 Other
- **Endgame, r500 games:**
  - DEV wins 28 on longest and 16 on queen; it loses 12 on longest and 15 on queen.
  - Longest-dragon games are decided by the r350 mass gap (3.6).
- **Portals:** on maps with portals, DEV makes a median 132 crossings per game, we make 105.
  - All 3 queen-tiebreak losses with both queens alive are on Portals (34 v 49, 30 v 32, 39 v 43). DEV's crowned queen ends a little longer than our parked one.
- **Per-map results, our wins / 7 vs DEV:**
  - Trauma 6, Portals 4, Prisoners Dilemma 4;
  - Australia, Around UNSW, Default (of 8), Devil, weakhold 3 each;
  - Tower Defense and Queen Of Spades 2;
  - Maze, Slithery, Stripes 1;
  - **Autarky, Islands, Schooltime, Trophy 0.**

| map | us W/n | endings (our view) | total r100 us v DEV | r200 | r300 | our queen alive / DEV's | our queen death (median) |
|---|---|---|---|---|---|---|---|
| Around UNSW | 3/7 | L-longest 3, L-queen 1, W-longest 3 | 112 v 133 | 161 v 200 | 172 v 233 | 0/1 | r119 |
| Australia | 3/7 | L-longest 4, W-longest 3 | 102 v 59 | 181 v 105 | 173 v 146 | 0/0 | r62 |
| Autarky | 0/7 | L-elim 5, L-longest 2 | 53 v 59 | 25 v 95 | 20 v 129 | 0/4 | r98 |
| Default | 3/8 | L-elim 3, L-queen 2, W-elim 2, W-longest 1 | 45 v 44 | 55 v 65 | 35 v 117 | 0/4 | r110 |
| Devil | 3/7 | L-elim 4, W-elim 3 | 28 v 38 | 94 v 26 | 84 v 32 | 0/2 | r53 |
| Islands | 0/7 | L-longest 6, L-queen 1 | 103 v 103 | 103 v 163 | 99 v 204 | 0/1 | r114 |
| Maze | 1/7 | L-queen 4, L-longest 2, W-longest 1 | 71 v 89 | 125 v 148 | 119 v 147 | 0/4 | r357 |
| Portals | 4/7 | L-queen 3 (both alive), W-queen 4 | 74 v 74 | 82 v 93 | 80 v 91 | 7/5 | alive |
| Prisoners Dilemma | 4/7 | L-elim 3, W-elim 1, W-queen 3 | 18 v 4 | 38 v 4 | 52 v 3 | 3/6 | r30 |
| Queen Of Spades | 2/7 | L-elim 5, W-elim 1, W-longest 1 | 27 v 27 | 20 v 43 | 33 v 20 | 0/0 | r45 |
| Schooltime | 0/7 | L-longest 7 (queens 3 v 3) | 108 v 66 | 162 v 158 | 154 v 191 | 7/7 | alive |
| Slithery Fight | 1/7 | L-longest 3, L-queen 3, W-longest 1 | 150 v 140 | 152 v 213 | 143 v 225 | 0/3 | r191 |
| Stripes | 1/7 | L-elim 6 (queen r13 vault), W-elim 1 | 8 v 55 | | | 0/1 | r13 |
| Tower Defense | 2/7 | L-elim 5, W-longest 2 | 18 v 36 | 70 v 6 | 89 v 14 | 0/5 | r89 |
| Trauma | 6/7 | W-queen 6, L-queen 1 | 62 v 55 | 102 v 109 | 102 v 97 | 6/6 | r499 |
| Trophy | 0/7 | L-elim 7 | 11 v 101 | | | 0/5 | r32 |
| weakhold | 3/7 | mixed | 21 v 22 | 24 v 33 | 22 v 48 | 2/2 | r265 |

### 3.9 DEV vs the other top teams (sample, 12 games each)
- **Vibing++ 9/12.**
  - DEV opens bigger: r60 total 50 vs 34.5, r100 76 vs 52.
  - It out-eats VIB on fresh pearls: r100-199 167 vs 125. Both feed by NoValidAction.
- **FTM 7/12.** Opening r60 52 vs 33.5; even by r300.
- **SSS 10/12.** r400 total 237 vs 96.
- **Sponge 3/5.**
- So against the VIB family DEV wins the opening and the harvest. Against us it wins on waste.

## 4. Our games vs DEV: decisive moments (84 losses, all h1)
Produced by `h2h_dev5.py L` (full rows are in that output). Shapes: **eliminated 40**, **longest dragon 28**, **queen tiebreak with our queen dead 13**, **queen tiebreak with both alive 3** (Portals).

### Eliminations (40)
The pattern: our queen is rammed early, then our mass falls below half of DEV's 10-90 rounds later.

| map | n | queen death (median) | queen L | killer | how | collapse below half |
|---|---|---|---|---|---|---|
| Trophy | 7 | r32 | L3-6 | L2-3, 2-5 steps | | r33-95 |
| Stripes | 6 | r13 | L3 | | vault HitSelf | r39-58 |
| Tower Defense | 5 | r88 | L4-6 | L2-3, 1-4 steps | | r64-127 |
| Queen Of Spades | 5 | r60 | L2-5 | | | r36-156 |
| Autarky | 4 | r51-149 | L5-6 | L3, 2-3 steps | | r51-161 |
| Devil | 4 | r22-65 | | | | r36-72 |
| Prisoners Dilemma | 3 | r9-42 | | | | |
| Default | 3 | r82-333 | | | | |
| weakhold | 2 | r186 / r296 | | | | |

### Longest dragon (28)
Islands 6, Schooltime 7, Australia 4, Around UNSW 3, Slithery 3, Autarky 2, Maze 2, weakhold 1. Behind on total at r300 in 26 of 28.

| game | map | longest at r500 | totals at r300 | detail |
|---|---|---|---|---|
| 1110592 | Islands | 40 v 90 | 94 v 208 | |
| 1112240 | Islands | 15 v 33 | 94 v 214 | |
| 1112503 | Schooltime | 12 v 52 | 14 v 191 | |
| 1116503 | Around UNSW | 36 v 55 | 146 v 294 | |
| 1110591 | Australia | 16 v 46 | 173 v 146 (we led) | our L23/L37/L29 rammed by 3-step lunges at r350/368/467 |
| 1114657 | Australia | 10 v 56 | 170 v 183 | seven of our L12-33 units rammed after r300, five of them by 3-step lunges |
| 1116506 | Schooltime | 52 v 64 | 154 v 226 | eight L10-38 rams after r300 |

### Queen tiebreak, our queen dead (13)
- **Maze 4: crowned queen rammed late.**

| game | queen | round | killer, lunge |
|---|---|---|---|
| 1111432 | L22 | r320 | L9, `NEEE` |
| 1115659 | L41 | r357 | L10, `NNN` |
| 1116320 | L44 | r455 | L6, `SSS` |
| 1114659 | L63 | r449 | L7, `NNEEEN` |

- **Trauma 1111765:** L56 queen rammed at r499 by an L4 with a 4-step lunge (`NEEE`). That lost 0 v 31 on the last round.
- **Slithery 3:**
  - 1112012: L5 queen, r159, an L9 with 5 steps.
  - 1114655: L5 queen, r300, an L26 with 5 steps.
  - 1115346: L5 queen, r168, an L2 with 1 step.
- **Default 2** (r113, r158), **Islands 1** (r144), **weakhold 1** (r265), **Around UNSW 1** (r36, HitSelf).

### Both queens alive (3)
All on Portals: 34 v 49, 30 v 32, 39 v 43. DEV's crowned queen is longer.

### The single biggest recurring gap
Mid-game mass waste, r150-400, from self-inflicted deaths: units boxed in by ally bodies, and first-round child deaths.
- It costs about 127 length per game gross and about 55-65 net, which is the r300-400 total gap.
- It decides the 28 longest-dragon losses and makes the lane-map collapses worse (TD 5x DEV's waste, Devil 3.6x).
- Second: on lane maps our queen is L4-7 and out in the field, and is rammed by r160 (28 of the 40 eliminations: Trophy, TD, Devil, Prisoners Dilemma, Autarky, Queen Of Spades).

## 5. Ranked changes for our bot
"Measure" = what to watch on the server. The unranked loop lets us restrict maps, and DEV games appear to be rating-free for the opponent.

### 1. Stop units being boxed in by ally bodies (all maps; biggest on Around UNSW / Australia / Devil / TD / Schooltime) — param test first, then code
- **Evidence:**
  - 116 vs 84 boxed-by-ally deaths per game (283 vs 204 length).
  - Per map: Around UNSW 762 vs 328, Australia 506 vs 117, Devil 269 vs 80, TD 81 vs 20, Schooltime 449 vs 184.
  - Heads are 30% more crowded (1.54 vs 1.19 ally heads within 3).
  - The maps where our self-waste matches DEV's (Portals, Queen Of Spades, Maze) all have a crowd penalty already. Schooltime and Trauma have one but are still 1.4-1.7x, so the head-only penalty is not enough by itself.
- **Step A (param, map-specific):**
  - Add Around UNSW / Australia / Devil / Tower Defense to the `crowd()` lambda in `applyMapParams` (main.cpp:183-192), with new `PM_AUN_CR`, `PM_AUS_CR`, `PM_DEV_CR`, `PM_TD_CR` = 3.0.
  - The penalty itself is main.cpp:6356-6365 (ally heads within 2 of the destination).
- **Step B (code, flag `ALLY_BOX`, all maps):**
  - `boxEffect()` (main.cpp, about 30 lines before `emitMove`) only scores our head sealing another head.
  - Add a destination check:
    - count the free exits of `t` with ally body segments of `freeT > 1` treated as walls;
    - penalise ≤ 1 exit when another ally head is within 2 of that exit (exit contention);
    - and score sealing an ally head with our body tiles, not just our head.
- **Previously tried:**
  - CROWD_PENALTY=3 was tested all-maps locally under the old rules (0.49) and kept per map.
  - COVERAGE was rejected locally.
  - Neither was server-tested on these maps under the new rules. The new angle is the measured boxed-by-ally waste.
- **Measure:**
  - `selfcause_dev5.py`: boxed-by-ally length per game on those maps (target: halve the gap);
  - units at r100 and total at r200/r300;
  - `ab_mech` `len_ratio_r300`;
  - wins on Around UNSW / Australia / Devil / TD vs DEV / VIB / FTM.

### 2. Stillborn children: SPLIT_NEEDS_EXIT alone, as a defer rather than a ban (code exists; all maps or the 5 waste maps)
- **Evidence:**
  - 50 vs 20 per game (105 vs 51 length). Ours are accidental (HitSelf 37, ally body 13); DEV's are deliberate (NoValidAction).
  - Per map: Around UNSW 298 vs 63, Australia 188 vs 63, Islands 176 vs 37, Devil 129 vs 17, Schooltime 102 vs 25.
  - ROUND2: 91% of growth splits made with no tail exit produce a stillborn child.
- **Code:** the growth-split gate, main.cpp:5777 (`(!SPLIT_NEEDS_EXIT || tailHasExit(2))`).
  - New param `SNE_DEFER` (for example 3): skip the split for at most 3 turns while moving on, then split anyway. This keeps the unit growth whose loss is suspected in c1.
- **Previously tried:** c1 (SPLIT_NEEDS_EXIT + LATE_HUNT + QKILL_KING) lost -9.9 pp, with `len_ratio_r300` x0.66.
  - It was a bundle and never isolated. h1 now carries the other two flags, so a clean A/B is h1 vs h1 + SNE.
- **Measure:** `ab_mech` `stillborn_by_r100` and `stillborn_len_by_r100`; units at r50 and r100 must not fall; `len_ratio_r300`.

### 3. Tip-reversal bulk split, so L5-9 units can harvest dead ends (code, flag; all maps)
- **Evidence:**
  - Bulk splits: DEV 87 per game, VIB 126, us 25. 65% happen at 0 head exits and 27% at 1; 67% at L5-7.
  - DEV's L4-7 / L8+ units eat 87 / 50 fresh pearls per game against our 34 / 22, and DEV holds 23% / 21% of unit-rounds at L4-7 / L8+ in r400-500 (ours 14% / 11%).
  - Against VIB, the harvest is where DEV's fresh-eat lead comes from (r100-199: 167 vs 125).
- **Code:**
  - (a) In the boxed fallback (`bestD < 0`) and when the only exit leads into a region smaller than L: for L ≥ 5 with `tailHasExit(L-2)` and a free unit slot, emit `SPLIT L-2` instead of shedding or dying. `PUMP_TIP_SPLIT` (main.cpp:5623, 5786) does this only inside the growth-split gate, at L4-6.
  - (b) Let `surviveDepth` count "tip split possible" as survival for L ≥ 5, so units enter food pockets. The `DIVE_VALUE` model (params.hpp ~985-1011) is already built.
- **Previously tried:** PUMP_TIP_SPLIT (tip29: Autarky 7/10 vs 6/10, local .449) and DIVE_VALUE (server dv33: tie on Slithery/Autarky) were both tested **before the 1 Oct rule change**.
  - New angle: with ceil(L/4) free steps an L5-8 has 2 free steps, and both top bots do this about 100 times per game.
- **Measure:** bulk splits per game and fresh eats by L4-7 (`agg_dev5.py`); `len_ratio_r300`; the guard is head-on deaths of L5+ units.

### 4. Lane-map queen: stay L2-3 near home (map params; Trophy, TD, Devil, Prisoners Dilemma, Autarky, Queen Of Spades)
- **Evidence:**
  - These maps hold 28 of the 40 eliminations. Our queen is L4-7, 8-15 tiles out, and dies between r20 and r160.
  - DEV's queen there is L2-3, 3-10 tiles from spawn, and survives TD 8/10, Trophy 6/10, PD 6/7, Autarky 6/9.
- **Change:**
  - Turn off the pre-r100 queen economy (`QS_FROM` behaviour) on these maps through a new RuntimeParams field.
  - Use the `RP.queenKeep` mechanism (TROPHY_QSPLIT / PM_QOS_QSPLIT; m3 stages the QoS one) so she splits down to L2-3.
  - Add a home radius of about 6 (no crown, no feeding).
- **Caution:**
  - q1 (park and crown on TD/weakhold) lost; TD eliminations went 8% → 44%. A crowned, fed queen is a target.
  - TROPHY_QSPLIT alone was flat in m1 (64% vs 70%).
  - The new angle is "small and close to home, never fed" (DEV's policy), not park and crown.
  - QS_FROM=100 was a server win overall (v55), so keep it on all other maps.
- **Measure:** queen alive at r100 and r200 on these maps; eliminations; units at r60. Unranked loop on these maps vs DEV / VIB.

### 5. Crowned queen and kings vs 3-6 step lunges (already staged as k1 = QK_EG=2; next QK_EG_KING=1)
- **Evidence:**
  - Maze: 4 queen-tiebreak losses, with crowned L22-63 queens killed at r320-455 by L6-10 units using 3-6 steps (1111432, 1114659, 1115659, 1116320).
  - Trauma 1111765: L56 queen killed by an L4 4-step lunge at r499.
  - In the longest-dragon losses, our L10+ units are rammed after r300 by 3-step lunges again and again (Australia 1114657, Schooltime 1116506).
  - Overall the big-unit exchange is even (21.5 vs 21.8 length per game), so this is mostly about the crowned queen.
- **Code:** `computeThreats` QK_EG block (main.cpp ~3690-3715). Keep k1 next in the queue; then test `QK_EG_KING=1`.
- **Measure:** crowned queen killed head-on after r300 per crowned game; head-on deaths of our L ≥ 10 units from 3+ steps.

### 6. Pearl-aware reach, small units (code, low priority)
- **Evidence:** DEV gets 5.6 kills per game that only reach because of pearls on the path; we get 0.
- **Defence:**
  - The threat model still uses the old-rules reach (visible length - 1; `THREAT_FREE` 0, `KREACH` 0; main.cpp:3640-3700).
  - Add +1 reach per visible pearl on the enemy's shortest path.
- **Attack:** extend `tryRam` (main.cpp:4503; capped at 2 steps) to 3 steps for L3 rammers only when the paid step eats a pearl. This is zero extra length, like the accepted QKILL_FUEL.
- **Previously tried:** LUNGE34 lost (length-paid lunges); the new angle is pearl-funded only.
- **Measure:** kills per game, 3-step kills, `paid_ate`; our small-unit deaths to 3-step lunges.

### Also
- **Ops:** DEV is a good stand-in for the VIB family (it beats VIB 74%), and our loop games appear rating-free for us. Keep the unranked dev loop for mechanism checks of items 1-4.
- **Not re-proposed:** QS_FROM changes outside the lane maps, Portals early crown (PM_POR_EARLY failed locally), Schooltime B (server loss), QEXIT_LOOK, QK_BIG, MATCH_STRICT.

## 6. R8 local build of fixes 1-3 (2026-10-05)
Four flags in bot/, all default 0. With all flags off, bot/ plays identically to variants/f1 (sandbox seed 1000, both sides, Australia/Devil/Portals/QoS: 8/8 SAME).
Method: 6 seeds x both sides vs f1 per map (12 side-games). Baseline is f1 vs f1 on the same seeds, with both sides counted. Ledger as in `selfcause_dev5.py`. Script: scratch r8/qp8.py, logs in r8/*.log.
Self-play is noisy at n=12. Treat these as mechanism checks only.

| flag | what | boxed-by-ally len/game | stillborn len | t100 | t300 | verdict |
|---|---|---|---|---|---|---|
| base f1 | | AUN 698, AUS 400, Dev 143, TD 71, Sch 512 | 227 / 177 / 67 / 24 / 99 | 127 / 92 / 39 / 27 / 86 | 171 / 158 / 56 / 41 / 180 | |
| CROWD_MAPS (bitmask 1 AUN, 2 AUS, 4 Devil, 8 TD; value 3; 16 = Schooltime 3 -> 5) | crowd penalty per map | AUN 479, AUS 367, Dev 53, TD 87, Sch 345 | 128 / 137 / 26 / 29 / 81 | 130 / 98 / 28 / 37 / 64 | 180 / 173 / 31 / 56 / 130 | **AUN and AUS kept** (waste down, mass up). Devil cuts mass (t100 -29%). TD waste goes up. Schooltime t100 -26%. **Staged: cm_pack = 3, cm_aun = 1, cm_aus = 2** |
| ALLY_BOX=1 | penalise steps to t with ≤1 exit when an ally body (freeT > 2 - ABX_SLACK) takes an exit; +25 if another head is within 2 of the last exit | 595 / 321 / 100 / 62 | 176 / 175 / 45 / 21 | 124 / 77 / 34 / 31 | 179 / 117 / 35 / 40 | box -15..-30% on all 4 maps, but 4-map t300 -13% (Australia -26%, Devil -37%). Fails. The no-exit-only variant (PEN1=0, CONT=0) is weak and mixed. SLACK=0 gives the same result. Not staged. |
| SPLIT_DEFER=3 | growth split waits ≤3 turns for a tail exit | 870 / 418 / 125 / 76 | **183 / 106 / 27 / 11** | 142 / 84 / 34 / 25 | 185 / 147 / 54 / 37 | stillborn length -20..-60% on every map. 4-map t100 and t300 flat (71.4 vs 71.2, 105.8 vs 106.3); AUN boxed goes up. **Staged: sdf** |
| TIP_REV=3 (and TR_NET=1 TR_DEPTH=8) | L≥5 non-queen: split L-2 when best depth < TR_DEPTH; surviveDepth counts tip split after eating TR_NET | ≈ base | ≈ base | identical | ≈ base | Inert: our units split at L4, so non-queen L≥5 exists only after split stop or as kings. t100 is bit-identical. A real test needs a larger SPLIT_LEN first. Not staged. |

CPU max on maps/sprint/australia.map with each flag on: 34.0-34.2M (trv2 37.0M).
Suggested server order:
1. cm_pack: unranked loop on Around UNSW + Australia vs DEV/VIB; judge boxed-by-ally waste and r300 length.
2. sdf: all maps; this is the isolated version of c1's SPLIT_NEEDS_EXIT; judge stillborn and `len_ratio_r300`.
