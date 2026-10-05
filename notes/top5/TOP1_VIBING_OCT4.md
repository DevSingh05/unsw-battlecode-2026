# #1 Vibing++ and #2 "dev test 1 :P" vs our builds, last 24 h (4 Oct 01:00 → 5 Oct 02:00 UTC)

Written 5 Oct ~02:20 UTC (4 Oct 22:20 EDT). Read-only study: nothing in `bot/` or `variants/` changed, nothing submitted, no challenges.

## Data and tools
- Listings: `replays/top1_vib/games_306.json` (1,610 Vibing++ games vs the top 17 teams since 4 Oct 01:00 UTC), `games_545.json` (1,425 dev test 1 games since 07:00 UTC).
- Replays: 191 in `replays/top1_vib/` (`sample.json` lists them).
  - Vibing++ (VIB): every game vs us since 01:00 UTC (102), plus 4 per other top team since 14:15 UTC (58).
  - dev test 1 (DEV): every game vs us since its new build (15), plus 2 per opponent (18).
- Our build per game comes from upload times with a 300 s grace, as in ab_server: v61 → v69 02:25 → v61 04:26 → c1 17:13 → m1 18:30 → m2 20:07 → b1 22:47 → q1 23:34 UTC. Games inside a grace window are marked `amb`.
- Scripts are in `notes/top5/new_rules_tools/`:
  - `fetch_vib4.py`, `sample_vib4.py`: crawl listings and download replays.
  - `an_vib4.py` + `an_vib4_extra.py`: per-game rows. Rows are in scratch `vib4/rows_vib4.pkl`.
  - `agg_vib4.py`: team tables (output in scratch `vib4/agg.out`).
  - `h2h_vib4.py`: decisive moment per game.
  - `mid_vib4.py`: mass ledger per 100 rounds.
  - `mob_vib4.py`: unit size mix and mobility.
  - `trace_vib4.py`: round-by-round trace of one game.
- "New builds" means m1/m2/b1/q1 (all with the Portals/Maze queen park); "old builds" means v61/v69/c1.

## 1. Who they are
- **Vibing++ = team 306 = Cutlery renamed** (spoon, fork, ldauth). Lifetime record 19015-4-9448, peak 2379, now 2317.
  - On 3 Oct it switched at 17:08:33 to a submission rated 1388, and back to ~2331 at 17:48 UTC.
  - Since then the rating history (617 points, `GET /api/v1/teams/306`) has no step change. There are short bursts of large swings, typical of a fresh upload's extra ±75 sigma, at about **06:15, 09:35 and 14:15 UTC 4 Oct**. These are probably new uploads, but other teams' submissions are not visible.
  - Win rate vs the top 17 is flat across those windows: 61%, 57%, 63%, 62%. Overall 982/1603 (61%).
  - The leaderboard `elo` in game listings is the current rating, not the rating at game time, so it cannot date their switches.
- **dev test 1 :P = team 545, an organiser DEV team.** `dev: true`, not eligible. One member, `lmkae1` (UNSW). Description: "devs will fly you to sydney". Lifetime 32639-8-14324.
  - It is not a renamed student team. Its rating sat flat at ~1800-1870 from 1 Oct 12:31 to 4 Oct 09:04 UTC. Then a new build took it 1810 → 2185 between 09:04 and 10:26 UTC 4 Oct; it has drifted to 2297 since.
  - Most of its games are unranked challenges from bread first search (926 since 09:05). It played 140 ranked games.
  - Since 09:05 it is 882/1300: vs VIB 14/30, vs forgot to mention (FTM) 79/130, vs SSS 10/20, vs us 10/15.
  - Fingerprint: the same family as VIB.
    - Feeds by NoValidAction: 286 per game (VIB 264; us 0, we feed by HitSelf, 208 per game).
    - 29% of its r100-300 splits are "bulk" splits, where the child takes L-2 (VIB 35%, FTM 8%, us 5%).
    - Unlike VIB it has some HitSelf deaths (18 per game).
- **All 15 of our games vs DEV were ranked challenges from our own loop**: 13:42 v61 (5), 17:13 v61/amb (5), 23:27 b1 (5). We went 5-10. If ranked games against dev teams count for rating (open question #3 in RULES), the loop is feeding rating to an ineligible bot.

## 2. Record vs us, last 24 h (listing, our wins / games)
- **By our build:**

  | build | our wins / games |
  |---|---|
  | v61 | 19/35 |
  | v69 | 3/10 |
  | c1 | 3/5 |
  | m1 | 3/10 |
  | m2 | 1/17 |
  | b1 | 4/10 |
  | q1 | 5/10 |
  | amb | 3/5 |

  - m1/m2 played VIB mostly on the unranked loop maps (Portals, Maze, Stripes, Trophy), so m2's 1/17 is a map-mix effect, not a build verdict.
- **By map, all builds:**

  | map | our wins / games |
  |---|---|
  | Stripes | **0/7** |
  | Queen Of Spades | **0/6** |
  | Around UNSW | 0/3 |
  | Islands | 0/2 |
  | Schooltime | 1/7 |
  | Maze | **2/12** |
  | Autarky | 1/4 |
  | Portals | 4/11 |
  | Trophy | 4/9 |
  | Tower Defense | 2/4 |
  | Slithery Fight | 3/6 |
  | Australia | 5/8 |
  | weakhold | 5/8 |
  | Default | 3/4 |
  | Devil | 3/3 |
  | Prisoners Dilemma | 3/3 |
  | Trauma | 5/5 |

- **VIB's own map profile vs the top 17** (VIB's win rate):
  - Weak: Trophy 33%, Tower Defense 35%, Prisoners Dilemma 48%, Portals 50%, Slithery Fight 54%, weakhold 58%.
  - Strong: Autarky 89%, Around UNSW 80%, Stripes 77%, Queen Of Spades 73%, Maze 71%.
- **New builds vs VIB, replay sample (47 games): 28% wins.**
  - 18 eliminations (we won 2).
  - 29 round-500 finishes: longest dragon 6 W / 9 L, queen tiebreak 5 W / 9 L.

## 3. Vibing++ profile (medians; "vs us" = 102 games, "vs top" = 58 games after 14:15)

### Opening (first 60 rounds)
- **Queen:** splits early (first split r10; 26-34% split at r0-1; 14-24% never split). She stays L3 and roams about 10 tiles from spawn by r30-60.
- **VIB is not bigger early.** Against us at r60 it has 12.5 units and total 30; we have 18 units and total 46.
- Its heads are about 70% in its own half at r60 (9.5 own / 4.3 enemy half), and it eats 24-27% of its r0-60 pearls in our half.
- **Per map, our opening is equal or ahead** on 13 of 17 maps (r60 total: Australia 56 v 34, Portals 54 v 34, Devil 35 v 14, Trauma 32 v 23).
- **Exceptions:**
  - Stripes: r60 total 9.5 v 29.5, r100 6 v 53.
  - Around UNSW: r100 116 v 152.
  - Queen Of Spades: units r60 6 v 7, r100 total 20 v 32; our queen dead by r100 in 7 of 9 games.

### Queen handling
- Alive at the end in 38% of games (48% of r500 games). Median death r112 vs us, r124 vs top.
- **Death causes vs us:** enemy head-on 40, **own NoValidAction 19**, other 4.
  - In 31 of 159 games the VIB queen kills herself at L2-3 (NoValidAction, its feeding move).
  - This happens mostly after our queen is already dead, but **6 of 15 times on Portals with our queen alive**. VIB lost those games (e.g. b1 1087067, 56 v 0).
- **Crowning and growth:**
  - Queen is the king at the end in 20-26% of games.
  - Queen length of survivors on **Portals**: r250 7 → r275 16 → r300 32 → r400 50 → r450 56.
  - Ours (m2/b1 park): r300 3 → r325 12 → r400 32 → r475 42.
  - Maze: 12 at r200 → 33 at r400 → 56 at r475.
  - Schooltime: she stays L3 all game (12/12 alive). VIB wins there on longest dragon with twice our total.

### Economy (per game, VIB vs us in the same games)
- **Mass ledger, new builds vs VIB (47 games):**

  | rounds | fresh eats: us / VIB | eats in the enemy half: us / VIB |
  |---|---|---|
  | r0-100 | 103 / 100 (even) | |
  | r100-200 | 116 / 141 | 72 / 85 |
  | r200-300 | 105 / 133 | 74 / 98 |
  | r300-400 | 85 / 116 | |

  - VIB eats about 85 more fresh pearls over r100-400, mostly in our half.
  - Recycling waste is even: our HitSelf + ally-body mass 161 per 100 rounds vs VIB NoValid + ally 158. Own-corpse recovery is also even.
- **The gap is unit size (`mob_vib4.py`, r100-300):**
  - Unit-turns are equal (5,700 per game each).
  - VIB spends 16% of unit-turns at L4+ (L4 5%, L5-8 8%, L9+ 3%); we spend 7%.
  - VIB's L4+ units eat 9.4-10.6 fresh pearls per 100 turns; ours eat 5.7-6.3.
  - **Fresh eats by L4+ units: VIB 92 per game, us 24.** L2-L3 eats are equal (182 v 197).
- **How VIB holds mass in big units:** the same number of splits (about 180 per game in r100-300), but 35% are bulk splits.
  - Split mix: L5→k3 26, L6→k4 15, L7→k5 8, L8→k6 7, L9→k7 5.5, L10→k8 3.5 per game. The parent keeps 2, and the child takes the bulk and leaves from the old tail.
  - Ours: 95% are L4→k2 (153 per game). So VIB units are allowed to grow to L5-11, harvest with 2-3 free steps, then throw off a big child.
- **Curves vs us:** units r100/200/300 20 / 34.5 / 46; total 54 / 89.5 / 110 / r400 168.
- **Largest unit:** first L8 at r103, L10 at r160, L15 at r258, L20 at r322. Ours: r264, r304, r323, r333.

### Kills
- **Per game vs us: 31 kills.**
  - By steps: 1-step 10.6, 2-step 14.1, 3-step 6.0, 4-step 0.3.
  - 20 of the 31 use paid steps; 7.7 of those ate a pearl on the path, which refunds the paid step.
  - Plus 25 paid moves that kill nothing (9.4 of them eat).
- **Ours vs VIB: 25 kills per game, 3-step kills 0.02.**
- **Our L>=10 units killed head-on by VIB:** 37 in 47 new-build games. **29 of 37 (78%) came from lunges of 3+ steps** (3: 16, 4: 11, 5: 2), killers L3-L13.
- **Queen kills:**
  - VIB kills our queen in 57% of games.
  - Early (r21-70), these are L2-3 rammers with 1-2 steps.
  - Later, these are L5-13 hunters that close to 3-5 tiles over 3-4 rounds and lunge 4-5 steps.

  | game | map | round | our queen | killer |
  |---|---|---|---|---|
  | 1082238 | Maze | r394 | L51 | L9, `NNWN` from 3 tiles |
  | 1079634 | Maze | r376 | L37 | L6, `EESS` |
  | 1072274 | Maze | r325 | L25 | L6, 5 steps |
  | 1086125 | Maze | r228 | L6 | L12, 5 steps from 2 tiles |
  | 1093732 | Around UNSW | | L6 | L7, 4 steps |
  | 1089975 | Around UNSW | | L6 | L13, 4 steps |
  | Slithery Fight q1 games | Slithery Fight | r315 / r319 | L25 / L33 | 5-step / 4-step lunges |

### King timing, feeding, endgame
- Feeding is by NoValidAction suicides: 237 per game vs us (r100-400 about 50-62 per 100 rounds).
- Their final king eats 9 own-corpse pearls after r250, and 3 fresh.
- **r500 games vs us (all builds), from VIB's side:** queen W 18 / L 12, longest W 18 / L 15.
- Big late king rams decide several games: our L>=10 units are rammed after r400 in 9 of the 26 losses listed below.

### Portals
- 181 crossings per game, vs our 148. No material difference.

## 4. dev test 1 profile (lighter: 15 games vs us, 18 vs others)
- **Opening:** bigger than VIB.
  - Vs top teams: r30 14 units / total 36; r60 24.5 / 64.5.
  - Vs us: r60 10 units / total 24.
- **Queen:** first split r9-18; 22-27% never split; she grows to L4-6 by r100.
  - She is the king at the end in 40% of games vs us. Survivor lengths at r500 are 32-38.
- **Kills:** 49 per game vs us, 134 vs top.
  - 3-step kills 5.2 per game; 4+ step kills 1.9 per game vs top.
  - Our L>=10 units die head-on 0.67 per game vs DEV.
- **Wins:**
  - All 7 eliminations vs us. Typical pattern: Queen Of Spades x3, Autarky x2, Devil, Stripes (our queen rammed r21-144, collapse r42-214).
  - r500 vs us: 3 W / 5 L. We win Trauma and Australia, and Slithery/weakhold on longest dragon.
- **Same weak maps for us as vs VIB:** Queen Of Spades 0/3, Autarky 0/2, Stripes 0/1 (queen r13 HitSelf), Portals 0/1 (v61 queen r22 HitSelf).

## 5. Head-to-head: decisive moment per game (b1, q1 and v61 vs VIB; all our builds vs DEV)
Auto-classified from replays (`h2h_vib4.py ... md`). "sN" = killer's steps, "dN" = distance from the dead queen's spawn.

### b1 vs VIB (4/10)
| game | map | res | decisive moment |
|---|---|---|---|
| 1086124 | Queen Of Spades | L | our queen r64 rammed (L6 by L3, s2); we fall below half their mass at r64 (r100 total 20 v 32); eliminated r232 |
| 1086125 | Maze | L | queen tiebreak 0 v 95: our queen (L6) r228 lunged by an L12 from 2 tiles, 5 steps |
| 1086127 | Portals | L | longest 40 v 49 with both queens dead (our parked queen died r409 HitSelf at L2); r300 longest 4 v 37 |
| 1086128 | Stripes | L | our queen r13 HitSelf in the vault (L3); below half mass r43; r100 total 7 v 54; eliminated r111 |
| 1087063 | Maze | L | longest 8 v 86; r300 total 97 v 195; our L26/L13/L24 units rammed r449-496 (3-9 step lunges) |
| 1087065 | Stripes | L | queen r13 vault HitSelf; our pump units keep dying in the vaults at (21,10)/(6,1); 6 v 20 units at r100; eliminated r165 |
| 1086126 | Trauma | W | queen tiebreak 56 v 26 |
| 1087064 | Trophy | W | eliminated them r256; their queen rammed r80 |
| 1087066 | Australia | W | longest 73 v 23; r300 total 241 v 83 |
| 1087067 | Portals | W | queen tiebreak 56 v 0: VIB queen self-NoValid at r166 |

### q1 vs VIB (5/10)
| game | map | res | decisive moment |
|---|---|---|---|
| 1089974 | Tower Defense | L | parked queen r159 lunged (L6 by L7, s4); r100 total 12 v 54; eliminated r159 |
| 1089975 | Around UNSW | L | longest 22 v 109; queen r175 lunged (L6 by L13, s4); r300 total 118 v 302; four L16-25 rams after r400 |
| 1093729 | weakhold | L | collapse r81 (r100 total 20 v 46); queen killed r382; eliminated |
| 1093731 | Tower Defense | L | r100 total 5 v 46; parked queen r268 rammed; eliminated r395 |
| 1093732 | Around UNSW | L | queen tiebreak 0 v 22: queen r225 lunged (L6 by L7, s4) |
| 1089972 | weakhold | W | queen tiebreak 16 v 0 |
| 1089973 | Australia | W | longest 81 v 21 |
| 1089976 | Slithery Fight | W | longest 97 v 61 (our queen L33 lunged r319, s4) |
| 1093730 | Australia | W | longest 57 v 35 |
| 1093733 | Slithery Fight | W | longest 61 v 21 (queen L25 lunged r315, s5) |

### v61 vs VIB (19/35)
Losses:

| game | map | decisive moment |
|---|---|---|
| 1003777 | Australia | queen r38 dead, 0 v 41 |
| 1004048 | Australia | queen r51 HitSelf, 0 v 25 |
| 1014944 | Slithery Fight | queen r218 HitSelf, 0 v 69 |
| 1014945 | Portals | queen r13 HitSelf, 0 v 51 |
| 1014947 | Maze | queen r86 rammed, 0 v 138 |
| 1003779 | Autarky | eliminated (queen r146) |
| 1039132 | Autarky | eliminated (queen r52, 3-step) |
| 1004051 | Queen Of Spades | eliminated (queen r108) |
| 1039135 | Queen Of Spades | eliminated (queen r77) |
| 1014946 | weakhold | eliminated (collapse r71) |
| 1018352 | Trophy | eliminated (queen r42, out by r79) |
| 1004052 | Around UNSW | longest 40 v 74 (L33 rammed r410) |
| 1014582 | Maze | longest 8 v 89 |
| 1044395 | Maze | longest 65 v 95 (r300 total 96 v 185) |
| 1044396 | Australia | longest 29 v 37 (L20/L21 rammed r415/433) |
| 1014584 | Portals | longest 28 v 45 |

Wins:
- Eliminations: Default x2, Tower Defense, Devil, Trophy, Prisoners Dilemma.
- Queen tiebreak: Trauma x3, weakhold x3.
- Longest dragon: Australia x2, Portals x2, Slithery, Maze 24 v 22, Schooltime 69 v 59.

### All builds vs DEV (5/15)
Losses:

| game | build | map | decisive moment |
|---|---|---|---|
| 1087069 | b1 | Devil | queen r21 rammed (L5 by L2, s1); eliminated r73 |
| 1087070 | b1 | Islands | queen r283 HitSelf; 0 v 66 |
| 1087071 | b1 | Queen Of Spades | queen r82 rammed (L6 by L3, s2); eliminated r275 |
| 1087072 | b1 | Autarky | queen r144 rammed (L6 by L4, s3); eliminated r446 |
| 1050072 | v61 | Queen Of Spades | queen r56; eliminated |
| 1064179 | v61 | Queen Of Spades | queen r131 (3-step); eliminated |
| 1050073 | v61 | Autarky | eliminated |
| 1050074 | v61 | Portals | queen r22 HitSelf; 0 v 32 |
| 1064182 | v61 | Stripes | queen r13 vault HitSelf; eliminated r115 |
| 1064180 | amb | Around UNSW | longest 48 v 76 (L46 rammed r410 by a 10-step lunge) |

Wins: Trauma x2 (queen), Australia, Slithery Fight and weakhold (longest).

### Loss pattern over the 26 b1 + q1 + v61 losses to VIB
- **10 eliminations:** Queen Of Spades 2, Stripes 2, Tower Defense 2, Autarky 2, weakhold 2, Trophy 1. The queen is rammed between r13 and r159 and our mass collapses between r43 and r101.
- **7 queen-tiebreak losses with our queen dead:**
  - 2 by 4-5-step lunges on Maze / Around UNSW.
  - 4 by HitSelf / HitOther (Australia x2, Slithery, Portals r13).
  - 1 early ram (Maze r86).
- **9 longest-dragon losses:** Maze 3, Around UNSW 2, Portals 2, Australia 1, plus one more. Mass deficit at r300 is about 0.5x, and 5 of these games have L>=13 units rammed after r400.

## 6. Ranked changes for our bot
Gains are not estimated; "measure" says which numbers to watch.

### 1. KREACH for the queen and kings: lunge-aware threat reach (flag + params, all maps)
- **Evidence:**
  - 29 of 37 of our L>=10 head-on deaths vs VIB came from 3-5-step lunges.
  - Crowned or parked queens were killed by these lunges in 4 Maze games (1072274, 1079634, 1082238, 1086125): 2 queen-tiebreak losses (0 v 65 twice) and 2 longest losses. Also Around UNSW 1093732 / 1089975 and Tower Defense 1089974 (q1 parked queen).
  - The killer closes from 6-7 tiles to 2-3 over 3-4 rounds; our queen walks towards it (1082238: an L51 queen steps toward an L9 at 3 tiles).
- **Code:** `computeThreats()` (main.cpp ~3584) and the reply penalty (~4870), using the built stage `P6_kreach` but with **`KREACH_QUEEN=1`**. Default `KREACH_MINLEN=8`; for the queen apply it once she is crowned (`RP.queenKing` / qPark maps) or at L>=8. The `P6_reach` params (`THREAT_TAIL_UNKNOWN=4`, `KING_THREAT_REACH=6`) go with it.
- **Previously:** QKREACH (queen-only) was rejected locally and never server-tested. The new angle: with the queen park live, this is the main way the parked queen now dies, and the server data above is specific to it.
- **Measure (ab_mech):**
  - Queen alive at r500 on Portals/Maze/q1 maps.
  - Head-on deaths of our L>=8 units from 3+ steps, per game. Target: halve the 0.8 per game.
  - Guard: the r300 length ratio must not fall.

### 2. Portals: crown and feed the parked queen ~60 rounds earlier (param, Portals only)
- **Evidence:**
  - With both queens alive at r500 we lose the length race: 1075993 (41 v 62), 1079633 (21 v 57), 1080365 (48 v 57), 1082237 (49 v 62).
  - VIB's queen is 7 at r250, 16 at r275, 32 at r300 and 56 by r450. Ours is still 3 at r300 and 42 at r475.
  - VIB funnels nearly all mass into her: total about 60 at the end, queen about 57. Ours: total about 70, queen about 45.
- **Change:** main.cpp:206 `v2("Portals", 250, 360, 300, 3)` → try seed 220 / split stop 300 / feed start 240. Check that `PM_POR_KS 330` (params.hpp:287) is not what actually sets her crown round; if it is, set it to about 240.
- **Measure:** Portals unranked loop. Our queen length at r300/r400/r500 (target ≥ 25 at r300 and ≥ 55 at r500) and wins vs VIB/DEV. Guard: queen alive at r500 must stay at about 85%.

### 3. Harvester units: let some units grow to L5-9 between r100 and r350, then make bulk splits (code, flag, all maps)
- **Evidence:**
  - VIB out-eats us by about 85 fresh pearls over r100-400.
  - The whole gap comes from L4+ units: 92 vs 24 fresh eats per game in r100-300. They hold 16% of unit-turns vs our 7%, and eat 10 vs 6 per 100 turns.
  - 35% of VIB's mid-game splits are bulk splits (child = L-2 at L5-11); ours are 95% L4→k2. DEV does the same (29%).
  - Our total length vs VIB at r300 is 90 v 110 (new builds), and our longest at r300 is 6.5 v 12.5.
- **Code:** growth-split gate at main.cpp ~5736 (`myLen >= SPLIT_LEN`).
  - New flag, for example `HV_FRAC=3` / `HV_LEN=8` / `HV_FROM=100` / `HV_TO=350`. Units with `myId % HV_FRAC == 0` skip the growth split until `HV_LEN`, then split with `k = myLen-2` (bulk child), unless threatened or boxed.
- **Previously:** HARVEST (v62, big maps) was rejected locally only (.426; harvesters died or split before growing). It was never server-tested. The new angle is VIB's measured split mix.
- **Measure:** `mob_vib4.py` share of L4+ unit-turns, fresh eats r100-300, ab_mech `len_ratio_r300`. Mechanism gate first (about 150 games).

### 4. Stripes: stop the r13 queen vault dive and cap pump dives vs strong teams (map-specific, code)
- **Evidence:**
  - Stripes vs VIB 0/7 and vs DEV 0/1, all eliminations.
  - b1 queen dies r13 HitSelf in the vault in both b1 games and in the v61 game vs DEV.
  - Pump units die in the (21,10)/(6,1)/(2,1) vaults all game (1087065: 12+ vault HitSelf deaths by r100). We have 6 units v 20 at r100; r100 total 3-22 v 41-65.
  - VIB's queen never dives; she roams L2-4.
- **Caveat:** ROUND2 found that ladder rating on Stripes tracks the dive (good vs the field). Test only as "dive and pump unless enemy heads have been seen in our half by r10" or as a pump-unit cap (`pfDiveOK`, main.cpp:4092; Stripes module). Low priority; 1 of 17 maps.

### 5. Queen Of Spades: earlier queen split (param via `RP.queenKeep`, as `TROPHY_QSPLIT`)
- **Evidence:**
  - Queen Of Spades vs VIB 0/6 and vs DEV 0/3, all eliminations.
  - Our queen grows to L6-8 before her first split (r42 in 1086124) while VIB splits at r10. In that game we had 3 units v 6 at r30 and 4 v 9 at r50.
  - Our queen is dead by r100 in 7 of 9 games.
- **Caution:** v44 was 23-3 on Queen Of Spades vs the field. Test unranked vs the top panel only. Low-medium priority.

### 6. Ops: drop dev test 1 from the ranked challenge panel (no code)
- 15 ranked challenge games vs an ineligible dev team; we went 5-10.
- Whether dev games move our rating is unconfirmed. If they do, they cost rating for nothing; if they don't, they are wasted challenge slots.
- Keep it for unranked mechanism tests, since it plays like VIB.

### 7. q1 caution on Tower Defense / weakhold vs strong teams (data point for the q1 verdict)
- q1 vs VIB on Tower Defense: 0/2, both eliminations.
  - r100 total 12 v 54 and 5 v 46.
  - The parked queen was lunged at r159 and rammed at r268.
- weakhold 1/2. Australia 2/2 and Slithery Fight 2/2 are fine.
- Small n; weigh it in the q1 per-map check.

### Not re-proposed
- **LUNGE34** (server loss -6.8 pp). VIB's lunges are partly pearl-refunded (7.7 kills per game). The queued f1 `QKILL_FUEL` covers the zero-cost angle for queen kills; extend it to all kills only if f1 wins.
- **QEXIT_LOOK and QEARLY_PEN** (server losses). Early queen rams by L2-3 units are still our biggest early leak: median death r67, 29 of 35 deaths are enemy rams. No new angle found.
- **PM_SCHB** (Schooltime B, server loss). VIB wins Schooltime on 2x total with an L3 queen; we are 1/7 there; no fix identified.

## 7. Watch list
- VIB uploads probably came at about 06:15, 09:35 and 14:15 UTC 4 Oct (rating-volatility bursts). Its behaviour vs the field is unchanged in win rate.
- DEV is a fresh organiser build (09:04 UTC 4 Oct) of the VIB/FTM family. Expect it to stay in the top 3 while it is ranked; it cannot enter the Qualifier.
