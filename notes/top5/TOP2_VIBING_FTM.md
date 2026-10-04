# Top 3 refresh: Vibing++ (#2), forgot to mention (#1), SSS (#3) vs our v55/v60 — 2026-10-03 ~18:30 UTC
Read-only study. Extends notes/top5/TOP1_FORGOT_TO_MENTION.md and NEW_RULES_TOP5.md (2 Oct numbers reused as baselines). Nothing submitted, no challenges.

## Data
- Listings: replays/top2/games_306,264,91.json — every game among {VIB, FTM, SSS, Sponge, horse, tung, glyph, Settlers, Computers, us} played by 306/264/91 from 05:00 to 17:10 UTC 3 Oct (VIB 629, FTM 1418, SSS 1663 kept rows). Team histories: replays/top2/team_{306,264,91}.json.
- Replays: 389 in replays/top2/ (sample.json). VIB 162 (all 40 vs us + up to 17 per opponent), FTM 171 (all 68 vs us + 14 per opp), SSS 86 (all 25 vs us + 8 per opp). VIB games after 17:08:30 excluded (they switched submission, see below).
- Our version by time: v44b 07:13, v55 11:42, v60 15:27 UTC. In replay sample: v55 72 games vs top-3, v60 25, v44b 31.
- Scripts (notes/top5/new_rules_tools/): fetch_top2.py, sample_top2.py, an_top2.py (= an_top1 on top2), agg_top2.py (team tables incl. 2 Oct baselines), permap_top2.py, mid_top2.py (per-100-round eats/mass-loss by cause/half; `mid_top2.py VIB v55,v60 big`), selfdeath_top2.py, lens_top2.py (length mix of units), eatlen_top2.py, kills_top2.py (kill move types), fp_top2.py (opening fingerprint; too noisy, opponent-dependent, not used). Outputs: scratchpad t5n/rows_top2.pkl, agg_top2.out, mid_*.out.
- "Big maps" = Islands, Maze, Around UNSW, Australia, Portals, Slithery, Stripes; the rest "small" (same split as TOP1 notes).

## 1. Who is Vibing++
- **Vibing++ = team 306 = Cutlery renamed** (Sprint champion, members spoon / fork / ldauth). Lifetime 15545-4-8157. Not a new team.
- Rating (team history): 1500 reset → 1865 by 12:37 1 Oct → several drops to ~1373-1396 (1 Oct 16:10, 2 Oct 00:00-01:36: they flip to a second, low-rated submission and back) → 2289 at 18:08 2 Oct → ranked OFF 01:34 3 Oct (sat ~2140-2150) → ranked ON 09:36 3 Oct → 2331 at 17:07 (+185 in 7.5 h) → **17:08:33 switched active submission to one rated 1388** (same pattern as their earlier test flips; expect a new/test build now, watch for it).
- New-version evidence: vs SSS now 43/61 (70%) unranked+ranked, vs Cutlery-2Oct 7/14; elimination win share 27% (2 Oct) → 62-73% now; total length r300 99 → 152-180. Upload time unknown (cannot see other teams' submissions; it was already this strong by 05:00-09:36, e.g. 22/27 vs SSS unranked).
- Its +185 came from ranked games: vs us 25/35 (71%), FTM 78/155 (50%), horse 15/25, Sponge 13/20, Settlers 5/5, Computers 3/5, SSS 4/5, glyph 4/5. It plays ~140 games/hour (mostly challenges vs FTM).
- Record vs us (listing): v49 0/5, v44b 3/10, **v55 6/20**, v60 1/5 (our wins). Per map vs us (all versions): Islands 0/4, Maze 0/5, Around UNSW 0/2, Portals 1/5, QoS 0/2, Stripes 0/1, TD 0/1, Default 0/1, Australia 2/3, Autarky 1/3, Devil 1/3, Slithery 1/3, Schooltime 1/2, Trophy 1/2, weakhold 1/2, Dilemma 1/1. **Big maps 4/23, small 6/17.**

## 2. FTM: no new version detected
- No rating discontinuity since the 20:00-21:00 2 Oct upload. Behaviour vs us old (v44/v49) vs now (v55/v60) is the same within noise: queen split r0-1 50%/49%, queen L2 at r100, multi-step L5-8 58%/64%, paid steps 30/28.5 per game, kill steps 1/2/3+ = 54/37/9% vs 53/37/10%, NoValidAction feeding. Differences in units/kills track OUR version change.
- 2280 → 2348 came from ranked wins: **vs us 26/30 before 12:00 (v44b) and 17/30 after (v55/v60)**, Settlers 13/15, Computers 5/5, Sponge 12/20, SSS 11/20; vs VIB 77/155 (even).
- **v55 fixed most of the FTM matchup:** our wins vs FTM v44b 4/21 → v55 20/37 (54%) → v60 2/10 (small n). v55 vs FTM per map: Portals 3/3, Default 3/4, QoS 2/2, Dilemma 2/4, Stripes 2/4, AUNSW 2/4; still Autarky 0/1+0/2 (v60), Maze 0/2, Trophy 0/1, Schooltime 0/2 (v60).

## 3. SSS: same bot, quick refresh
- Same profile as 2 Oct: L2-3 escorted queen all game (median 3 at r400), multi-step 66-76% incl. queen 65%, 75-80 paid steps/game, HitSelf+HitOtherBody feeding. Rating 2183 → 2304 from ranked vs Sponge (15/20) etc. vs us 14/25 (v55 7/15 ours, v60 4/10). It loses to VIB (12/56 unranked).

## 4. Metric table (medians; n games; "us" rows are v55/v60 vs that team)
| metric | VIB v us (40) | VIB v top (68) | Cutlery 2 Oct (99) | FTM v us (68) | SSS v top (47) | v55 v VIB (20) | v55 v FTM (37) |
|---|---|---|---|---|---|---|---|
| win | 75% | 68% | 57% | 62% | 47% | 30% | 54% |
| elim win / elim games | 73% of 11 | 62% of 26 | 27% | 63% of 30 | 64% | 25% of 4 | 56% of 16 |
| queen never split / first split | 38% / r18 | 37% / r18 | 36% / r27 | 4% / r0 | 6% / r0 | 25% / r12 | 16% / r27 |
| queen len alive r100/200/300/500 | 5/10/13/27 | 5/8/8/38 | 4/7/11/25 | 2/2/7/27 | 3/3/3/15 | 4/4/4/4 | 5.5/5/4.5/14 |
| queen alive at end / death median | 38% / r230 | 43% / r105 | 32% / r168 | 38% / r138 | 30% / r173 | **20% / r59** | **16% / r60** |
| queen self deaths | 1/25 | 1/39 | 2/67 | 4/42 | 4/33 | **9/16** | **17/31** |
| queen is king at end | 28% | 26% | 19% | 12% | 11% | 5% | 8% |
| queen kelp sides / allies within 4 | 0.66 / 0.82 | 0.69 / 0.78 | 0.66 / 0.70 | 0.53 / 0.91 | 0.53 / 1.43 | 0.59 / 1.50 | 0.56 / 1.13 |
| units r25/50/100/200/300 | 6/13.5/27/53/58 | 6/12/22/44/53.5 | 6/8/18/35/34 | 6.5/10/21.5/37/48 | 7/12/26/42.5/61 | 9/18.5/31/40/33 | 7/10.5/22.5/39/36 |
| total r25/50/100/200/300 | 18/33.5/68/**140/180** | 17/28/54.5/108/152 | 15/22/46/87/99 | 16/26/50/95/129 | 17/29/59.5/100/163 | 29.5/49/71/**97/89** | 19/29/56/93/98 |
| longest r100/200/300/400/500 | 6/13/16/34.5/54 | 5/8.5/13/35/63 | 5/8/12/29/54.5 | 4/4/10/31.5/50 | 3/5/10/31/41 | 4/4/6.5/30.5/46.5 | 4/5/7/32/47 |
| multi-step L5-8 / L9-16 / queen L5+ | 46/60/33% | 46/61/32% | 38/53/30% | 64/65/1% | 71/76/66% | 49/57/41% | 46/57/33% |
| paid steps/game (eat share) | 54.5 (37%) | 49.5 (39%) | 43 (38%) | 28.5 (18%) | 80 (27%) | 12.8 (7%) | 14.2 (10%) |
| kills with 3+ steps | **19%** | 17% | 18% | 9% | 10% | **0%** | **0%** |
| portal crossings/game | 193 | 148 | 137 | 112 | 100 | 204 | 160 |
| h2h kills/game, lost L>=10 h2h | 74, 1.95 | 73, 1.88 | 56, 1.57 | 64, 1.24 | 78, 2.68 | 72, 1.15 | 57, 0.95 |
| feeding deaths/game | NoValid 255 | NoValid 230 | NoValid 211 | NoValid 143 | HitSelf 82 | HitSelf 271 | HitSelf 214 |
| r500: queen W/L, longest W/L | 9/2, 13/5 | 14/6, 16/6 | 18/5, 28/11 | 9/6, 14/9 | 5/7, 8/13 | 1/6, 4/5 | 4/5, 7/5 |

## 5. What VIB does that we don't
1. **Big-map mid-game growth (the main gap).** On big maps vs VIB (14 v55/v60 games, we won 3):
   - Total length us/VIB: r50 55/39, r100 73/80, **r200 98/197, r300 91/207**. Units r200 40/61. Longest r200 5/16, r300 6/20. vs FTM on the same maps we are even (r200 151/159, units 59/62).
   - Per 100 rounds, r100-300 (mid_top2 big): fresh pearls us 163/158 vs VIB **194/184**; eaten in our half by VIB 106/124 vs FTM's 74/79 in the same games type. Mass destroyed by own suicides+ally-body collisions us 251/285 vs VIB 193/258, recovered as own-corpse eats 155/179 vs 122/165. Head-on mass lost is even (57/61 vs 61/69).
   - So VIB out-eats us by ~+57 fresh pearls over r100-300 (mostly in our half) and wastes ~40 less mass in recycling. That's the whole ~100-length gap at r200-300. (All maps together: fresh share r0-100 ours 55%, r100-300 VIB's 54%.)
   - Unit makeup (lens_top2, means, all maps): we hold almost everything as L2-3 (r200: 33 of 37 units; L8+ 0.4). VIB keeps 6 units at L4-7 and 2-3 at L8+ (r300 top-3 dragons sum 37 vs our 23). VIB's L4-7 dragons ate 64 fresh + 58 corpse pearls in r100-300 vs our L4-7 22 + 27. Growth-split rule is the same for both (82-89% of open splits are L4→k2), so VIB's mid-size dragons are units it does not split, not a different split size.
2. **Lunges using pearls and paid steps.** In mutual games VIB kills 35/game vs our 28.
   - 3+ step kills: VIB 7.3/game (L3 3-step eating a pearl on the way 3.3, L4-6 3-step 2.0, L2 3-step with pearl 1.2); SSS 4.6/game, FTM 3.5/game; us 0.1.
   - Kills where a pearl eaten on the path paid for the extra step: VIB 8.8/game, us 1.2.
   - VIB also makes 24 paid moves/game that don't kill (8.4 to eat a pearl). We make about 0.
3. **The queen stays in the economy, whole, and becomes a king seed.**
   - 38% of VIB queens never split; otherwise the first split is around r18.
   - She sits against kelp (0.66-0.71 kelp sides) with fewer escorts (0.8). She grows when alive: 5 / 10 / 13 at r100 / 200 / 300, then 27-38 at r500. She is the king at the end in 26-33% of games.
   - She almost never kills herself (1/25). Enemy head-ons kill her, 6/25 at L10+.
   - Most VIB r500 wins vs us come from its queen alive at L40-55 while ours is dead (Portals L54/55, Islands L42, Maze L43).
4. **Elimination.** VIB now wins 62-73% of games that end in elimination (Cutlery won 27%). It took 8 of 11 such games vs us, mostly small maps (Autarky, Devil, QoS, Stripes, TD, Trophy).

## 6. Our weak points vs the top 3 (v55/v60)
- **The early queen kills herself.** With QS_FROM=100 the queen plays v35-style before r100. She dove into kelp pockets and pumped split after split (k=2, 0-2 exits), then died boxed (HitSelf/HitOtherBody at L2-3).
  - This happened before r100 in **24/72 v55 games vs top-3**, plus 8 more after r100. Her median death is r59-60, and our queen was alive at r500 in only 16-20% of those games. Examples: 967606 Islands, 964198 Portals, 964201 Australia, 967602 QoS.
  - v60 (QEXIT_LOOK) cut early self deaths to 1/25. But v60 won 7/25 vs the top 3, and server totals are v60 105-83 (56%) vs v55 298-187 (61%). Its 5 VIB games and 10 FTM games show a mid-game stall (units 13.5→13 from r100 to r200 vs FTM). The sample is small, so treat this as a warning, not a verdict.
- Losses vs VIB+FTM (v55/v60, 43 losses): 16 elimination, 14 queen tiebreak (their queen alive, usually L23-55), 13 longest dragon.
  - In the 11 "longest" losses on big maps our king was often fine (AUNSW 50, Maze 90, Islands 38-51). The enemy mass was 2x ours.
- Weakest maps vs the top 3 in the replay sample:
  - Autarky 1/12 (8 elimination losses), Islands 1/9, Maze 1/8, Trophy 1/7, Schooltime 2/8.
  - In all 8 Schooltime games both queens were alive; we lost on longest dragon.
  - Server v55 byMap agrees: Portals 1886, Maze 1916, Devil 1989.

## 7. Ranked changes for our bot (impact = rough guess for overall score vs the top 3; P = can be a param change on v55, C = needs code)
1. **Stop the early queen's pocket deaths, keeping QS_FROM=100 (P first, then C). HIGH.**
   - Evidence: 24/72 v55 games lose the queen to herself before r100. Queen-tiebreak losses are 11 of v55's 21 r500 losses vs VIB and FTM. VIB/SSS/FTM queens die by their own hand in 2-10% of games.
   - P: v55 + `QSPLIT_ROOM=1` (applies to the queen in every phase: she splits only with ≥16 tiles on her side and no ally head within 2). That blocks the k=2 pump splits in pockets. Also try `SPLIT_NEEDS_EXIT`-style gating for the queen only, which needs code.
   - C: in the queenEarly() branch, add a no-pocket rule. Don't enter pockets (PF/tip) or split with ≤1 exits. Keep the eat/forage behaviour that made QS_FROM=100 pay off.
   - Expected +3-5 pp vs the top 3. v60 shows the self-death fix alone is not enough if it also costs economy, so A/B against v55, not v60.
2. **Big-map mid-game "harvester" dragons (C, maybe P). HIGH on big maps, MED overall.**
   - Evidence: vs VIB on big maps we lead at r50, then fall to half their mass by r200 (98 vs 197). Their edge is fresh pearls in our half plus less recycling waste, carried by 6 L4-7 and 2-3 L8+ non-splitting dragons. We have 3.6 and 0.4-1.
   - P tests (big maps only, via per-map params):
     - Earlier king seed (`KING_SEED_ROUND`/v2 seed 250 → ~150) so 1-2 dragons start growing at r150.
     - Or `SPLIT_STOP_ROUND` ~200 with `LATE_SPLIT_MAXLEN` 3, which stops growth splits after r200 so mass collects in L4-8 units.
     - Both are blunt. Watch units and fresh eats r100-300 with mid_top2.py.
   - C (better): from ~r100, let N=4-6 units with id hash, room ≥ X and no threat skip growth splits up to L8-12. They forage the contested/enemy half using their 2-3 free steps. Small-map behaviour stays unchanged.
   - Expected: big maps are 7/17 of the pool. We are 4/23 there vs VIB (listing), but even with FTM. +10-20 pp vs VIB on big maps, about +2-4 pp overall.
3. **Port LUNGE34 / pearl-refunded lunges (C, code exists in v42). MED.**
   - Evidence: VIB 7.3, SSS 4.6, FTM 3.5 three-plus-step kills per game vs our 0.1. VIB gets 8.8 kills/game from lunges a pearl paid for (ours 1.2) and leads us 35 vs 28 kills per game.
   - v42 failed in self-play (.476 unseen), but every top team does this. Test it on the server (A/B vs v55), not in self-play.
   - Expected +2-4 pp vs the top 3; it also makes their L3 lungers trade into us less cheaply.
4. **Queen as king seed when she survives r200 (P: QUEEN_KING=1 on big maps; C: gate on her alive + enemy queen dead/unseen). MED-LOW.**
   - VIB's queen is the king at the end in 26-33% of games, and VIB wins 9/11 queen tiebreaks vs us. Ours is the king 5-8% of the time. QCROWN was parked before (fed queens die to small rammers), and VIB's L10+ queen also dies 6/25.
   - Only worth trying after idea 1 keeps her alive.
5. **Small-map elimination.** Autarky 1/12, Trophy 1/7. Same diagnosis as TOP1 notes ideas 2-3 (coverage/home defence). Nothing new from VIB beyond its elimination rate jump.
   - Its small-map unit counts are lower than ours (r100 8.5 vs 13). It wins those fights with lunges (idea 3), not with numbers.
- **Not worth copying:**
  - FTM's r0 queen split (its queen dies median r105-138).
  - SSS's 80 paid steps/game (SSS 47% vs the top 3 now).
  - VIB's bigger NoValidAction-vs-HitSelf feeding style: recycling recovery is the same, about 62-64% of the mass.

## 8. Watch list
- VIB switched to a 1388-rated submission at 17:08:33 UTC (13:08 EDT) 3 Oct. Re-check its rating and behaviour in a few hours: games after that time are a different build.
- FTM: no new build since 2 Oct ~20:00 UTC. Its rating gains now come mostly from lower teams and even games vs VIB.
- v60 vs v55 needs the A/B result. The replay sample hints v60 is worse vs the top 3 (7/25).
