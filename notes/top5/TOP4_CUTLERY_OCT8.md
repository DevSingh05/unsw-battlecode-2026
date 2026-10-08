# Cutlery (306, #4 at ~2437): current build, games vs b4/kf1, harness-checked loss causes (8 Oct)

Written 8 Oct, about 04:00-05:30 UTC (00:00-01:30 EDT). This was a read-and-replay study only.
- Nothing in `bot/` or `variants/` changed. Nothing was submitted, no challenges were run, and no local games were played.
- The prototype is in scratch `top4/cutlery/bot/`: the b4 submission zip 18751 plus `QSTALK` bit 4 (ported from `vib5/bot`, default 0).

Scratch dir: `/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/cutlery/`

## 0. Data
- **Listing:** `replays/top4_cutlery/games_306.json`, 3652 Cutlery games from 6 Oct 14:00 UTC to 8 Oct 04:10 UTC. Crawled with scratch `fetch.py`.
- **Replays:** 60 in `replays/top4_cutlery/`, chosen in `sample.json`:
  - all 10 games vs us in that window: 5 on b4 (8 Oct 02:39 UTC) and 5 on kf1 (7 Oct 09:33);
  - 50 vs top teams, spread over maps: aAah 12, FTM 12, larp 8, SSS 8, DEV 5, glyph 5.
- **Rows:** scratch `rows.pkl`, built by `an_cut.py` (a wrapper of `an_vib4.analyse`). The profile table comes from `agg_cut.py`.
- **Harness:** batch runner `vp.py` (from vib5, with kf1/b3 flag mapping), list files `all.txt`, `vib5_all.txt`, `panel.txt`, results in `v/<label>/`.
- **Harness fidelity, flags off, queen turns:** 100% on every game: 9/9 vs Cutlery, 66/66 in the b4 panel, and 48/48 vib5 b3-equivalent games. The exception is Queen Of Spades, whose 2nd layout is not fitted.

## 1. Who they are and whether the build changed
- Cutlery = Vibing++ under its old name again; the listing has shown "Cutlery" since at least 6 Oct 12:00 UTC.
- **6 Oct 12:00-22:45 UTC: 0 wins in 202 games**, including ranked losses to 670-1600 teams. This is their usual broken/test-build window (same pattern as 5 Oct 22:06).
- **Strong build back at 6 Oct 22:48 UTC**, starting with a challenge series vs aAah. Since then the win rate per 3 h block is 58-69% and the rating is 2436-2448 (now 2437).
- Nothing in the listing points to another switch since 22:48. The sample's two halves differ (win 0.67 → 0.41, feeding and splits up), but map and opponent mix confound that, so I don't call it a change.
- **This is a different build from the 5 Oct VIB one.** Medians vs top teams, Oct 8 vs Oct 5:
  - NoValidAction feeding 71 vs 222 per game;
  - splits 210 vs 282 per game;
  - first L10 at r134 vs r171;
  - units at r300 44 vs 51.5.
- **Listing win rate vs top teams** (36 h): FTM 190/390, aAah 152/348, SSS 142/250, larp 86/207, glyph 68/160, DEV 26/61, us 5/10.

## 2. Current play (Cutlery-side medians; vs us n=10, vs top n=50)
| metric | vs us | vs top | VIB 5 Oct vs top |
|---|---|---|---|
| win % (sample) | 50 | 56 | 39 |
| queen first split | r4 | r8 | r8 |
| queen alive at end / median death | 30% / r97 | 30% / r77 | 26% / r94 |
| queen length alive r100/200/300 | 3/6/11 | 3/3/3.5 | 3/5.5/11 |
| units r50/100/200/300 | 8.5/17/23/21 | 10.5/21/34.5/44 | 10.5/22/41.5/51.5 |
| total r50/100/200/300 | 19.5/44/55/61 | 26.5/50/92/112.5 | 25/53/110/149 |
| opponent total r100/200/300 | 69/102/107 | 50/89/127 | 54/111.5/96 |
| longest r100/200/300/400 | 4/4.5/11/15 | 4/6/10/23 | 4/9/9.5/14 |
| first L10 / L20 | r123 / r231 | r134 / r268 | r171 / r407 |
| kill steps 1/2/3/4+ (mean per game) | 9.6/12.9/6.2/0 | 15.5/13.9/6.6/0.2 | 15.7/12.7/5.7/0.1 |
| paid kills / paid kills that also ate | 18.7/5.5 | 20.1/7.8 | 18.4/6.3 |
| enemy queen killed by Cutlery | 30% | 64% | 57% |
| NoValidAction feeding per game | 152 | 71 | 222 |
| splits per game / stillborn by r100 | 191/2 | 210/1.5 | 282/1 |

- **Queen policy: expendable worker, not a plan.**
  - She splits at L4 like any unit: 32 of 54 first splits are at L4, 14 at L5. 12 of 60 games split her at r0 (Slithery L26 spawn coil, Schooltime, Maze, Trauma, Default). She never splits in 6 games, and first splits after r100 in only 2.
  - She dies in 70% of games: 22 by enemy head-on (11 before r100, 11 after), 15 by NoValidAction (8 early), 5 HitOtherBody.
  - She is the king at the end in 9/60.
  - Half of her eats are own corpses (309/608).
  - **No queen hunt:** Cutlery heads within 4 of the enemy queen average 0.1-0.3 per sampled round, about the same as near any other enemy head.
- **They play for elimination.**
  - 31 of 60 games ended by elimination; Cutlery won 20 of those.
  - At r500 they won only 13 of 29: 8/13 with both queens dead, 3/8 with both alive, 0/6 with their queen dead and the opponent's alive, 2/2 the reverse.
- **Fighting and food:**
  - 2+ step moves on 47% of L5-8 turns and 62% of L9-16 turns.
  - Paid moves: 41 per game (16 eat, 20 kill). Ours in the same 10 games: 11.5 per game, almost all kills.
- **Portals:** median 90-116 crossings per game on portal maps, against our 56 in the same games.
- **Endgame:**
  - Late big deaths (L5+, r300+) are mostly NoValidAction feeding (227) and head-on (186).
  - At r400 their longest is only 15-23. They are beatable on the longest tiebreak whenever both queens die.
- **Per map vs top** (Cutlery W/n):
  - strong: AUNSW 4/4, Default 3/3, Devil 2/2, TD 2/2, Stripes 3/4;
  - weak: PD 0/4, Australia 0/2, Islands 0/1, Maze 1/3, Slithery 1/3.

## 3. Our games vs the current build: 5-5
| game | build | map | result | how it was decided | our decision at the decisive moment |
|---|---|---|---|---|---|
| 1410024 | b4 | Portals | L r500 | **Their queen died r25.** Our crowned queen was L48 at r460 (their longest 37), then was boxed and shed 2 per turn from r462 to death at r485 (HitSelf L3). Longest 11 vs 47. | Harness MATCH r446-461. From r448 every candidate has depth 3-6 inside her own coil near (3-9,4-12). At r456 E t=(7,6) shows area 115 / depth 6; one turn later the best area is 6. r461 W through the portal to (22,10), area 1, the only candidate. This is the known Portals crowned-coil collapse (UNDERSTANDING: time-aware area assumes the tail retracts). Not a cheap fix (k2 and pb2 already lost). |
| 1410022 | b4 | QoS | L elim r244 | Economy stall: 6-8 units and total 17-20 from r50 to r200 while theirs grew 7 → 22 units. Queen boxed, HitSelf r28 at L2 with no enemy within 9. | Not checkable: the 2nd QoS layout is unfitted and the rebuild diverges at r7. |
| 1410021 | b4 | Trophy | L elim r145 | Queen L5-6 foraged for 12 rounds with enemy L2-3 heads 1-5 tiles away; killed r46 by an L3 head-on. Units r100 14 vs 24. | r46 free path NN to (10,10), threat=0, score 12.45. The L3 that was 4 tiles away at r45 lunged in. |
| 1333036 | kf1 | Devil | L elim r68 | Queen L6 with an enemy L2 at distance 2 for 6 rounds (r26-31), rammed r32. Then 2 units left at r50. | **r32: she picks W t=(15,9) with threat=1 (score -10) over S options at depth 3 (score -492).** The depth penalty (~480) dwarfs the threat penalty (~20). The L2 walking S down x=15 steps into (15,9). |
| 1333032 | kf1 | AUNSW | L r500 | Our queen died r56 (HitSelf L2) while theirs lived to r500 (L24). | r51 area 3536; r52 all candidates area 0-1. Ally heads 47 and 97 and bodies of 64, 13 and 95 wall her in at (47-51,6-12). Ally seal (the known QALLY_KEEP saturation), not a single bad move. |
| 1410020, 1333035 | b4, kf1 | weakhold | W ×2 | Their queen died r101-103 (NoValidAction / head-on); ours lived at L4-5. | |
| 1410023 | b4 | Trauma | W | Both queens alive; ours L56 vs 27. | |
| 1333033 | kf1 | Schooltime | W | Both queens L3 in the box; our total 386. | |
| 1333034 | kf1 | Trophy | W elim | Their queen killed r44; we swept. | |

- **When our queen lives to r500 we are 4/4 against them; when she dies, 1/6.**
- We out-massed them in these games (median total r100 69 vs 44, r200 102 vs 55).
- 4 of 5 losses are our queen dying, 3 of them before r100. The other is Portals at r485.

## 4. Top cause: our queen dies to small heads before r100 (worker phase), all maps
**The size of it:**
- In a 151-game b4 panel (local replays, every opponent, no QoS), 26 of the 70 losses have our queen killed by an enemy before r100. That is the largest bucket.
- Against Cutlery: Trophy and Devil (above).

**Why:**
- Before `queenSafe()` (QS_FROM=100) the queen is scored like a worker.
- `threat>0` costs her about 20 points. The depth term is worth about 500, so she takes threat=1 tiles over depth-3 alternatives (Devil r32).
- Paid lunges by L3s are not modelled (Trophy r46). Cutlery's 20 paid kills per game make this worse against them.

**Prototype:** `QSTALK=4` with `QSE_THREAT_PEN=1000`, in scratch `top4/cutlery/bot/` (b4 code plus one block in evalDir, queen only, `!queenSafe()`, `!RP.qPark`).
- `threat>0` costs 1000.
- A tile within an enemy head's kamikaze reach K(L) = ceil(L/4) + (L-2), capped at 3 (wrapDist), costs `QSE_PAID_PEN` = 120.

Harness, queen turns only (counterfactual on a fixed history; flags off = 100% MATCH everywhere):

| set | losses: decision changed | changed at the fatal move, avoiding the collision tile | wins changed |
|---|---|---|---|
| vs Cutlery (9 games) | 2 of 2 small-head deaths (Trophy r46 NN → N; Devil r32 W → S). Portals and AUNSW unchanged | 2 | 0 of 5 |
| b4 panel, pre-r100 enemy-killed queen (26 losses / 40 wins) | 11 of 26 | 6 (PD 1261398 r9, Islands 1378740 r91, Default 1379202 r82, Australia 1383113 r70, Autarky 1383471 r82, Trophy 1410021 r46). Another 2 change at the fatal move but the new path still crosses the collision tile (1260766, 1261401). 3 change earlier (1383488, 1383474, 1378741) | 5 of 40. 2 of them change only at the move on which the queen died anyway (1257439, 1257443); 1257441 Islands changes 16 turns; 1378747 and 1383114 change 1 turn |
| VIB 5 Oct, b3-equivalent (29 losses / 22 wins) | same as the 300-penalty run in VIB_OCT5 (1106626 r19, 1129479 r74, 1164512 r23/26, plus Autarky and Slithery ×2) | 3 of 8 checkable | 3 of 22, 1 turn each |

**Totals:**
- At least 7 of 28 small-head queen deaths with checkable decisions (2 vs Cutlery + 26 panel; 1410021 is in both) now step off the collision tile at the fatal move. 13 of 28 change some decision.
- 59 of 67 wins keep identical queen moves.

Read this as "the fatal move changes", not "she survives".

- **Scope:** all maps, queen only, before r100. It plays identically to b4 in about 88% of wins.
- **Risk:** same family as v69 QEARLY_PEN and QKREACH, which lost or never shipped. This version is narrower (enemy ram reach only, no portal or blind penalties) and is the first with a large decision-level count.
- **Recommendation if there is server time:** one unranked block on all maps. Judge it on "queen alive at r100" and on pre-r100 enemy-killed queen deaths per game; move it to the ladder only if those improve and wins don't drop. With about 25 h to the freeze, an unseen-only gate (`!RP.known`-style) is the safer form for the Qualifier. Known-map seeding then stays byte-identical to b4.

**Not cheap, evidence only:**
- Portals crowned coil (1410024): a lost game we had won.
- AUNSW ally seal (1333032).
- QoS economy stall (1410022): can't be harness-checked until the QoS 2nd layout is fitted (`tools/pearl_infer.py --auto --base maps/server_live/queen_of_spades.map`).

## 5. What generalises to unseen maps (the Qualifier)
1. **Their queen is not a plan; ours must be.** Cutlery's queen dies in 70% of games and they win 0/6 r500 games where theirs is dead and the opponent's alive. On any map, a living queen of ours at r500 beats them unless they eliminate us. Every r500 game vs us where our queen lived was a win (4/4). Early queen survival (section 4) is the lever that carries to unseen maps.
2. **They win by elimination** (20 of 31 elimination games), above all on small and lane maps. Our elimination losses to them (Devil, QoS, Trophy) all followed an early queen death plus a unit deficit by r100. Not losing the queen before r100 also protects against elimination.
3. **Paid lunges for food and kills** (41 per game vs our 11.5) and **portal-heavy foraging** (about 2x our crossings) are map-independent strengths. Copying lunges already lost on the server (v64 LUNGE34). Defending against them (the K-reach in QSTALK bit 4) is the transferable part.
4. **Their late game is weak.** Longest is only 15-23 at r400, and late feeding is by NoValidAction. On unseen maps where both queens die, our longest-dragon economy wins. In the 10 head-to-head games our median total was 1.6-1.9x theirs at r100-200.

## 6. Files
- Listing, sample and replays: `replays/top4_cutlery/`.
- Scratch `top4/cutlery/`:
  - `fetch.py`, `dl.py`, `an_cut.py`, `agg_cut.py`, `vp.py`, `rows.pkl`, `b4panel.json`;
  - list files `all.txt`, `vib5_all.txt`, `panel_L.txt`, `panel_W.txt`;
  - harness JSON `v/{offq,qs4,qs4t1000,v5off,v5t1000,poff,pt1000}/`;
  - prototype `bot/` (QSTALK bit 4 only; flags off = b4).
