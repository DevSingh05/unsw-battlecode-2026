# larp stock zi balls (team 157, ladder #1, 2593): replay study, 12 Oct 2026

Data: their public game list, 10 Oct 09:28 UTC (5:28 AM EDT, start of the 31-map pool) to 12 Oct 19:33 UTC (3:33 PM
EDT): 1,350 ranked games. Replay sample: 122 ranked games on all 31 maps (3 to 6 per map) = the 20 games against us
(all 11 Oct, our qf1 build) + 62 wins and 40 losses against others. Losses are over-sampled (35% of the sample, 26% of
their games), so wins and losses are split where it matters. "Opp" = their opponent in the same games. "Us" = 120 of
our own ranked games (14 new maps + Around UNSW, 8 per map, qf1, opponents other than larp) through the same scripts.
"King line" follows the long body through reverse splits.

## 1. What they do

**Record: 1005-345 (74%); 14 new maps 481-118 (80%), 17 old maps 524-227 (70%).** Weak: Caution 6-30, weakhold 9-37,
Trophy 13-33, Devil 14-25, Portals 22-37, Ezam 24-19. Atlantis 39-10, Trolley 28-7, Trolley (Buffed) 43-10, Thermopylae
34-12, Detention 35-5, Whale Song 36-7, Around UNSW 38-7, Slithery 41-8, Troll Australia 48-2, Ouroboros 51-1.

**Queen (122 games).**
- Cut to length 2 at once. Start length 4 (21 maps, 84 games): split 4>2 at r0 in 75, at r2 in the other 9 (both
  Trolley maps, every game). Slithery (start 25): 25>18 at r0, 7>2 at r4, 5>3 at r5, every game. Start length 3
  (7 maps): first split at a median r18, as soon as she reaches 4.
- Kept at 2-3 until about r250: 349 re-splits 4>2 before r250; 2 or 3 long at r50 in 109 of 115 games; mean length
  r10-250 3.0. Stays on her own side: median 10-15 tiles from her spawn at r50/r100/r300; at r50 she is 3+ tiles
  further from the enemy queen's spawn than at the start in 63 of 112 games, 3+ closer in 9. An enemy head is in her
  7x7 view in 10% of her rounds (other opp queens 15%, ours in the 20 games 26%). Not parked (40-200 different tiles
  after r100). Crosses portals on Caution, Portals, Prisoners Dilemma, Stripes (14 of 15 games), never on Atlantis.
- Alive: r100 102/118, r200 64/101, r300 52/90, end 56/122 (wins 48/79, losses 8/43). Opp queens: 94/118, 60/101,
  47/90, 34/122 (8/79 in larp's wins). Of her 66 deaths 50 are enemy head-ons (median r141, her length 3), 12 walls.
- Fed from r250 with own-team corpses (1,833 of her 2,012 corpse pearls are from suicides). Median length of live
  queens in games that reach r500: r250 3, r300 10, r350 18, r400 20, r450 25, end 17. She reaches 8 in 52 games
  (median r258), 20 in 37, and is the team's longest at the end in 13. She loses length to her own late splits: of 26
  queens that peaked at 20+, median end length is 0.57 of the peak (30 length split off after r300; 5 died).

**How games are decided.**
| | n | elimination | queen: other side's dead | queen: longer, both alive | both queens dead: longest | queens equal: longest |
|---|---|---|---|---|---|---|
| larp wins | 79 | 38 (median end r226) | 14 | 3 | 19 | 5 |
| larp losses | 43 | 11 | 12 | 8 | 12 | 0 |

Maps up to 32x32 (39 games): 30 end by elimination. Larger maps (83): elimination 19, queen 34, longest 30. With both
queens alive at r500 (16 games) larp is 8-8; all 8 losses are a shorter queen (2-33 against 19-84; test4 four times).

**Economy (medians larp / opp).** Units r25 8/7, r50 15/14, r100 35/26, r200 61/38, r300 56/40. Total length r50
36/35, r100 81/65, r200 170/100, r300 192/104. Pearls eaten 1,436/744 a game, 43% of theirs from own-team corpses.
Cap (64 units) reached in 60 games, median r119: Maelstrom r67, Slithery r68, Ouroboros r72, Detention r80, Metro r81,
Athena r84, Atlantis r104, Around UNSW r116, Hive r123, Troll Australia r128, Whale Song r146, Trolley r175.
- Splits: before r100, 85% of non-queen splits are length 4 into 2+2. Whole game: 474 splits, 78% at length 4-5,
  19% reverse splits (parent keeps 2-3, the reversed child is the long part; 88 a game, opp 45): how long units turn.
- Length lost per 100 rounds (mean): r100-199 wall 70, self 54, ally body 46, own rams 54, rammed 40; r200-299
  suicide 154, wall 88, self 69, ally body 60; r300-399 suicide 244, wall 73, self 41, ally body 39. Their small
  units die on walls (103 a game, 95% length 2-3; why is not known), ours on themselves. On the ten big maps wall +
  self is 127 (r100-199) and 153 (r200-299) against our 129 and 148: playing at the cap costs them what it costs us.
- Rams (own move into an enemy head, 15 comparison maps): larp 95 a game, 2.8 of their length for 3.8; we make 64,
  3.1 for 6.0. Opponents' rams take 4.8 from us and 2.9 from larp, whose army is nearly all length 2-3.

**King building.** Longest dragon, 73 games that reach r500 (larp / opp): r200 8/5, r300 22/7, r400 47/16, end 64/28.
Ten big maps (Around UNSW, Athena, Detention, Ezam, Hive, Maelstrom, Metro, Ouroboros, Troll Australia, Whale Song):

| | n | king line r250 | r300 | r350 | r400 | r450 | end | 2nd longest end | total r300 | king-line pearls r200-299 / r300-399 / r400-499 |
|---|---|---|---|---|---|---|---|---|---|---|
| larp | 30 | 7 | 17 | 38 | 57 | 72 | 97 | 48 | 268 | 24 / 48 / 51 |
| us (qf1) | 75 | 3 | 4 | 12 | 25 | 37 | 55 | 28 | 227 | 7 / 24 / 33 |

- Method: the suicide action (not timeouts), 121 a game (233 on the big maps); 43% length 2, 35% length 3, 8% length
  8+. The first is at exactly r250 in 27 games; median first-decile round r269.
- Local, not a walk to the king: at the suicide a longer ally head is in the 7x7 view in 80% of 14,802 cases and an
  ally of 8+ in 52%, but the team's longest is within 3 tiles in 10% (median 19 away). The pearls are eaten a median
  2 rounds later: 51% by units of 8+, 40% by small units, 6% by the queen, 2% lost.
- 59% of the king line's pearls are own-team corpses, 76% of those from suicides. The king is the queen in 10 of 73.

**Enemy queen.** Dead in 88 of 122 games, 73 by a head-on with a larp unit (larp moved in 71): before r100 19,
r100-299 40, r300+ 14. Killer length 2-3 in 52 (4-6: 16, 7+: 5), born a median 24 rounds earlier; 43 of 71 kill moves
are 2-5 steps; the killer was 14/11/8/4 tiles away 20/10/5/1 rounds before. They do not look for her: larp heads
within 6 of the enemy queen against within 6 of an average enemy unit are 0.44/0.53 (r20-99), 0.83/0.79 (r100-249),
0.74/0.82 (r250+), 0.44/0.72 when she is 10+ long. Still, ten queens of 18+ died at r295-493, nine to units of 2-5.

**Special maps (larp / opp medians; n = sample games).**
| map | n, W-L | queen: first split; dist from spawn r50/r100/r300; alive r200; at end | units r100 | total r100; r300 | cap | longest r300/r400/end (opp end) | decided by |
|---|---|---|---|---|---|---|---|
| Atlantis | 5, 3-2 | r0; 15/15/19; 3/3; L2, L2, L23 | 60/8 | 145/23; - | r104 | 34/95/153 (1 game) | elimination 4, opp queen dead 1 |
| Trolley | 4, 2-2 | r2; 12/8/8; 4/4; L7-17 | 19/16 | 48/38; 180/50 | r175 | 11/26/40 (22) | opp queen dead 2 (W), queen shorter 2 (L) |
| Trolley (Buffed) | 5, 3-2 | r2; 11/11/3; 3/5; 1 alive | 23/22 | 60/62; 84/124 | 1 of 5 | 8/8/27 (28) | longest 4 (lost 27 v 28, 26 v 29), opp queen dead 1 |
| Thermopylae | 6, 4-2 | r0; 15/20/17; 4/6; L26, L50 | 24/22 | 54/56; 72/68 | 1 of 6 | 8/20/30 (12) | queen 3, longest 2, elimination 1 |
| Detention | 4, 2-2 | r0; sealed 2x2 room, L3 | 62/37 | 274/122; 406/144 | r80 | 68/87/166 (20) | longest 2 (W), queen died at L4 2 (L) |
| Whale Song | 4, 2-2 | r0; 5/12/5; 4/4; L15-71 | 42/40 | 104/100; 268/130 | r146 | 32/49/66 (49) | queen length 3, opp queen dead 1 |
| Troll Australia | 5, 3-2 | r0; 7/11/13; 3/5; 0 alive | 62/56 | 162/129; 317/54 | r128 | 32/82/140 (11) | longest 3, elimination 1, own queen dead 1 |
| Around UNSW | 5, 3-2 | r0; 7/13/21; 4/5; 1 alive | 56/60 | 131/166; 245/169 | r116 | 26/54/88 (39) | longest 2, queen 3 |
| Slithery | 6, 4-2 | r0 (L2 by r5); 12/25/17; 6/6; L17-86 | 63/61 | 175/160; 209/206 | r68 | 24/54/64 (42) | queen length 3, opp queen dead 1, longest 1, elim 1 |

- Atlantis: 13-29 portal crossings and 250-310 pearls by r100 in the wins; both losses (acegi) were lost by r100
  (63-77 pearls against 297-334). The queen never crosses; in four of five games she circles 16-39 tiles.
- Trolley (both): almost no enemy head comes near the queen (0.03 within 6); alive at r200 in 7 of 9; tiebreak games
  with small margins. Troll Australia: the one loss to a weaker team was acegi's live L10 queen against a 195 king.
- Detention (and Schooltime): she splits 4>2 at r0, the child dies in the room, she eats its pearl, circles at L3 and
  splits again whenever a pearl takes her to 4 (r36, r165, r172). At 64 units she cannot split and dies on the wall
  (Detention r200, r248; Schooltime r180): both Detention losses, to teams near 2,100, while ahead 417-106 and 531-69.

**Against us (20 games, 11 Oct, qf1): 17-3.** Elimination 9 (larp 8, us 1: Prisoners Dilemma r69); both queens dead
then longest 5, all larp (their longest 26-185, ours 10-39); our queen dead, theirs alive 3; ours alive, theirs dead 1
(Portals: their queen hit a wall at r98); Trauma our queen 20 against 12; Schooltime equal queens, longest 91-3.
Our queen was dead by r129 in 15 of 20 (10 rammed, 9 of them by units of length 2-4; 1 walked into an enemy head; 2
hit herself; 1 rammed by an ally; 1 hit a wall) and split at r0 in 3 of 20. Medians larp / us: units r50 20/12, r100
43/27; total r100 102/65, r200 229/84; pearls by r100 122/69; longest r300 28/5, end 86/13.

## 2. How this differs from our bot

| measure (the 15 comparison maps unless noted) | larp | us (qf1) |
|---|---|---|
| queen split at r0 | 81/122 (every start of 4+ except Trolley, r2) | 30/455 (14 new maps + Around UNSW; median first split r38) |
| queen length at r100: median; share 5+ | 3; 8/59 | 5; 67/89 |
| queen alive r100 / r200 / end | 59/61, 36/57, 25/61 | 89/116, 47/113, 18/120 |
| queen death: median round, length, distance from spawn | r177, 3, 11 | r135, 5, 22 |
| queen distance from spawn r50/r100: Trolley; Buffed; Around UNSW; Troll Aus | 12/8; 11/11; 7/13; 7/11 | 26/29; 22/28; 19/22; 16/14 |
| queen alive at r200: Trolley; Buffed; Whale Song; Around UNSW | 4/4; 3/5; 4/4; 4/5 | 1/8; 1/8; 5/8; 1/8 |
| units r100; total r100 | 43; 106 | 30; 76 |
| longest r300 / r400 / end; end as share of total r300 | 18 / 52 / 70; 0.35 | 14 / 34 / 48; 0.25 |
| Detention: units r100, total r100, longest end | 62, 274, 166 | 28, 73, 46 |

- Not the gap: same split rule (SPLIT_LEN 4, SPLIT_CHILD 2), better ram exchange, same collision loss at the cap.
- Our queen plays the pre-QUEEN_SAFE rules until QS_FROM (r100), is 5 long, walks 20-30 tiles from home on the
  Trolley maps and Around UNSW, and is rammed at a median r135. Theirs is a length-2 unit within about 12 tiles of
  home. Existing code: qsrBlock (QSPLIT_ROOM, QSR_A 16, QSR_ALLY 2) is one gate on her splits (why she does not split
  at r0 was not traced); LANE_QSMALL (QSM_KEEP, QSM_RAD 6, QSM_PULL; RP.qSmall) is a small home queen for lane maps;
  QUAL_QHOME (QUAL_QHOME_R 8) is a home leash for known Qualifier maps.
- Our feed starts at UNK_KING_SEED 250 / UNK_KING_FEED 300 (FEED_START 330, KING_V2_MERGE_ROUND 380) and, by its
  flags (FEED_PULL, KING_CONSENSUS), brings feeders to one king; our king-line pearls jump at r300. Theirs starts at
  r250 and a small unit feeds whichever longer ally it sees: their king line runs about 100 rounds ahead of ours.

## 3. Candidate changes, by expected value

1. **Small home queen where ours dies far from home.** Split at r0 (start length 4+), re-split at 4 until the feed
   round, leash of 10-12 walking steps. Evidence: queen rows above; "our queen dead, theirs alive" decides 12 of 27 of
   our Trolley games, 10 of 30 Buffed, 16 of 33 Whale Song, 15 of 32 Around UNSW. Maps: Trolley x2, Whale Song, Around
   UNSW, Troll Australia, Thermopylae. Reuse: LANE_QSMALL bits (QSM_KEEP 2, QSM_RAD 10) or QUAL_QHOME (R 10-12), and
   whatever gates her first split (qsrBlock is one). Check: unranked series on those six maps against ranks 5-30, base
   and candidate against the same opponents; read queen alive at r200/r500, her distance from spawn at r100 and the
   share of games decided "our queen dead" (analyze.py gives all three).
2. **Feed from r250, and locally.** Evidence: king line table (97 against 55 from similar totals); "both queens dead,
   longest decides" is 29/31 of our Athena games, 33/42 Metro, 23/26 Ouroboros, 18/23 Hive, 27/31 Maelstrom, 25/31
   Troll Australia; Detention is 28/30 longest. Maps: those seven. Reuse: per-map RP.kingSeedRound / RP.feedStart
   (UNK_KING_SEED 200, UNK_KING_FEED 250; REAL_SWEEP had this at .537 locally), KING_V2_MERGE_ROUND about 300. "A
   longer ally head in view: suicide" would be new code behind a flag. Check: unranked series on those maps; read
   king line at r300/r400/end (analyze.py, king_lineage_len) and the record in games decided by longest.
3. **Detention as a longest-dragon race, with the queen's split kept legal.** Evidence: 166 against our 46 at the end,
   62 against 28 units at r100; larp's two losses are the queen stuck at L4 with 64 units. Reuse: QUAL_KNOWN bit 3 +
   QUAL_CROWD bit 3 (local 2-2), the early feed from 2, and a cap of 63 on Detention and Schooltime (SPLIT_MAX_UNITS,
   or only the queen may use the last slot). Check: unranked Detention-only series; queen alive at r500 must stay
   100% (ours is 30/30 as an unseen map), then longest at the end.
4. **Feed the surviving home queen from r250-300.** Evidence: with both queens alive the longer wins and larp is only
   8-8; their queen is a median 20 by r400; 12 of their 14 games on Trolley, Whale Song and Slithery were decided by
   the queen tiebreak (8 on length). Our parked Atlantis queen stays at L4. Maps: Atlantis, Trolley x2, Whale Song,
   Slithery. Reuse: QUAL_QPARK_QKFROM / QUAL_QPARK_FEED / QUAL_QPARK_QKCAP, RP.queenKing, QG_RAM and QK_EG to guard
   her. Do not copy their late queen splits. Risk: larp's small units killed nine 18+ queens. Check: after 1, same
   series; read queen length at r400/r500 and the "queen longer / shorter" results.
5. **Atlantis: the first 100 rounds decide.** Evidence: 250-310 pearls and 60 units by r100 in larp's wins, 63-77 and
   5-7 in both losses; queen at home. Supports km1's "route off + parked queen" plus 4. Check: build_watch.py.

## 4. Not determined
- Whether they store map data: identical openings every game on Slithery and Trolley fit either answer.
- How their queen picks moves; only where she is and what she meets were measured.
- Why 103 units a game die on walls. Not feeding (5% within 3 tiles of the longest ally). The queen died this way 12
  times: Portals 4 (dead-end pockets, r83-389), Detention/Schooltime 3, five others.
- What keeps test4's and horse's long queens alive against larp's rams; whether larp changed builds on 10-12 Oct.
- Per-map rows rest on 3-6 games: indications, not rates. All 20 games against us are qf1 (last met 11 Oct 10:54
  UTC), so nothing here measures km1/km2 against larp.

## Rerun (from /Users/devsingh/Developer/UNSW_Battlecode; read-only GETs paced 1.4 s; 2 worker processes)
Run `python3 work/top3_oct12/larp/<script>` in this order: `crawl.py` (listing.json, about 390 pages) -> `sample.py`
(record.json; keeps sample.json, `--repick` redraws; downloads missing replays) -> `analyze.py` (rows.json) ->
`summary.py [record|queen|decide|econ|king|eqkill|vs952|maps]` -> `deep.py` (suicides, wall deaths, rams, queen
series) -> `queen_geo.py` -> `hunt.py` -> `us_baseline.py` (same measures on 120 of our games in work/oct12/replays).
