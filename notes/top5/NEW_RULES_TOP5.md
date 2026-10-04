# Current top 5 under the queen rules vs our v41/v43 (games 2026-10-02 06:20-15:24 UTC)
Ladder at 14:44 UTC: 1 Cutlery 2187 · 2 horse 2175 · 3 Sponge 2140 · 4 SSS 2117 · 5 bread first search (BFS, id 507, new) 2071 · 6 us 2029.
Builds on notes/top5/SPONGE_HORSE.md, notes/top5/CUTLERY_SSS_WHQ.md and notes/newrules/OPPONENTS.md (morning studies). Read-only research; nothing was run, submitted or challenged.

## Data and method
- 312 replays (624 team-games) in replays/top5_new/. For each top-5 pair: the 14 most recent games, covering every map seen. Our games vs top 5: v41 128 (08:09-14:42), v43 44 (14:42-15:24, ranked and unranked battles). Draws (3) are skipped.
  Team-games: Cutlery 99, horse 92, Sponge 89, SSS 89, BFS 83, v41 128, v43 44. Game list: games_pairs.json (1296 top-5/us games crawled from /games/__data.json); sample.json is the analysed subset.
- Scripts in notes/top5/new_rules_tools/: fetchlist.py/fetch1.py (crawl), sample.py (pick + download), an.py (per-game metrics via notes/tools/midgame/sim2), agg.py (team table), agg2.py (r500 classes, queen deaths, per-map), qhunt.py (enemy-queen approach counts).
  Raw outputs: scratchpad t5n/agg.out and the agg2/qhunt printouts. Re-run with `python3 notes/top5/new_rules_tools/agg.py` after an.py.
- Our version is inferred from upload time (replays carry no bot name). The listing ignores kind/perPage filters, so crawling is about 9 s per 10 games.
- Definitions:
  - "Multi-step" = turns with 2+ steps. "Paid" = steps > ceil(L/4).
  - "Self" queen death = HitSelf, or HitOtherBody/HitHeadToHead with an ally.
  - "In reach" = one of our heads within K(L)=ceil(L/4)+L-2 (Manhattan) of the enemy queen's head at turn start.

## Headline: r500 games are now decided by the queen, and that is where we lose
| team | win | r500 W/L decided by queen | only OUR queen alive (W) | only THEIR queen alive (L) | elim win% | queen alive at end | enemy queen killed |
|---|---|---|---|---|---|---|---|
| Cutlery | 57% | 18 / 5 of 62 | 15 | 3 | 27% | 32% | 53% |
| SSS | 64% | 16 / 5 of 57 | 14 | 3 | 72% | 40% | 62% |
| Sponge | 57% | 11 / 8 of 54 | 7 | 5 | 63% | 27% | 60% |
| horse | 48% | 13 / 13 of 56 | 11 | 8 | 53% | 34% | 45% |
| BFS | 34% | 9 / 16 of 60 | 8 | 12 | 48% | 28% | 25% |
| **v41** | 44% | **12 / 23 of 79** | 7 | **21** | 41% | 27% | 44% |
| **v43** | 45% | **3 / 12 of 30** | **0** | **10** | 57% | 34% | 34% |
- v43's losses: 12 queen tiebreak, 6 elimination, 6 longest dragon. v41's: 29 elimination, 23 queen tiebreak, 20 longest.
- **Of v43's 10 "only their queen alive" losses, our longest dragon was longer in 7.** 9 of those 10 enemy queens were L>=10 queen-kings: Cutlery 73/84/39/25, horse 107, BFS 24/26. v41: 10 of 21 had our longest ahead, and 14 of 21 enemy queens were L>=10.
- Our longest dragon is not the problem. Median longest at r500: v43 52, Cutlery 54.5, SSS 47, v41 47, horse 46, Sponge 39.5, BFS 26.
- Head-to-head in the sample (row wins/games):
  - v41: Cutlery 11/28, horse 13/26, Sponge 10/28, SSS 8/28, BFS 14/18.
  - v43: Cutlery 8/15, horse 6/10, Sponge 2/5, SSS 1/5, BFS 3/9.
  - SSS beats everyone except Cutlery (7/14).

## Per-team profiles (medians unless noted; "us" = v41 / v43)
### Cutlery (#1): queen = king seed; best at r500 (74%), worst at elimination (27%)
- **Queen:** unsplit in 36% of games, first split median r27. She stays L4 to r100, then grows when alive: L7 r200, 11 r300, 24 r400, 25 at r500. She is the king at the end in 19%. 63% of her eats are own corpses.
  Dies median r168, almost always to an enemy head-on (50/67). The other 15 are NoValidAction suicides of L2-3 remnants.
  On Portals she is L3, never split, roams about 11 tiles from spawn and survives 5/7. On Slithery she is L12-15 by r100.
- **Growth:** units 6/8/18/35/34 at r25/50/100/200/300, falling to 9 at r500. Total 46 at r100 (the opponent's 52). Longest 12 at r300, 29 r400, 44 r450, 54.5 r500. The king forms late.
- **Moves:** multi-step 38% at L5-8 and 50-53% at L9+, almost never paid; queen 30%. Paid lunges 43/game, 38% eat and 45% kill.
- **Kills:** 3-step kills are 18% of all kills. Portal crossings 137/game.
- **Fighting and endgame:** h2h 56/game. Enemy queen killed 53%.
  Feeding is by NoValidAction (211 deaths/game, 5/game for L>=5 after r300). Splits 284/game.
- **Weakness:** loses elimination games (27/43 of its losses).

### horse (#2): mass army, L2 queen, cascade late
- **Queen:** split r0 in 61% of games; median length 2 to r300. She is escorted (1.27 allies within 4) and lives 34%. When alive she is fed late: 23.5 at r400, 29 at r500 (one reached 107 vs v43).
  Deaths: enemy head-on 49/61; self 12, the late ones being k=L-2 trap splits of a big queen on Maze/Portals.
- **Growth:** biggest mid-game army: units 27 r100, 61 r200/r300; total 154 at r200 and 170 at r300 (opponents 91/111). Collapses to 10 units / 132 total at r500, longest 46.
- **Moves:** multi-step 45-48% (queen 17%). Paid 22/game, 66% of them kills.
- **Kills and portals:** 3+ step kills 12%. Portal crossings 171/game.
- **Feeding:** HitSelf (164 deaths/game). Lost L>=10 dragons head-on 2.7/game, the highest leak (the morning study found the same).

### Sponge (#3): fights hardest, keeps big dragons out of fights, sacrifices the queen when convenient
- **Queen:** churns (first split median r9, 3+ splits). She dies earliest of the top 4 (median r111), alive 27%. When alive she reaches L20 at r300.
  On weakhold the queen suicides into kelp at r65 in 6/7 games, and Sponge still wins 7/7 there (elimination/longest). Sponge does not rely on the queen tiebreak.
- **Growth and fighting:** h2h 64.5/game, but lost L>=10 dragons head-on only 0.53/game (lowest). Kills include 3-4+ step lunges (17%).
- **Moves:** multi-step only 21% (16% at L17+, queen 2%). It is the least mobile of the top 4.
- **Portals and endgame:** crossings 176/game. Endgame merge by NoValidAction (6.1 L>=5 deaths/game after r300, 29% within 3 of the king).
- **Opponents:** best record vs v41 (18/28).

### SSS (#4): best overall (64%); tiny escorted queen, the most free steps, the most queen kills
- **Queen:** split r0 in 55% of games and kept at **L2-3 all game** (median 3 even at r500). She has the most escorts (1.5 allies within 4), the fewest enemies near her (0.19 within 4) and survives 40%. Self deaths 11/89.
  weakhold: L2 queen hugging kelp (0.91 kelp sides per tile), alive 6/7, 7/7 wins.
- **Moves:** multi-step 72-75% of L5+ turns, queen 65% (us 26%).
- **Enemy queen:** in reach 12.9 times/game (us 4.1/5.5). Enemy queen killed 62% (the highest).
- **Growth:** units 57 at r300 (stays wide), longest 47 at r500. Elimination wins 72%.
- **Weakness:** few big lunges (3+ step kills 10%). Portal crossings lowest of the top 4 (115).

### bread first search (#5, new): weakest in this sample (34%)
- **Queen:** L2-3, dies earliest (median r88); 21/57 deaths are HitWall at L2-3. On weakhold she suicides into kelp at r26/r56 in 9/12 games.
- **Moves:** almost no multi-step (1-2%). No 3+ step kills.
- **Growth:** low: total 37 at r100, 71 at r200; longest 4 until r300, 21 at the end.
- **Results:** loses 27 r500 games on longest and 16 on queen. Its #5 rating probably comes from beating weaker teams; v41 beat it 14/18. v43 went 3/9 in unranked games: small sample, mostly queen tiebreaks.

### Us: v41 / v43
- **Queen:**
  - Alive 27% / 34%. Dies median r143 / r198.
  - Self deaths 35/128 and 11/44 (27% / 25% of games) vs SSS 12%, horse 13%, Cutlery 2%.
  - **Nearly every self death is a 0-exit trap split** (L4-6 queen splits k=L-2 or k=2, then dies HitSelf/HitOtherBody next turn) (qdeath list in agg2 output). Typical maps: Portals, Slithery, Maze, Tower Defense.
  - Enemy kills hit her at L4-6 (37/59 for v41), a size the others rarely carry.
  - Kelp sides at her tile 0.33/0.39 vs 0.52-0.76 for every top team.
  - Portals: our queen alive **0/13** (all self deaths, 2 allies within 4, stays about 6.5 tiles from spawn). Cutlery 5/7, Sponge 5/6.
- **Growth:** the best early economy: total 64.5 at r100 (v43) vs 46-63. 395-428 splits/game vs 243-284. Feeding is HitSelf (240-266 deaths/game). Longest at r500 52 (v43).
- **Moves:** multi-step 43-54% (fixed by v41), queen 26%. Portal crossings 162-194/game, the highest (fixed since the morning).
- **Kills:** **3+ step kills 0%** (top 4: 10-18%). Paid lunges 12-13/game, almost all for kills; paid eats 11-14% of them vs 26-42%.
- **Enemy queen:** killed 44% / 34%, in reach 4.1 / 5.5 times per game (SSS 12.9, Sponge 9.1, Cutlery 7.4). Our heads sit near the enemy queen less often than near other enemy heads: 0.20-0.23 vs 0.35 per 4-tile radius. Every top team is about 1:1.
- **Per map (v41+v43 vs top 5):**
  - Weak: weakhold 3/16, Slithery 5/16, Stripes 2/10, Around UNSW 2/7, Maze 2/8, Portals 5/13, Autarky 2/8.
  - Strong: Trauma 10/11, Islands 8/10, Dilemma 7/9.

## Ranked ideas for our bot (G = generalises to unseen maps, M = map-specific)
1. **Hunt the enemy queen, above all a big queen-king (G, HIGH).**
   - Evidence: 7/10 v43 and 10/21 v41 "only theirs alive" r500 losses had our longest ahead, and 9/10 (14/21) enemy queens were L>=10. A head-on kills both, so one L2-3 trade into her head flips the game. We get in reach of her 4-5.5 times/game vs SSS 12.9 / Sponge 9.1, and our units cluster less around her than around other heads.
   - Build: turn QSTATE's enemy-queen tracker (exists, QSTATE=0) into an always-on attraction. Small units (L2-4, not feeding the king) within R~12 of her last sighting (seen <= 40 rounds ago) score -W*dist. From r300, or once her length is >= ours, widen R and also send L5-8. Keep QKILL as is.
   - Expected: +3-6% overall winrate if half of those losses convert. The tracker and relay are already in v43, so effort is low.
2. **Stop the queen's 0-exit trap deaths (G, HIGH).**
   - Evidence: about 26% of our games lose the queen to herself (v43 11/44), almost all as split-at-0-exits followed by death next turn. Top teams do this 2-13% of the time.
   - Build: a QSPLIT_EXITS-style lookahead on her moves. An L4-6 queen may not step onto a tile whose next-turn exits (after allies' likely moves and her own tail) are <= 1. The QALLY_KEEP radius should also cover her escape tiles on Portals/Slithery (2+ allies within 4 there).
   - Alternative to test: SSS/horse style, keeping her at L2-3 with an escort until r300 (QG_MIN 5 -> 3). L2-3 queens on top teams die mostly to enemies, rarely to themselves.
   - Expected: queen alive about +10 points, which moves r500 classes from "only theirs" to "both dead / longest".
3. **Port LUNGE34 from v42 into the v43 line (G, MED).** Top 4 make 10-18% of their kills with 3-4 steps (we make 0%) and use paid eat-lunges at 7-19/game (ours about 1.5). The code exists (v42 flag LUNGE34=1); it was never merged into v43, which is v41-based.
4. **Queen hugs kelp, roams from the home crowd (G, MED).** Top queens sit on tiles with 0.52-0.76 kelp sides (SSS weakhold 0.91, alive 6/7); ours 0.33-0.39 (weakhold 0.17, alive 3/16). Try a small bonus per kelp side when the tile keeps >= 2 free exits. This is the opposite sign of v43's QOPEN_PEN, which should stay 0. Cutlery's Portals queen also roams 11 tiles from spawn with 0.9 allies near; ours stays 6.5 with 2.
5. **Queen free steps (G, LOW-MED).** SSS queen multi-steps on 65% of L5+ turns, ours 26%. v42 QUEEN_FREESTEP (built, off) raised it to 33%. Mainly useful together with 2.
6. **Late queen growth only if she is alive at r300 (G, LOW).** "Both alive, theirs longer" lost us only 2+2 games. Feeding her to L20+ (Cutlery, Sponge, horse: 24-29 at r400-500) is cheap insurance but also makes her a target (see 1). Gate it on the enemy queen being dead or unseen for 100 rounds.
7. **Not worth copying:**
   - Sponge/BFS's weakhold queen suicide (M). It works for Sponge only because it wins weakhold by elimination.
   - Cutlery's low elimination rate.
   - Our split churn (395-428 splits/game) is not hurting growth (best total at r100) and does not need changing.
- **Map-specific (M):**
  - Portals: queen alive 0/13 → idea 2 plus not parking near home; Cutlery's unsplit L3 roaming queen survives 5/7.
  - weakhold: L2 queen against kelp (SSS).
  - Slithery: our queen pumps 12-15 splits at L5 then traps; Cutlery's is L12-15 by r100.

## Changes since the morning studies
- WeHaveQuizzes dropped to #10; BFS entered at #5.
- Cutlery now keeps the queen alive to r500 more often (it wins 15 r500 games as the only queen alive).
- Everyone now uses free steps except Sponge (21%) and BFS (1-2%).
- We closed the multi-step and portal gaps (v41).
- The queen tiebreak has become our main loss mode (v43: 12/24 losses).
