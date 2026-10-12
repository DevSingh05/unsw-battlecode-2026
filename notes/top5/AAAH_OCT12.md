# aAah (id 454, #3 at 2509) on the 31-map pool: what they do, and what we can take (12 Oct)
Read-only study, written 12 Oct about 5 PM EDT. Nothing in bot/ or variants/ was changed, nothing was uploaded or challenged, no local games were
run. It builds on TOP4_AAAH_OCT8.md and DEEP_AAAH_OCT8.md and does not redo their per-turn rule profile. Scripts, data and replays are in
`work/top3_oct12/aaah/` (rerun commands in section 6). "r500 game" = a game that reached the round limit.

## 0. Short version
- **No queen plan and no king plan: they win on mass.** The queen is an ordinary unit that splits 4 -> 2+2 at round 0 and avoids portals. She is
  alive at r500 in 32 of 64 r500 games, the opponent's in 17. They play the 14 new maps as they did in the Qualifier, when the maps were unseen
  (units at r100: 51 then, 50 now); on 10 of the 14 they hold 52 to 62 units by r100.
- **How they lose** (37 sampled ladder losses): longest dragon with both queens dead 15, elimination on small maps 10, opponent's queen alive and
  longer 7, their queen dead and the opponent's alive 5. With both queens dead at r500 they win only 14 of 32, holding 62 to 64 units in 12 of
  the 18 they lost: nobody on their team is a king (their longest at r500: quartiles 8 / 24 / 41).
- **Their units do not go looking for the enemy queen.** She is rammed in 67 of 112 games (median r158) because 50 to 60 units are everywhere.
- **Since 8 Oct:** rank 1 -> 3 (behind larp 30-35 and horse 7-8, level with WeHaveQuizzes 35-31); the queen now grows at the unit cap instead of
  staying L2-3 (already so in the Qualifier); Trophy (24-8) and Devil (20-10) are no longer weak; Detention and Schooltime are (2.6).
## 1. Sample
- Game list: all 4,346 games of team 454 from 10 Oct 5:28 AM EDT (new pool) to 12 Oct 3:45 PM EDT. Ranked **805-261 (76%)**: new maps 388-112, old
  maps 417-149, 158-118 against the eight other top-9 teams, 22-3 against us. By half day the win rate fell from 86% to 68%, the rating from 2660
  to 2509. Worst maps: Portals 13-21, Tower Defense 12-14, Trauma 22-20, Detention 24-19, PD 19-15.
- Replays: **112 ranked games** (75-37; 3 to 6 per map on all 31 maps; all 25 against 952; losses and strong opponents over-sampled, median opponent
  2402), **all 21 Qualifier games from the quarter-final on** (14-7), and 18 more Detention / Schooltime losses for 2.6 (132 downloads).
- Parser fix: `notes/tools/replay_sim.py` counts each starting dragon 1 too long until its first split; my copy `rsim.py` corrects it.
## 2. What they do
### 2.1 How their games are decided
| | n | elimination | one queen alive, the other dead | both alive, longer queen | longest, both queens dead | longest, queens equal | total |
|---|---|---|---|---|---|---|---|
| ladder wins | 75 | 38 (median r285) | 20 | 0 | 11 | 5 | 1 |
| ladder losses | 37 | 10 | 5 | 7 | 15 | 0 | 0 |
| Qualifier wins / losses | 14 / 7 | 7 / 2 | 4 / 2 | 0 / 0 | 2 / 3 | 1 / 0 | 0 / 0 |
- The 7 "longer queen" losses: Portals 3 v 62 (us, parked queen) and 2 v 32, Trauma 3 v 34, Slithery 3 v 59 (larp), three sealed-room games at 2 v 3.
- The 18 longest-dragon losses (ladder + Qualifier): their longest 17 (median) against 51, their units 63 against 14 (Ouroboros 50 v 93 with 64
  units v 2, Metro 42 v 60 with 64 v 5). The winner's longest was 13 at r300 (median) and grew late, about half of it from own-team corpses.
  The 10 elimination losses: Caution x2, Tower Defense x2, Devil, PD, QoS, Stripes, Trophy, Atlantis.
### 2.2 Per map (aAah's side, ladder sample, medians; * = new map)
| map | ranked W-L | n | queen split at r0 | queen len r100/r300 | queen alive at r500 | queen steps from spawn r100 | units r50/r100/r200 | total r100/r300 | 60 units from | longest r300/r500 | lost per 100 rounds: self / ally body |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Athena * | 23-15 | 3 | 3/3 | 7/4 | 1/3 | 13 | 56/60/63 | 396/610 | r71 | 37/43 | 390 / 31 |
| Atlantis * | 20-9 | 5 | 5/5 | 2/2 | 0/1 | 36 | 6/52/40 | 137/33 | r110 | 3/4 | 113 / 0 |
| Caution * | 24-14 | 3 | 0/3 | 2/0 | 0/0 | 5 | 1/4/3 | 10/26 | never | 7/- | 22 / 1 |
| Detention * | 24-19 | 5 | 5/5 | 3/3 | 5/5 | 1 | 29/60/62 | 326/432 | r78 | 33/34 | 548 / 35 |
| Ezam * | 21-9 | 3 | 3/3 | 3/3 | 1/2 | 4 | 20/58/62 | 173/245 | r102 | 22/16 | 341 / 35 |
| Hive * | 25-1 | 3 | 3/3 | 0/0 | 0/3 | 12 | 56/59/61 | 310/532 | r66 | 31/62 | 316 / 9 |
| Maelstrom * | 22-12 | 3 | 3/3 | 6/8 | 0/2 | 14 | 38/62/62 | 320/466 | r64 | 26/60 | 186 / 7 |
| Metro * | 34-1 | 3 | 3/3 | 2/2 | 1/2 | 20 | 28/54/56 | 145/309 | r251 | 21/42 | 58 / 14 |
| Ouroboros * | 29-4 | 3 | 3/3 | 0/0 | 0/2 | 20 | 38/56/60 | 208/396 | r198 | 33/65 | 238 / 53 |
| Thermopylae * | 36-2 | 5 | 5/5 | 2/1 | 0/2 | 15 | 14/28/56 | 74/126 | r222 | 8/4 | 22 / 9 |
| Troll Australia * | 43-3 | 5 | 5/5 | 3/0 | 1/3 | 27 | 25/60/62 | 235/713 | r91 | 35/52 | 167 / 10 |
| Trolley Problem * | 23-12 | 6 | 6/6 | 2/0 | 2/6 | 36 | 5/24/52 | 63/153 | r258 | 6/16 | 318 / 9 |
| Trolley Problem (Buffed) * | 35-7 | 5 | 0/5 | 3/2 | 0/1 | 56 | 5/37/56 | 103/150 | r122 | 8/4 | 265 / 24 |
| Whale Song * | 29-4 | 5 | 5/5 | 3/5 | 4/5 | 36 | 17/52/57 | 141/380 | r197 | 21/24 | 68 / 7 |
| Around UNSW | 26-6 | 5 | 5/5 | 7/0 | 1/4 | 20 | 48/60/59 | 257/400 | r70 | 22/28 | 229 / 1 |
| Australia | 31-0 | 3 | 3/3 | 2/0 | 0/2 | 28 | 24/45/58 | 109/312 | r165 | 17/36 | 71 / 10 |
| Islands | 39-0 | 3 | 0/3 | 3/4 | 0/0 | 15 | 31/52/59 | 126/337 | r126 | 24/- | 132 / 12 |
| Schooltime | 28-9 | 3 | 3/3 | 3/3 | 3/3 | 1 | 13/54/62 | 159/416 | r128 | 30/40 | 239 / 14 |
| Slithery Fight | 22-8 | 5 | 5/5 | 2/3 | 4/5 | 5 | 60/60/62 | 231/311 | r50 | 17/23 | 518 / 2 |
| other 12 old maps | 271-126 | 36 | 15/36 | 2/2 | 9/13 | 13 | 8/16/28 | 40/93 | r283 | 5/5 | 72 / 2 |
### 2.3 Queen
- **Round 0:** she splits 4 -> 2+2 in 80 of 85 games where she starts at L4 or more (the 5 misses are all Trolley Problem (Buffed), r20 to r31);
  where she starts shorter, at her first L4. Every top team does it: larp 21/24, WeHaveQuizzes 15/15, chat gippy tea 12/13, FTM 5/5.
- **Length:** median 2 to 3 at every checkpoint. She splits like any unit until the team is near the cap, then grows because she cannot split, then
  sheds all but 2 in one split (39 -> 2 at r198 in one game). She passed L10 in 38 of 128 non-Slithery games, every time after the team first held
  60 units. No crown and no feeding: 3.1 of her 14.6 pearls a game are own-team corpses; she is the team's longest at r500 in 1 of 64 games.
- **Where:** 14 / 16 / 14 walking steps from her spawn at r50 / r100 / r300, 84% of her turns nearer her own spawn than the enemy's. **Portals:** 12
  crossings in 38,250 queen steps over 111 games (the team: 182 a game; Caution, Stripes, Portals, Trauma force her and are left out).
  **Deaths:** dead by the end in 56 of 112 (median r166, 15 by r100): rammed 42, moved into an enemy head 5, self hit 9 (boxed each time).
- **Survival follows mass.** Unit ratio at r100 against queen alive at the end, theirs / the opponent's (sealed maps excluded): below 2/3: 2 and 6 of
  18; 2/3 to 3/2: 21 and 9 of 52; 1.5x to 3x: 18 and 1 of 29; 3x or more: 16 and 0 of 22. Opponent queens that were L4 to L6 at r100 lived to the
  end in 1 of 23 games, L2 to L3 queens in 12 of 68.
### 2.4 Economy and the longest dragon
- New maps: 8 / 18 / 50 / 60 / 60 units and 25 / 43 / 131 / 286 / 328 total length at r25 / r50 / r100 / r200 / r300 (opponents in the same games: 8 / 14 /
  26 / 42 / 47 and 21 / 36 / 68 / 105 / 127). First round at 60 units: median r123, reached in 73 of 112 games.
- Pearls per 100 rounds on new maps: 536 (opponents 274); 34% of all they eat is own-team corpses. Per 100 rounds they lose 219 length to self hits
  (75 from L4+ units), 16 to ally bodies, 141 to enemies: on Athena about 3,700 a game, and our known build lost 3,844 there.
- At the cap (r200, 57 games at 56+ units): 61 units, 27 of them L5+, 13 L8+, total 320. Opponents at the cap: 10 L5+, 3 L8+, total 203.
  Splits (50,721): the parent keeps 2 in 77%; parent length L4 33%, L5 14%, L6-7 16%, L8-11 15%, L12+ 22%; 70% happen at 56+ units, 44% boxed.
- Spread (`spread.py`): 8x8 blocks holding one of their heads at r100: Maelstrom 33 (opponents 13), Troll Australia 36 (15), Detention 30 (17), Around
  UNSW 32 (17), Whale Song 31 (21). Portal crossings before r100: Detention 64, Thermopylae 63, Athena 42, Australia 41.
- Longest at r300 / r400 / r500: 21 / 27 / 32 on new maps, 13 / 12 / 17 on old. No persistent king: the body that is longest at r500 on the dense maps
  (41 games) was 11 / 15 / 19 long at r300 / r400 / r450 and has had 5 heads. They lose 18.7 units of L15+ per r500 game, half to rams, half to self hits.
### 2.5 Enemy-queen kills
- Ladder: one of their heads rams the opponent's queen in 67 of 112 games (plus 5 where she moved into a head); round quartiles 110 / 158 / 249,
  13 by r100. Killer: L2 17, L3 16, L4 12, L5-7 13, L8+ 9. Paid steps in 39 of 67; start distance 1 (24), 2 (11), 3 (13), 4 (8), 5 (9). Qualifier: 15 of 21.
- **No search** (`approach.py`): over 5 rounds, units 7 to 12 tiles from the enemy queen change their distance to her by +1.25 and to any other enemy
  unit by +1.31 (r30-149, 2,304 samples); 20% close 3+ tiles in both cases. No bias at 13 to 20 tiles or in later rounds either.
- **No queen preference at the hit** (`lunge.py`): share of turns with an enemy head in reach that end in a head-on: queen 1.9% (75 of 3,965), other
  units up to L7 2.5%, units of L8+ 5.6%. They prefer long targets, and a queen of L5 (her median when killed) is one.
### 2.6 Map notes
- **Detention, Schooltime** (`sealed.py`; 26 games on disk, 21 of their 28 losses). The room is 2x2, so a queen circles at L3. A room pearl forces
  eat -> L4 -> split -> L2 -> eat the child's pearl -> L3, which is what we and most teams do. aAah's queen instead pays a step (L3 -> L2) when a room
  pearl is due (16 paid queen moves in 14 of 26 games, 1 to 10 rounds before the opponent's mirrored eat) and then often gets no pearl. Result: 12
  losses at 2 v 3 (their longest 111, 43, 46 against a lone L3 queen), 2 losses with the queen dead (L4 at 64 units, no split possible), 7 losses
  and 5 wins at 3 v 3 decided by the longest (winners 39 to 84; their median 34 to 40).
- **Atlantis:** unseen-map play then and now (first portal crossing r19 in 6 of 7). They win when the opponent starves (52 to 60 units at r100
  against 6 to 10) and lose when the opponent is in the field first (3 of 3 losses: 5 to 10 units at r100 against 55 to 62).
- **Trolley Problem:** slow for everyone (4 / 5 units at r25 / r50), 24 at r100; all 7 sampled games went to r500 (4 on the longest with both queens
  dead, 3 on queens). **Buffed:** 37 units at r100, 184 pearls before r100 against 33; 4 of 5 games were eliminations (r185 to r416).
- **Thermopylae:** 63 portal crossings before r100 (opponents 29), 99 pearls against 47, opponent's queen dead at r51 to r172 in 6 of 7; both losses
  are to larp. **Whale Song:** queen alive at r500 in 6 of 7; all 6 wins are "their queen alive, the other dead". **Slithery Fight:** larp and
  WeHaveQuizzes keep a long queen (25 -> 7 at r0, then L54 to L84); aAah rammed her at r437, r473 and r479 and lost when she lived (3 v 59).
### 2.7 The 25 games against 952 (10 Oct x10, 12 Oct x15; aAah 22-3; our build was qf1)
- **Their wins:** elimination 12 (Stripes, QoS x2, weakhold, Trolley Buffed x2, Trophy x2, Islands, Troll Australia, Default, Around UNSW; r76 to
  r496); our queen dead and theirs alive 6 (Trolley Problem x2, Troll Australia, Whale Song x2, PD); longest with both queens dead 3 (Trolley
  Problem 19 v 13, Hive 64 v 3, Maelstrom 105 v 4); longest with equal queens 1 (Detention 32 v 28).
- **Our wins:** Caution (eliminated them at r74), Tower Defense (r191), Portals (parked queen L62 v L3). Our queen died in 22 of 25 (median r101, 11
  by r100): rammed 16 (9 by a paid lunge; she was L4 to L7 every time), boxed self hit 5, ally body 1. We rammed theirs in 8 games and lost 6 of them.
## 3. How we differ (the same 25 games)
| | aAah | 952 |
|---|---|---|
| queen's first split | r0, 4 -> 2+2 | median r36 at L7, keeps 5; r0 in 1 of 25 |
| queen length at r25 / r50; when rammed; dead by r100; alive at the end | 2 / 2; L2 in 29 of 50 (all games); 6; 15 | 4 / 4; L4 to L7 in 16 of 16; 11; 3 |
| units r25 / r50 / r100 (mean) | 7.6 / 16.0 / 34.9 | 6.3 / 10.6 / 18.9 |
| pearls before r50 / r100, the 13 big-map games | 56 / 275 | 27 / 105 |
| portal crossings before r50, big maps | 5.5 | 0.9 (0 before r100 on Around UNSW, Hive, Maelstrom, Whale Song) |
| share of tiles a head has stood on by r100 | 0.44 | 0.15 |
| length lost to ally bodies per 100 rounds | 9 | 20 (29 on new maps), with about a third of the units |
| longest at r500 (median) | 32, no king | 11 |
- On Detention and Schooltime our queen is already right: L3 at r500 in 37 of 37 of our own games (opponent L2 or dead in 4). 33 of the 37 were decided
  on the longest and we held it in 15 (ours 50, theirs 65, median). Our record there since 10 Oct is 39-36.
- The known build "hits the cap by r100 and then loses a lot of length" (QUAL_MAPS_OCT12.md). aAah loses as much and eats about the same (Athena 4,500
  pearls a game against our known 4,175, Hive 5,000 against 4,410). What they have at the cap is 27 units of L5+ and heads in half the map's blocks.
## 4. Candidate changes, by expected value (none built or tested; staging and server runs belong to the server owner session)
1. **Queen splits at r0 while we are few.** Evidence: 80 of 85 for aAah, 53 of 57 for larp, WeHaveQuizzes, chat gippy tea and FTM; ours 1 of 25. It is
   one more unit from turn 0 and a queen of L2 instead of L4 to L7 when heads arrive (2.3, last bullet). Maps: the 22 where she starts at L4+; first
   those with 2 or 3 starting dragons and no queen module of ours (Ezam, Trolley Problem x2, weakhold, Hive, Metro, Ouroboros, Devil). Reuse:
   `qFloorOff()` with `RP.queenKeep` / `RP.queenKeepR` (the TROPHY_QSPLIT / PM_QOS_QSPLIT mechanism) behind a map mask. Earlier evidence is mixed
   (TROPHY_QSPLIT +12 pp in one read, flat in another; l1 and QPARK_UNK lost). Check: unranked series on those maps against ranks 5 to 30, builds
   alternating; read first queen split round, units at r25 / r50 and queen dead by r100 before the win rate.
2. **Detention and Schooltime as a pure longest race.** Evidence: 2.6 and section 3: queens are equal in 9 of 10 of our games there, so the longest
   dragon decides; 70+ at r500 beats aAah's 34 to 40 and most of the 39 to 84 that beat them. Reuse: Schooltime's king schedule (`PM_SCH_KS`, the
   `v2("Schooltime", ...)` line); Detention through `QUAL_KNOWN` bit 3 with the same schedule and `QUAL_CROWD` bit 3. Keep `QBOX_RESERVE`: it prevents
   the death their queen dies at 64 units. Check: unranked series on the two maps; read our longest against theirs at r500 (now 50 v 65).
3. **Parked, growing queen where the map has a safe pocket.** Evidence: all four of their non-sealed "longer queen" losses are to a long safe queen
   (Portals 62 and 32, Trauma 34, Slithery 59); Portals is their worst map and our only non-elimination win. Reuse: `QUAL_QPARK` with `QUAL_QPARK_SEED`
   / `QUAL_QPARK_FEED` (the Atlantis "let her grow" item), `PM_QPARK_*`. Check: queen alive at r500 and her length; L9 beats 49 of their 56 living queens.
4. **Spread on the dense maps, measured against their numbers.** Evidence: 2.4 and section 3 (their heads are in 24 to 36 blocks at r100; our tile
   coverage is a third of theirs; 0 portal crossings before r100 on Around UNSW, a known map where we are 11-21). Reuse: `QUAL_CROWD` (Athena, Hive,
   Metro, Ouroboros, Detention), `CROWD_MAPS` bit 1 (Around UNSW), `UPE_HUNGER` (25 hungry rounds before a unit scouts a portal). Check: the
   `spread.py` counts on our own replays first, then unranked series on those maps.
5. **A king once our queen is dead.** Evidence: with both queens dead aAah wins only 14 of 32; about 50 at r500 beats their longest in three games of
   four; ours was 13, 3 and 4. Reuse: `UNK_KING_SEED` / `UNK_KING_FEED` (250 / 300), seeded earlier once `lhOurDead()` is true. Low value until the
   economy holds: in the 6 lost games where we had killed their queen we ended with 0 or 1 units.
## 5. Not determined
- Whether a small queen survives because she is small or because her team is bigger. Why their sealed queen pays the step (pearl timer, or an
  enemy head seen through the wall: the nearest was 2 to 7 away).
- Whether the queen's growth at the cap is a code change after 8 Oct or was missed by that sample. No submission history is public.
- Their sonar use and per-turn rules (split hazard, free steps, pearl choice): not redone. Per-map medians rest on 3 to 6 games. Nothing was built or run.
## 6. Rerun (from `/Users/devsingh/Developer/UNSW_Battlecode`)
```
python3 work/top3_oct12/aaah/crawl.py          # listing.json + qual.json (about 15 min; adds newer games to the saved list)
python3 work/top3_oct12/aaah/select_games.py   # games.json, downloads missing replays (--no-fetch: selection only)
python3 work/top3_oct12/aaah/analyze.py        # rows.json (2 processes, about 2 min)
python3 work/top3_oct12/aaah/report.py         # all tables; sections: compact decide queen econ splits lineage sizes qmass eqkill special vs952 qual
python3 work/top3_oct12/aaah/listing_stats.py  # ranked record per map, day and opponent;   timeline.py <gameId> <aAah side A|B>: one game
python3 work/top3_oct12/aaah/approach.py       # 2.5 search test;   lunge.py: 2.5 hit rates;   spread.py: 2.4 spread and portals
python3 work/top3_oct12/aaah/sealed.py         # 2.6 Detention / Schooltime (--fetch downloads up to 18 more losses)
```
