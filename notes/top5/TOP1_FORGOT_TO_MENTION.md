# #1 "forgot to mention" (FTM, id 264) vs us (v44/v49) and the top 5, 2026-10-03
Read-only study. Games from 2026-10-02 14:42 to 2026-10-03 07:15 UTC. Builds on notes/top5/NEW_RULES_TOP5.md, which holds the 2 Oct top-5 numbers reused below.

## Data
- Game list: replays/top1/games_264.json, 1162 FTM games against {SSS, Sponge, Cutlery, horse, tungtung67, 𓎼𓃭𓅱𓂋𓇌 (glyph), us}, crawled back to 08:42 UTC 2 Oct. Our battles are in our_battles.json and us_vs_264.json.
- Replays: 98 in replays/top1/.
  - All 62 of our games vs FTM since 14:42: v43 5, v44 15 (16:36-20:11), v49 42 (20:12-07:13).
  - Up to 6 recent games (one per map) for each of the 6 other top teams.
- Scripts, all in notes/top5/new_rules_tools/: an_top1.py (an.py plus pearl eats per half and corpse eats), agg_top1.py, qhunt_top1.py, qkill_top1.py (how our queen dies), early_top1.py (small-map fights, invasion, corpses), pearl_top1.py.
  Outputs go to the scratchpad t5n/ (rows_top1.pkl, agg_top1.out).
- Versions are inferred from upload times; v44 was re-uploaded at 07:13 on 3 Oct.
- "Small maps" = Autarky, Devil, Queen Of Spades, Tower Defense, Dilemma, weakhold, Default, Trophy, Trauma, Schooltime. "Half" = the side nearer to that team's queen spawn.

## Identity and how they got +150
- **Not a new or renamed team.** id 264 has 13.1k lifetime wins. Before the reset it was #11 at 1952 (notes/16). Members: gecko, horiseun, speedyninja5967, niftyfour (UNSW).
  Its rating stayed at 1500 until about 01:00 UTC 2 Oct (no active bot after the reset), then jumped to 2010 by 02:54. It reached about 2050 by 09:00, dipped to 1904 at 14:50, then climbed overnight (2075 at 20:48 → 2201 at 23:47 → 2327 at 07:14). By 07:20 it had fallen back to 2280.
  The overnight climb suggests a new upload around 20:00-21:00 UTC 2 Oct.
- **Much of the overnight lead comes from ranked games against us.**
  - SSS, Cutlery and tungtung67 have ranked turned off (SSS since 08:14 2 Oct, Cutlery since 01:34 3 Oct), so FTM can't gain rating from them.
  - FTM's ranked games since 20:48 2 Oct: us 29-11, Sponge 12-8, tung 12-3, glyph 3-2.
  - Unranked, FTM is only about even with the elite: SSS 83/167 (50%), Cutlery 70/156 (45%), Sponge 90/153 (59%), horse 40/68 (59%).
- So the +150 is not dominance over SSS/Cutlery. FTM is a bad matchup for us, and we feed it rating. In our sample FTM beat v49 30/42 and v44 9/15.

## What FTM does (vs us = 62 games, vs top = 36 games; top-5 numbers are from 2 Oct)
| metric | FTM v us | FTM v top | v49 | v44 | SSS | Cutlery |
|---|---|---|---|---|---|---|
| win | 69% | 47% | 29% | 40% | 64% | 57% |
| elimination wins / elim games | **81%** of 26 | 1 game | **16%** of 19 | 40% of 5 | 72% | 27% |
| queen split by r1 / median length r100 | 50% / 2 | 75% / 3 | 31% / 5 | 33% / 4 | 55% / 3 | 24% / 4 |
| queen alive at end | 32% | 22% | **10%** | 27% | 40% | 32% |
| enemy queen killed | **68%** | 47% | 36% | 40% | 62% | 53% |
| units / total at r100 | 26.5 / 64.5 | 42.5 / 107.5 | 25 / 61 | 30.5 / 74 | 22 / 53 | 18 / 46 |
| longest at r500 | 47 | 51 | 52 | 27 | 47 | 54.5 |
| multi-step L5-8 / L9-16 / queen L5+ | 58 / 58 / 0% | 64 / 68 / 8% | 49 / 60 / 33% | 43 / 57 / 27% | 72 / 75 / 65% | 38 / 53 / 30% |
| paid steps per game (share that kill) | 30 (53%) | 53 (50%) | 13.6 (99%) | 15 (100%) | 71 | 43 |
| kills with 3+ steps | 9% | 11% | 0% | 0% | 10% | 18% |
| portal crossings per game | 154 | 141 | 178 | 182 | 115 | 137 |
| head-on kills per game | 62 | **120** | 62 | 64 | 62 | 56 |
| feeding deaths per game | NoValidAction 252 | NoValidAction 387 | HitSelf 223 | HitSelf 280 | HitSelf 80 | NoValidAction 211 |
| splits per game (by r50) | 339 (31) | 525 (39) | 362 (30) | 450 (39) | 243 (20) | 284 (19) |
- **Queen.** FTM's queen is an expendable L2-3 unit. It splits on round 0 or 1 in 50-75% of games, never uses multi-steps at L5+ (it is almost never L5), and dies at a median of r104 against us.
  Its queen survives only 32% of games. But FTM kills ours 68% of the time, and only 11% of their r500 games against us ended with our queen alive.
- **r500 results vs us:** 12 W / 11 L on longest dragon, 10 W / 3 L on the queen tiebreak.
- **Late game.** Like Cutlery, FTM feeds its own units by suicide (NoValidAction) rather than by self-collision. It does this 6.9 times per game for L>=5 units after r300. Its king grows late (median longest 5 at r300, 23 at r400, 47 at r500).
- **Against the top teams FTM is the most violent bot measured:** 120 head-on kills per game, 3.4 kills of L>=10 dragons per game, 525 splits per game. It loses about as much as it kills (it lost 3.3 L>=10 dragons head-on per game).

## Why we lose to FTM
v49's 30 losses: 16 elimination, 8 queen tiebreak, 6 longest dragon. v44's 9: 4 longest, 3 elimination, 2 queen.

1. **Small-map elimination.** We won 7/33 small-map games vs FTM and 12/29 on big maps.
   - In elimination losses, units at r25/r50/r100 were 5/5/7 for us vs 8/11/23 for FTM. Total length was 13 vs 26 at r50 and 17 vs 55 at r100.
   - Head-on trades are even (r<=150: FTM 299 kills, us 289; the same pattern of L2-3 killers, 1-2 steps).
   - **The gap is food.** In r<=150 on small maps FTM ate 2432 fresh pearls vs our 1601 (+52%), 1203 own corpses vs 697, and 464 enemy corpses vs 301.
   - FTM gets there by **covering more ground, not by picking pearls up faster.** Time from a pearl spawning to being eaten is the same for both bots (median 2 rounds, 46-49% eaten within 1 round). FTM simply reaches more tiles, including ours.
   - FTM heads in our half: 2.7 / 4.7 / 5.4 at r50 / r75 / r100. Ours in theirs: 1.5 / 2.0 / 3.0. By r100 FTM has eaten 25.7 pearls in our half; we have eaten 13.3 in theirs.
   - Example, Autarky: FTM ate 43 pearls in our half by r100; we ate 1 in theirs.
2. **Our queen is killed by short lunges.** v44+v49 queen deaths vs FTM: 41, of which 34 were enemy head-ons. The queen was L5-6 in 25 of those because QG_MIN keeps her at 5.
   - **Killer moves** (length, steps, start distance): L3 2-step paid ram from distance 2 in 17 cases; L2 1-step in 8.
   - **Longer lunges:** 3-5 step lunges from distance 3-5 in 13 cases. L2-3 killers can only take that many steps by eating pearls on the path (each pearl refunds a step).
   - At the start of her last turn the nearest enemy head was 2 tiles away in 18 cases and 3 tiles away in 11. She then moved 1 step (29) or 2 steps (12) and stayed in reach.
   - KREACH is 0 in v43/v44/v49. QUEEN_SAFE's F(L)+1 reach does not cover pearl-refunded lunges or heads whose length is under-read because the tail is out of view.
3. **We rarely threaten their queen.** One of our heads is within striking reach of FTM's queen 3.5 times per game (v49), vs 5.4 for FTM against ours. FTM's queen is an L2-3 unit that is easy to kill; we killed it 36% of the time.

## Per map, us (v43/v44/v49) vs FTM
- **We lose:** Autarky 0/5 (4 elim), Devil 0/3 (elim), Queen Of Spades 0/3 (elim), Tower Defense 0/2 (elim), Australia 0/4 (FTM queen alive 4/4), Maze 0/4, Dilemma 1/7 (5 elim), weakhold 1/3.
- **We win or split:** Portals 5/8, Islands 3/4, Slithery 4/8, Default 3/6, Trophy 1/2, Trauma 1/1.
- On big maps we are ahead by r100 (total 119 vs 74 on Islands, 154 vs 93 on Around UNSW). On small maps FTM is ahead: 59 vs 29 on Autarky, 59 vs 20 on Devil, 54 vs 17 on TD.

## Ranked ideas (G = generalises to unseen maps, M = map-specific)
1. **Queen threat model with pearl-refunded reach (G, HIGH, low-medium effort).**
   - Change: for the queen only, an enemy head threatens a tile if it can reach it within K(L)=ceil(L/4)+(L-2) steps, plus 1 per visible pearl on the path. When the tail is unseen, count the head as L3 or more.
   - Evidence: 34 of 41 queen deaths vs FTM were head-ons, and the killers came from 2-5 tiles with 2-5 steps.
   - Implementation: reuse KREACH (exists, off) with KR_CAP 4-5, applied to the queen only (KREACH parts gated to amQueen()). Add the pearl term to the BFS.
   - Expected: the queen survives r100-250 more often. That flips some "theirs only" tiebreaks, which were 8 of v49's 30 losses.
   - Test: queen death cause histogram on dilemma/devil/trophy/stripes and unseen sets.
2. **Push small units forward early on small maps (G, HIGH, medium effort).** FTM wins elimination games by r50-r100 through territory: about 2x the heads in our half and +52% fresh pearls.
   - Change: from r20-r100, send part of the L2-3 foragers to forage in the enemy half and on contested ground, for example any pearl or countdown tile closer to their spawn within N steps.
   - Change: count enemy heads in our half as targets for the home units.
   - Partial precedent: HOME_DEFEND/EARLY_PUSH were built in v48 and showed no gain there. Re-test them with the FTM matchup in the pool (scrims vs FTM-like bots) rather than vs v35/v38m.
   - Measure with an_top1's eat_en_r100 and the per-half head counts.
3. **More fresh-pearl coverage from more early units (G, MED).** FTM had 7 units at r25 on small maps vs our 5, with 14 splits by r50 vs our 12. Its units cover more ground (fresh eats +52%), not faster. Try a looser early split floor on small maps (unit-count target 8-10 by r25 when the area per unit > X). V50's EARLY_QSPLIT targets the same gap through the queen, but it kept the queen at L3; it had a +.04 screen result.
4. **Recycle more by explicit suicide next to allies (G, MED).** FTM ate 1203 own corpses by r150 on small maps vs our 697. It uses NoValidAction suicides (603 vs our 229 HitSelf deaths). Cutlery and Sponge do the same.
   Explicit suicide does not need a reachable self-collision, so it can drop pearls right next to the king or a feeder. Try a SUICIDE_FEED flag: replace the HitSelf feed with an explicit suicide when an ally head is within 1-2 tiles.
5. **Hunt their queen; it is a cheap L2-3 unit (G, MED).** We get within reach of FTM's queen 3.5 times per game and kill it 36% of the time; FTM kills ours 68%. This is the same as idea 1 in NEW_RULES_TOP5.md: an always-on pull toward the last sighting (QSTATE tracker) for L2-4 units. It matters most on big maps, where we already lead on mass and the queen tiebreak decides games.
6. **Port LUNGE34 (3-4 step rams and paid eat-lunges; G, MED).**
   - Gap: we make 0% of kills with 3+ steps (FTM 9-11%, Cutlery 18%), and our paid steps are only 13.6 per game, almost all kills (FTM 30 per game, 23% of them eats).
   - Status: already in v42, not in v43/v44/v49.
7. **Map-specific (M).**
   - Autarky, Devil, QoS, TD, Dilemma: an opening for elimination maps (ideas 2-3) is worth more there than anything queen-related. They account for 18/62 games and 1 win.
   - Australia 0/4: FTM's queen survived 4/4. Big-map hunting (idea 5).
- **Do not copy:** FTM's expendable queen policy (our tiebreak wins depend on our queen living); its 120 trades per game vs elite bots (it breaks even at best).
- **Matchup note:** FTM's #1 rating rests partly on ranked games against us. Each fix that turns small-map elimination losses into wins also stops feeding it rating.
