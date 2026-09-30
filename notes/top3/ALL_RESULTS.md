# Top-3 study results (saved by main agent)

{
 "track": "cheji bt (team 70, #1, elo ~2119)",
 "games_used": "40 recent games of cheji against peers rated 1900 or more (forgot to mention, 中国必须人能飞, SSS, Sabotage-d, Sponge). All 10 maps, at most 4 per map, played 30 Sep 00:36-02:02 UTC, in notes/top3/cheji_bt/replays. Cheji won 27/40. 34 of our games against cheji (ledger 15, replays/ab_* 14, 5 new games 649046-50): we won 8/34, 4/20 round-limit and 4/14 elimination. Control: 107 of our games since 29 Sep 15:00 against the same peer teams (we won 56). The full report is at /Users/devsingh/Developer/UNSW_Battlecode/notes/top3/cheji_bt/REPORT.txt. The scripts (analyze.py, agg.py, consol.py, wave.py, hazard.py, localfeed.py, feedeff.py, survive.py, bigmerge.py, splitline.py, sprints.py, sprint_eat.py, corpserace.py, bleed.py) and their out_*.txt outputs are in the same directory.",
 "key_numbers": "Units/total/longest are map-averaged. \"Us\" is our games against the same peer teams; \"vs\" is the direct cheji-v-us games.\n\n| Round | cheji vs peers | us vs peers | vs: cheji | vs: us |\n|---|---|---|---|---|\n| r60 | 15.9/38.8/4.1 | 19.1/45.5/3.7 | 16.1/38.9/3.8 | 19.3/45.8/3.5 |\n| r100 | 24.8/59.3/3.9 | 26.1/63.3/4.0 | - | - |\n| r200 | 32.5/87.0/4.6 | 34.2/88.0/5.2 | - | - |\n| r300 | 35.5/98.1/4.9 | 32.3/94.7/9.1 | 28.8/79.1/4.2 | 22.4/60.7/5.6 |\n| r400 | 20.9/89.6/12.4 | 29.8/101.7/14.5 | - | - |\n| r500 | 19.5/80.4/18.1 | 20.8/101.6/20.8 | 11.6/68.8/23.0 | 15.7/79.6/15.9 |\n\nRound-limit games against us (20), units/total/top1:\n\n| Round | cheji | us |\n|---|---|---|\n| r250 | 46.8/134/6.5 | 45.3/114/6.0 |\n| r325 | 47.4/147/10.5 | 26.4/94/15.6 |\n| r350 | 14.6/120/18.4 | 22.9/94/18.9 |\n| r400 | 6.9/119/28.1 | 22.0/105/21.8 |\n| r475 | 4.5/109/44.9 | 16.2/133/33.0 |\n\n- Portals has no contact between the teams. We have more mass at r300 (84 v 69) and still lose the king race 42 v 31. Cheji turns 62% of its r325 mass into the final king; we turn 41%.\n- Eats per phase (r1-60 / 61-200 / 201-350 / 351-500): cheji 56/225/218/67; us 91/328/313/221.\n- Splits per phase: cheji 21/69/52/12; us 40/125/116/73. Growth splits of 4 into 2+2 after r350: 0.55 v 63.\n- Deaths per phase: cheji 11/53/62/14; us 26/110/120/81. Cheji's non-ram deaths are all NoValidAction (the dragon outputs no action and dies in place).\n- Splits per 25 rounds: cheji 21 up to r325, then 10, then 3-5. Ours stay at 30-35 until r450.\n- Rams per game in r61-200 / 201-350: cheji 12.8/6.4, us 13.4/9.0. Directly against us, cheji 11.9/12.0 and us 10.5/7.1. On Schooltime in r201-350 it is 48.8 v 22.\n- Sprints per game: cheji 83 (62 of them eat pearls: 27 corpse, 31 contested), us 14 (almost all L3 rams).\n- Corpse race after head-on fights, r1-350, against us: cheji eats 106 pearls per game (31 by sprint), we eat 71 (0.9 by sprint).\n- Mass change r200 to r325 against us: cheji +14.7, us -20.1. Natural eats are equal (258 v 252). Our trapped suicides are 162 v 55.\n- Late big merges (r300+, L8 or more) against us: cheji 6.2 per game (98 length, the king eats 12.6 of the pearls); us 2.3 (29 length, the king eats 0.95).\n- Final king (map-avg max at r500): cheji 18.1 v us 20.8 against peers, but 23.0 v 15.9 head to head.\n- How games end (map-avg): cheji wins by elimination 47% (us 30%) and loses by elimination 15% (us 19%).\n- Portal crossings and deaths up to r350: equal.\n- Distance from king to nearest enemy head after r400: 11.0 v 11.7.",
 "behaviours": [
  {
   "what": "A synchronized consolidation wave at about r325 on every map. Growth splits stop (21 falls to 10, then 3-5 per 25 rounds). Small dragons (L2-5) die in place next to a LONGER ally they can see in their 7x7 view, and that ally eats the corpse. The result is a local, tournament-style merge into a tier of medium dragons, not travel to one global king. Units fall from 47 to 15 in 25 rounds and to about 5 by r450, while mass falls only from 147 to 120.",
   "evidence": "wave.py: every round-limit game (Slithery, Portals, Schooltime, Trauma, Autarky) starts its burst at r320-330, peaking r330-342; for example 650307 goes 56 to 20 units between r330 and r344. hazard.py (r325-360, L<=5): per-round death chance 0.26 when an L10+ ally is visible, 0.16 for an L5-9 ally, 0.027 for none; before r320 it is 0.015-0.03 regardless. localfeed.py: 29.5 of 53 pearls per game are eaten by the specific nearest visible bigger ally, and 92% by the team. The eaters are L5-19 in 60% of cases. Top three at r350 are 18/14/12 and at r400 28/22/18.",
   "we_do": "We keep 4-into-2+2 splitting until r450 (LATE_SPLIT_ROUND 450 / LATE_SPLIT_MAXLEN 5, variants/v31/params.hpp:550, main.cpp:3420), about 30-35 splits and deaths per 25 rounds up to r450, and 22-25 units at r400-450. Feeding goes only to one consensus king (shouldFeed, main.cpp:1965-1980: kingLen>=myLen+2, KC_FEED_FRAC 0.75, feed length at most 3 until r380, 6 until r420). 63% of our own-corpse pearls after r330 go to dragons outside the top 10 (pump recycling).",
   "general": true,
   "impact": "The biggest factor. It explains our round-limit losses to cheji (16/20, including 5/6 on Portals where we had more mass). King at r475 is 44.9 v 33.0. At cheji's conversion rate (62%) our Portals r325 mass would give a king of about 47 against their 42. Suggested flag WAVE_R=325: from that round, no growth splits for L<=5, and a small dragon feeds (moves in front and dies) next to ANY longer own head within Chebyshev 3; keep about 4 reserve dragons. The simplest first test is LATE_SPLIT_ROUND=330 alone. Test on the server, Portals plus Slithery against the top 10."
  },
  {
   "what": "No king-building before the wave; the swarm keeps harvesting. Every dragon stays L2-5 (top1 about 7 at r300; on Portals 4.5 at r300) at the unit cap (64 on the big boards), so team mass keeps growing from r250 to r325.",
   "evidence": "Against peers, top1 at r300 is 7.6 v our 12.4; on Slithery against us it is 7.2 v 18.8. bleed.py, r200-325 in round-limit games against us: mass +14.7 v -20.1 with equal natural eats (258 v 252) and equal enemy head-on deaths (31 v 31). Our churn: 162 trapped suicides v 55, 218 splits v 118, own-corpse re-eats 298 v 176. Total at r325 is 147 v 94.",
   "we_do": "Per-map king seeding from about r170-250 (RP.kingSeedRound / KING_SEED_ROUND) plus pump/feeding from r250. Our mass falls from 114 to 94 between r250 and r325. On Slithery we lead the king race until r375, then lose at r450-500 (37.5 v 46.8) because their mass pool is about 40 larger.",
   "general": true,
   "impact": "About 35 mass by r325 in the head-to-head games. Counter-example: on Trauma our early single king beats peers 6/6 and cheji is 1/3 there. So test a later or no king seed on Slithery and Portals only, together with WAVE_R; do not change Trauma."
  },
  {
   "what": "Big-dragon merge into the king at r350-480. After the wave, the smaller big dragons (L8-32) output no action and die 1-2 tiles from the king, which eats about 85% of their pearls. Big dragons also U-turn by splitting off their rear L-2 segments and letting the L2 front die.",
   "evidence": "bigmerge.py against us: 6.2 such deaths per game (98 length), king eats 12.6 of the pearls. Examples: 650042 r436, an L28 dies at distance 1 from the L38 king, which eats 12 of 14 pearls; 650303 r433, an L26 dies at distance 2 from the L27 king, which eats 12. Portals top2 goes from 19.7 at r400 to 14 at r475 and the king from 28 to 42. Big splits of L10+ after r300: 23.7 per game against our 13.2.",
   "we_do": "Big non-kings feed only after KING_V2_MERGE_ROUND 420 and only a king that is 2 or more longer. Self-declared kings step down only after hearing two longer kings (KING_MERGE_STEPDOWN from the forensics notes is not in v31). We have 2.3 big non-king deaths per game (29 length); the king eats 0.95, and most of these deaths are HitSelf or rams.",
   "general": true,
   "impact": "About +12 king length per game in the head-to-head games. Cheji's own weakness is that it keeps a top three too long (r400 top three 38/25/23), and single-king peers (SSS 79, Sabotage-d 84 on Slithery) beat it. So merge into one king earlier: KING_V2_MERGE_ROUND about 380 plus KING_MERGE_STEPDOWN, on top of WAVE_R."
  },
  {
   "what": "Sprint to grab contested and corpse pearls. L3-4 dragons do 2-3 step sprints to snatch pearls, especially corpse pearls, near enemy heads, paying about 1 length for tempo. This wins the post-fight corpse race.",
   "evidence": "sprints.py: 83 sprints per game (2581 two-step and 612 three-step over 40 games); 37 per game to eat, 10 to kill, 10 to flee. Net length: -1 in 1447, 0 in 871, +1 in 433. sprint_eat.py: 62 sprint-eats per game (110 against us), 27 corpse and 31 contested (enemy head within 3 of the pearl). corpserace.py: of the corpse pearls dropped by head-on fights in r1-350, cheji eats 106 v our 71 per game (31 v 0.9 by sprint); against peers 73 v 41. Enemy-corpse eats in r201-350 against us: 20.4 v 9.9.",
   "we_do": "We sprint only to ram (about 14 per game, almost all L3 2-step rams; 0.2 eat-sprints). EAT_SPRINT=0 (params.hpp:448); it was rejected at 0.46 in v15 self-play, which cannot show a corpse race against a sprinting opponent.",
   "general": true,
   "impact": "About +35 corpse pearls per game in the head-to-head games, roughly half of the 35-mass gap at r325. Matters most on contact maps (Schooltime, Slithery, Autarky, Devil). Suggestion: a narrow EAT_SPRINT that fires only when the path includes a corpse pearl under 3 rounds old with an enemy head within 3 of it, for L>=3, max 2-3 steps, with the step-by-step threat check. Server A/B on Schooltime and Slithery; target a corpse-race share above 50%."
  },
  {
   "what": "A high-volume midgame ram war on Schooltime (sprint rams while locally ahead), reaching and holding 64 units while our swarm collapses.",
   "evidence": "Schooltime against us, r201-350: cheji rams 48.8 per game (28.6 sprint rams, 31.2 while locally ahead) against our 22.2. Units r200 to r300: ours 41 to 17, theirs 50 to 64 (map averages from agg.py; the separate cheji-vs-us wave table gives 55 at r300). Total at r300: 199 v 63. On other maps ram counts are about even (Slithery 19 v 17).",
   "we_do": "The known Schooltime layout-B swarm-war loss (notes/forensics Schooltime): our units collapse between r200 and r300.",
   "general": false,
   "impact": "Decides the Schooltime games (we lost 3 of 4 round-limit games there, 5/6 in total). Not a generic lever beyond #4 (corpse race) and the existing forensics fixes."
  },
  {
   "what": "Early ram aggression and pocket control on small pocket maps (Devil, Queen of Spades, Autarky), leading to early elimination.",
   "evidence": "Devil 649048 and 632910: cheji rams 8-11 times before r80 and eats 75-96 pearls by r60 against our 31; units at r60 are 25 v 5 and 14 v 2. QoS 625540 and 608228: our 6-7 trapped HitSelf deaths plus 3-4 rams leave us at 4-7 units at r60 against 9-11. Against cheji we lose Autarky 6/6, QoS 2/2 and Devil 2/3 by elimination.",
   "we_do": "Covered by earlier studies: the notes/22 Autarky pocket race (POCKET_FACTORY) and the Devil forensics (box bonus, hot pockets, idle wanderers).",
   "general": false,
   "impact": "About 10 of our 26 losses to cheji, but nothing specific to cheji beyond the existing notes. Not ranked above #1-#4."
  },
  {
   "what": "Death style and early game, checked and NOT levers. (a) Cheji's non-ram deaths are all NoValidAction (no action; the dragon dies in place), never HitSelf or HitWall; the pearls land the same way, so this is cosmetic. (b) Opening: first split at r9, and more spread (nearest own head 6.5 v 4.6 at r30), but less mass than us at r60. (c) Portal crossing rate and fatality up to r350, and king distance to enemy heads late, are equal to ours.",
   "evidence": "dive_novalid.py: all 4000+ NoValidAction deaths are 'no action'. Opening, map-averaged: eats r1-60 56 v 91; total at r60 38.8 v 45.5. Portal crossings in r61-350: 57/60 v 62/59, fatal 4.8/6.1 v 5.1/6.0. King-to-nearest-enemy distance after r400: 11.0 v 11.7. Deaths of the team's longest L8+ dragon after r300: 0.47 v 0.25 per game.",
   "we_do": "Same or better.",
   "general": true,
   "impact": "None; do not chase. Correction to notes/16 #3: the #1 team does NOT keep splitting after r350 (0.55 v our 63 4-into-2+2 splits per game). LATE_SPLIT_ROUND=450 was built on that premise and should be re-tested at 330 on the server."
  }
 ]
}

---

{
 "track": "Stockfish (team 206). Full report: /Users/devsingh/Developer/UNSW_Battlecode/notes/top3/Stockfish/REPORT.txt. Scripts, data (metrics.pkl, index.json, listing.json) and 50 new replays are in /Users/devsingh/Developer/UNSW_Battlecode/notes/top3/Stockfish/. The scripts are collect.py, agg.py, kingrace.py, onset.py, feedpipe.py, feeders.py, kingwatch.py, churn.py, childfate.py, sprints.py, bigsplits.py, bigrams.py and harvest.py. All requests were GETs, all computation single-process, and nothing under bot/, variants/, tools/ or maps/ was modified.",
 "games_used": "Stockfish against strong teams (elo 1940+): 50 games, 5 per map on all 10 maps, played 30 Sep 00:14-02:04 UTC, downloaded into notes/top3/Stockfish/replays. Stockfish won 60% (map average). Us against Stockfish: 39 games (we won 18). 15 are from the ledger, 14 from our A/B batches (ab_kc31, pf31, pk30, schb31, v29aut, v29ds2, v30kc, v30sch, v31c), and 10 are fresh v31 games from their listing (649071-5, 651741-5). Of Stockfish's 21 wins, 19 were round-limit king races and 2 were eliminations. By map, our wins/games: Slithery 1/9, Portals 1/6, Autarky 4/7, Schooltime 1/3, Trauma 1/3, Queen Of Spades 1/2, Default 2/2, Devil 4/4, Prisoners Dilemma 2/2, Trophy 1/1. Baseline: 138 of our ledger games since 29 Sep 17:00 against strong non-Stockfish teams.",
 "key_numbers": "All figures map-averaged.\n\nUnits/total/longest, all games, Stockfish vs us (SFu) against us vs Stockfish (U):\n- SFu: r50 12.7/31/3.3, r100 20.0/52/3.8, r200 25.4/73/4.0, r300 21.4/71/9.9, r400 14.5/78/17.9, r500 10.6/83/23.8.\n- U: r50 17.4/41/3.6, r100 27.4/66/3.9, r200 34.1/85/4.9, r300 31.7/86/7.2, r400 30.7/91/12.6, r500 25.3/91/16.9.\n\nRound-limit games only (26 games):\n- SFu: r100 33/87/5.0, r200 46/132/6.5, r300 39/130/17.0, r400 26/148/34.5, r500 17.5/157/46.8.\n- U: r100 34/83/4.6, r200 39/99/6.3, r300 30/90/11.2, r400 26/96/21.6, r500 14/94/31.1.\n- The economy is even at r100. Stockfish gains about 33 total length in r100-200, on Slithery, Schooltime and Autarky only.\n\nKing as a share of total length at r350/r450/r500:\n- SFu .22/.44/.45; U .20/.28/.40.\n- Us against other strong teams .15/.26/.31; those teams .18/.37/.47.\n\nRound the longest dragon reaches 20/30 (Stockfish vs us):\n- Portals: 305/361 vs 414/473.\n- Schooltime: 321/377 vs 433/444.\n\nFeeding onset (median round):\n- Portals 168 vs 314; Autarky 130 vs 412; Trauma 255 vs 320; Slithery 253 vs 223.\n\nOwn-corpse pearls eaten by L10+ dragons per 50 rounds, r250-500: SFu 10-13 vs U 4-10.\n\nEats per phase (r0-60/61-150/151-300/301-400/401-500):\n- Stockfish vs strong teams 63/144/241/138/95; us vs Stockfish 84/183/284/152/109. We eat more but die more.\n- Length lost to deaths in r151-300: 222 (theirs) vs 278 (ours).\n\nDeaths by cause, r151-300, Stockfish vs us:\n- head-on with an enemy 17 vs 19;\n- into an ally body 8.9 vs 18.6;\n- self 29 vs 67;\n- wall 27 vs 3;\n- trapped (0 free exits) 48 vs 76.\n\nSplits by parent length L4/L5/L6/L7+: 140/42/18/21 vs 288/17/3.6/4.6. Splits of L10+ dragons after r400: 6.0 vs 1.6.\n\nRams:\n- Symmetric before r400 (r151-300: 9.0 vs 9.4).\n- After r380: 3.7 per game by them vs 1.7 by us.\n- Our L10+ dragons rammed: 0.62 per game against Stockfish, 0.28 against other strong teams. Theirs rammed by us: 0.13.\n\nSlithery at the 64-unit cap (r61-300):\n- splits 388 vs 643; deaths 389 vs 648;\n- stillborn (die within 5 rounds of birth) 127 vs 257;\n- total length at r150 215 vs 154.\n\nEndgame (round-limit):\n- Units at r450: 16.6 vs 23.8.\n- Small dragons (L3 or less) at r450: 3.0 vs 8.8.\n- Feeder deaths near an L10+ king: about 27 per game on both sides. Feeder median length 3 vs 2.\n\nSonar: 34,000 pings per game vs 4-5,000.",
 "behaviours": [
  {
   "what": "Early, committed king with a continuous feeding conveyor. One dragon at about L6-12 becomes king around r250 by default, and at r110-240 on Portals and Autarky. From then until about r480, small dragons of about L3 kill themselves 2-4 tiles from the king's head: 92% HitSelf (reversing into their own neck) with 2 free exits. The king eats the pearls 1-3 rounds later, about one pearl every 2-3 rounds, and never stops.",
   "evidence": "Portals 646840 (kingwatch.py): their king went L6 at r255, L18 at r290, L30 at r329, L49 at r450; our king was only L8 at r315. Feeding onset (median round): Portals 168 vs our 314; Autarky 130 vs 412; Trauma 255 vs 320; Schooltime 262 vs no onset in 2 of 3 games. In round-limit games their king is 16.8 vs 11.1 at r299, 24.8 vs 16.8 at r349 and 44 vs 24 at r449. Own-corpse pearls eaten by their L10+ dragons: 10-13 per 50 rounds vs our 4-10. Portals: 5 losses where our total was equal or larger (75-88 vs 59-87) but our king was 25-31 vs 39-64. Trauma 649072 and 651745: we had 36 units, 119 total and a king of 32 at r450; they had 6 units, 60 total and a king of 42.",
   "we_do": "variants/v31/main.cpp applyMapParams and the KING_V2 table: Portals seeds the king at 250, starts feeding at 300, stops splitting at 360; Autarky seeds at 380 (PM_AUT_KS); Trauma seeds at 450 (PM_TRA_KS); global FEED_START is 330. In practice our king candidates keep splitting before r300 (646840: split[673 L6 k4] at r270, split[544 L7 k5] at r273). The feeder mechanics are the same as theirs; the timing is not.",
   "general": true,
   "impact": "Largest single factor. It decides Portals and Trauma and is part of Slithery and Autarky. Our r500 king share is 0.31 even against other strong teams (theirs 0.47), so this is a general conversion gap. Proposed EARLY_KING flag: seed at 200-230 and feed from 240-250 on maps that usually reach r500, with no king self-splits except U-turns. Needs a server A/B, since self-play can't measure king races."
  },
  {
   "what": "Swarm drawdown after about r300. They cut their unit count while total length keeps rising, and merge secondary big dragons into the king.",
   "evidence": "Round-limit units go 45.8 (r200), 39 (r300), 25.7 (r400), 17.5 (r500) while total length rises from 132 to 157. Small dragons (L3 or less): 14 at r350, 5.9 at r400, 3.0 at r450. Merges of L10+ dragons into the king: 0.44 per game with 0.38 of the pearls eaten by the king (ours: 0.23 and 0.24). k=2 splits in r401-500: 8 vs our 30. Final unit count 10.6 vs 25.3 with equal total length.",
   "we_do": "We hold about 25-30 units until r450 (26.2 at r400, 23.8 at r450) with 8.8 small dragons still alive at r450. LATE_SPLIT_ROUND keeps small dragons splitting until r450, and FEED_RESERVE holds some back, so our mass stays in the swarm.",
   "general": true,
   "impact": "Large. It is the other half of the king-race gap: our king has less to eat. Proposed: after the feed start, every non-reserve dragon of L5 or less feeds; keep only 2 insurance dragons of L8+; no new k=2 splits after about r380."
  },
  {
   "what": "Hunting our big dragons with sprint rams. Their L4-8 dragons (median L5 before the sprint) close in over 5-10 rounds, from 11 tiles to 7 to 3, then hit an L10+ head with a 3-5 step sprint from 3-5 tiles away. They also ram our feeders late, using L4-5 dragons.",
   "evidence": "25 of our 51 L10+ deaths against Stockfish were these rams: 0.62 per game, against 0.28 per game from other strong teams, whose rams are mostly 1-3 steps. Sprint lengths used: 3 steps 9, 4 steps 7, 2 steps 4, 5 steps 3, 1 step 1. Our victims averaged L16, the largest L47 (642793 r437); in 642793 we lost six L10-47 dragons between r324 and r437. Late rams (r380+): 3.7 per game by them vs 1.7 by us; their rammers median L4-5, ours L3 or less.",
   "we_do": "computeThreats (main.cpp about line 2023) gives an enemy head a reach of its visible length minus 1, capped at 4 for kings. When the enemy's tail is out of view the floor is THREAT_TAIL_UNKNOWN=2, so a Stockfish L5 with its tail off-screen looks like reach 2 when it can sprint 4. KING_ESCAPE only reacts to adjacent threats. RAM_MAX_OWN_LEN=3 means our L4-5 dragons never ram.",
   "general": true,
   "impact": "Medium-large, and decisive in several Slithery and Schooltime games. Proposed: THREAT_TAIL_UNKNOWN=4 for L10+ dragons, keep 5+ tiles from enemy heads whose tail is unseen or raise an alarm on enemy_head sonar echoes, and allow L5-or-less non-king dragons to ram after the feed start."
  },
  {
   "what": "Mass retention at the unit cap. Near 64 units they do not split every dragon at L4; they let dragons grow to L5-9 and split them into k3+ children. Pump children (split from 0 free exits) survive better. They lose far less length to deaths while eating less.",
   "evidence": "Slithery r61-300, parent length at split: theirs L4 187, L5 81, L6 60, L7 23, L8+ 37 per game; ours L4 574, L5 52, L6+ 16. Children with k of 3 or more: 150 vs 18 per game. Splits 388 vs 643; deaths 389 vs 648; stillborn 127 vs 257. Pump children die within 5 rounds 44% of the time vs 56% for ours, and eat 2.9 vs 1.95 pearls. Total length at r150: 215 vs 154, even though we eat more (641 vs 465 in r61-150); our death length in r61-150 is 613 vs their 377. On Autarky they eat 77 pocket pearls in r151-300 vs our 34.",
   "we_do": "We almost always split L4 into 2+2, even at 56+ units, and pump splits leave stillborn children (see notes/22 and notes/23). SPLIT_VIABLE and PUMP_TIP2 were already tried and rejected.",
   "general": false,
   "impact": "Explains the Slithery economy gap (8/9 losses) and part of Schooltime and Autarky. It applies to any map with pockets or a unit cap. The new lever to try is CAP_SPLIT: at 56+ units, split only at L5+ with children of k3+."
  },
  {
   "what": "Evasive and positional sprints by small and mid-size dragons, used to escape or grab pearls, not just to ram.",
   "evidence": "Their L4-or-less dragons make 13.5 non-ram sprints per game, half moving away from or level with the nearest enemy head, plus 1.9 eating sprints. Their L5-9 dragons make about 7 sprints per game (away 1.9, eat 1.4, kill 1.8). Evasive sprints with an enemy head within 3 in r151-300: 3.5 per game vs our 0.1.",
   "we_do": "Our small dragons sprint only to ram (13.4 per game, all kills). Our L5-9 dragons sprint 0.4 times per game.",
   "general": true,
   "impact": "Medium-low; mostly keeps units alive. Proposed: allow 2-step escape sprints for L4+ non-kings when every 1-step move is threatened."
  },
  {
   "what": "King navigation with U-turn splits. Big dragons split off all but 2 segments (SPLIT L-2) to reverse direction, often with 2-3 free exits, to steer towards corpses or away from rammers. The king's ID changes each time.",
   "evidence": "L8+ U-turns per game: 4.2 before r300, 2.9 in r300-399, 5.1 after r400 (against us 6.6 after r400). Ours: 0.7 / 3.1 / 3.4, almost all with 0-1 free exits. Example: the Slithery king 1517 in 646839 was born at r353 from L47 with k45, then grew to L80.",
   "we_do": "We U-turn mainly when trapped (KING_ESCAPE / reverse split). KING_CONSENSUS king identity must cope with the ID changing.",
   "general": true,
   "impact": "Low-medium."
  },
  {
   "what": "Sonar mesh. Every dragon casts about 4 rays per turn with unencrypted payloads: the sender's head position, relays of other dragons' positions, and a field shared by many senders that looks like king state. All team dragons know where the king and the other dragons are.",
   "evidence": "34-37k pings per game vs our 4-5k. Payload fields: x = (v>>53)&63, y = (v>>46)&63 (for example 0x33c28e09... at (30,10)). Relay messages have a low word ending in 0x...00001. A field such as 0x5aa1.... is repeated by many senders.",
   "we_do": "We send king relays and portal warnings only, 4-5k per game.",
   "general": true,
   "impact": "Enables items 1-3. Opportunity: we can decode their beacons for free to learn their king's and dragons' positions, including through portals."
  },
  {
   "what": "Portal discipline: fewer crossings, fewer fatal crossings.",
   "evidence": "Crossings r151-300: 44 vs our 68; fatal crossings 3.5 vs 6.7.",
   "we_do": "Already analysed in notes/16 (warning memory, mouth clearing).",
   "general": true,
   "impact": "Low here (already known)."
  },
  {
   "what": "Not their edge: opening and per-head harvest. Stockfish is weak early on small, aggressive maps.",
   "evidence": "First split 3.7 vs our 3.0. At r60 they have fewer units and less length than us (15/36 vs 20/47). Spawn pearls eaten per head-round are equal on every map. We eliminated them on Devil 4/4 (between r39 and r216), Prisoners Dilemma 2/2, Default 2/2, Trophy 1/1 and Queen Of Spades 1/2. At r60 on Devil they have 1.5 units to our 14; on Prisoners Dilemma 1 to our 9.",
   "we_do": "Our opening is stronger. Keep the current Devil, Prisoners Dilemma and Default play.",
   "general": true,
   "impact": "None to chase. Don't touch the early game against them."
  }
 ]
}

---

{
 "track": "v31 regression check (Trophy/Devil and all maps). Verdict: not a regression. On Trophy and Devil the v31 binary makes the same decisions as v30 and v29 on every turn replayed. The dip is noise, helped by harder opponents and possibly a side-A effect on Trophy. Full report: /Users/devsingh/Developer/UNSW_Battlecode/notes/top3/regression/REPORT.txt",
 "games_used": "1,050 of our games from 2026-09-29T15:30Z to 2026-09-30T02:01Z: 604 fetched with a rate-limited script (notes/top3/regression/fetch_ledger.py → ledger.json), plus the replays/auto ledger. 417 replays are in replays/regcheck (185 newly downloaded, the rest symlinked). Every dragon's decisions were replayed through v29, v30, v31, v31 with KC=0 and v31 with EDF=0 on 98 v31-family games (all maps) and on all 38 Trophy/Devil games since v30 went live. sim2 profiles cover every Trophy/Devil game since 15:30 and Portals/Trauma/Slithery/Schooltime from v30 on.",
 "key_numbers": "Decision divergence, v31 vs v30 (lives per game): Trophy 0 (7 games), Devil 0 (8), Dilemma 0, Trauma 5, QoS 8, Default 10, Autarky 18, Portals 32, Schooltime 58, Slithery 88. Real moves match the v31 bot on 96.7-99.7% of turns. v30 vs v29 on Trophy/Devil: 0 divergent lives in 38 games (only 2 L3 moves in one win). EDF changed a decision in 19 lives across 98 games (L8-41, r244-497). In the 12 games checked with the KC=0 binary, every divergent life was a KC life.\nRanked records v29 / v30 / v31 (corrected version windows): ALL 171/295, 28/55, 32/60. Trophy 13/24, 4/4, 0/5. Devil 18/29, 2/8, 2/6. Portals 20/39, 3/7, 2/8. Slithery 10/29, 3/9, 3/5. Autarky 7/30, 1/2, 5/6.\nVs opponents rated 1990+: ALL 132/294 (.45), 34/80, 25/45 (.56). Devil 15/30, 3/7, 2/3. Trophy 13/19, 5/5, 0/3.\nMean ranked opponent Elo: v29 1990, v31 2017 (Trophy 1964 vs 2024).\nOpponent-matched expectation: Trophy 3.9 expected vs 1 won (P=.02); Devil 4.9 vs 3 (P=.11); both P=.005 before correcting for picking the worst maps after looking (Bonferroni ~.2).\nTrophy by side since 15:30: A 13/26, B 25/34 (vs 1990+: A 10/19, B 8/8). All 4 v31 ranked Trophy losses were as A.\nv31 Trophy/Devil losses: our longest dragon never above 4-6, eliminated r70-233 after the unit count flips at r40-100 (e.g. 651473 calc 17-17 r60, 18-22 r100; the v29 loss 629431 went 16-16, 18-27).\nVs opponents rated 1960+: Slithery 7/28 → 10/16, final longest 44.9 v 52.5 → 55.5 v 50.8. Portals 6/19 → 6/19, but late own-corpse feeding by L>=10 dragons after r300 fell 33.6 → 26.9 and final longest 30.0 v 35.8 → 28.4 v 37.9. Trauma 7/9 → 4/6: king races lost by r300-450, feeding unchanged (14.4 → 16.2).\nFingerprint: battles at 01:08-01:10 (649046-50, 649071-75) were still played by v30, so v31 counts from about 01:15.",
 "behaviours": [
  {
   "what": "KING_CONSENSUS cannot run on Trophy or Devil: all of its code is gated by RP.kingDeclare, which is 0 on those maps.",
   "evidence": "variants/v31/main.cpp:1758, 1841-1851, 1973 all require RP.kingDeclare. KING_DECLARE=0; PM_TROPHY_KD and PM_DEVIL_KD are -1; the KING_V2 v2() list covers only Schooltime, Slithery, Portals and QoS. Replaying decisions: 0 divergent lives in 7 Trophy and 8 Devil v31-family games.",
   "we_do": "v31 = v30 + KC + EDF. On Trophy/Devil this plays exactly like v30 and v29.",
   "general": true,
   "impact": "Rolling back v31 would change nothing on Trophy or Devil. Stop attributing the dip to v31."
  },
  {
   "what": "ESCAPE_DEADEND_FIX rarely fires and never on Trophy/Devil (big dragons only, L>=8).",
   "evidence": "edf_all.txt: 19 changed lives in 98 v31 games, all L8-41 at r244-497 (turns a 1-step move into a 2-3 step sprint or reverse split), on Slithery, Schooltime and Portals. No v31 Trophy/Devil loss had a dragon of length 6 or more.",
   "we_do": "tryKingEscape now skips unthreatened steps into dead ends (main.cpp:2969).",
   "general": true,
   "impact": "Negligible either way. Keep it."
  },
  {
   "what": "Trophy/Devil losses are the early swarm war: units level until r40-60, the opponent overtakes by r80-100, we are eliminated before r235 with no dragon above 4-6. The pattern is the same under v29.",
   "evidence": "early_trophy.txt: 651473 calc 17-17 r60, 18-22 r100 (v31) vs 629431 calc 16-16, 18-27 (v29). 651716 Sabotage-d 15-14 r60, 13-18 r100. 652120 calc 15-9 r60, 16-20 r80. Devil v31 losses 649982, 652117 and 652127 are like v29 629017 and 612864.",
   "we_do": "Same swarm policy on both maps since v29 (proven by the decision replays).",
   "general": false,
   "impact": "The Trophy/Devil weakness against calc, forgot to mention, Sabotage-d and Sponge is old. It needs an early-war study, not a v31 rollback."
  },
  {
   "what": "The opponent mix got harder, and the per-map samples are too small to show a regression.",
   "evidence": "Mean ranked opponent Elo 1990 (v29) vs 2017 (v31); Trophy opponents 1964 vs 2024. Vs 1990+ overall v31 25/45 (.56) vs v29 132/294 (.45); Devil vs 1990+ v29 15/30, v31 2/3. Opponent-matched expectation: Trophy+Devil P=.005 before correcting for choosing the worst maps after looking (Bonferroni about .2). Opponents' Elo histories show no clear jump.",
   "we_do": "n/a",
   "general": true,
   "impact": "Judge versions by strong-opponent and opponent-matched records, not raw per-map ranked counts of 5-7 games."
  },
  {
   "what": "Possible side-A weakness on Trophy.",
   "evidence": "Since 15:30: side A 13/26, side B 25/34; vs 1990+: A 10/19, B 8/8. All 4 v31 ranked Trophy losses were as A.",
   "we_do": "No side-specific Trophy handling; trophy.hpp is an empty module.",
   "general": false,
   "impact": "Weak evidence (p about .1). Worth checking mirror/frame and turn order on Trophy."
  },
  {
   "what": "On Portals, KC cut late feeding by about 20% with no change in win rate.",
   "evidence": "feedstat (vs 1960+): own-corpse eats by L>=10 dragons after r300 fell from 33.6 to 26.9 (them 38.7 to 41.8); final longest 30.0 v 35.8 → 28.4 v 37.9; W 6/19 in both versions. Every v31 Portals game diverges (32 lives per game, feeders L2-4 from r300). In 651472 and 647117 our longest stayed at 3-7 from r250 to r420.",
   "we_do": "KC: no feeding a king under 0.75x the longest heard in the last 40 rounds; a longer king heard in the last 30 rounds blocks crowning and forces step-downs (KC_FEED_MEM 40, KC_STEP_MEM 30).",
   "general": false,
   "impact": "Might be memory of a dead or split king stalling the king race. A Portals-only A/B with shorter KC_FEED_MEM/KC_STEP_MEM is cheap. Slithery clearly gained from KC (vs 1960+: 7/28 → 10/16, final longest 55.5 v 50.8)."
  },
  {
   "what": "Version tagging by battle 'at' time is wrong near a submit: the time is when the battle was requested, not when it was played.",
   "evidence": "The decision fingerprint shows battles 649046-50 and 649071-75 (01:08-01:10) matched the v30 binary on 22-59 of 25-63 divergent decisions. From 01:22 on, games match v31.",
   "we_do": "Journal and ledger analyses tag versions by submit time.",
   "general": true,
   "impact": "Use notes/top3/regression/mech.py as a fingerprint to tell which version played a game in A/B and regression analysis."
  }
 ]
}

---

{
 "track": "Cutlery (team 306). Report: /Users/devsingh/Developer/UNSW_Battlecode/notes/top3/Cutlery/REPORT.txt. Scripts and data are in the same directory: collect.py, agg.py, curves.py, onset.py, feed.py, kingsrc.py, scav.py, churn.py, lendist.py, early.py, zones.py, sprints.py, rams.py, metrics.pkl and agg_out.txt.",
 "games_used": "- 48 fresh Cutlery replays (29 Sep 23:29 to 30 Sep 01:56 UTC, GET only) in notes/top3/Cutlery/replays: 38 against elo >= 1900 (forgot to mention, free trip to sydney pls, glory to ra, Stockfish, Sabotage-d, bread first search) and 10 against 1700-1899 peers. All 10 maps are covered, 4-5 games each.\n- Our 15 ledger games vs Cutlery.\n- 80 of our ledger games vs elo >= 1950 since 29 Sep 15:00 (the 8 most recent per map).\n- 70 v30/v31 server A/B games vs the top-10 (ab_kc31, ab_pf31, ab_v30kc, ab_v30sch).",
 "key_numbers": "Head to head we are even with Cutlery (8/15). The Elo gap comes from other opponents on the big round-limit boards. Our record vs >= 1800 since 29 Sep 15:00: Schooltime 12/44, Slithery 15/51, Autarky 22/61, Portals 32/62. Cutlery in the last 2.5 h vs >= 1800: Schooltime 9/10, Autarky 6/8, Slithery 5/10, Portals 5/11. Cutlery is weak on Devil (0/5 in our sample) and Default (2/5).\n\nUnits/total/longest, all maps:\n- Cutlery vs strong: r50 14/36/3.7, r100 21/56/4.1, r200 29/81/4.7, r300 27/84/7.2, r400 14/68/18.4, r500 10/68/23.3.\n- Us vs >= 1950: 16/38/3.7, 24/57/3.9, 32/82/5.1, 32/90/8.0, 30/97/12.7, 22/98/18.9.\n\nKing maps, round-limit games (Cutlery vs us):\n- r300: 40/142/11.0 vs 35/109/13.2.\n- r350: 27/120/19.9 vs 30/108/17.6.\n- r400: 14/109/31.2 vs 30/117/22.8.\n- r500: 7/117/43.0 vs 16/124/34.5.\n- King eats per 25 rounds: 7.4/6.6/5.3 in r325-400 vs our flat ~3.\n- King eats r300-399: 21.1 vs 11.9. Own-corpse eats from feeders 3-6 tiles away: 17.7 vs 6.8.\n\nEats per 100 head-rounds by phase: Cutlery 10.3/8.6/8.1/10.7 vs us 11.9/8.5/7.8/9.5 (equal).\n\nDeaths:\n- Cutlery never dies by HitSelf or HitWall. All non-ram deaths are NoValidAction with 0 free neighbours (the pump or feed equivalent of our HitSelf), and 94% of those pearls are eaten by their own team.\n- Voluntary (free-neighbour) own deaths r100-320 on Slithery+Schooltime: Cutlery 3.9, us 44 (v28/v29), v31 51.7.\n\nRams per game, initiated/received: cut 22.3/16.9, us 20.8/16.4. In our games vs them: Cutlery 22.9 vs our 15.1. The corpse race is about even (64 vs 59). 3-step rams: 4.0/game vs 0.\n\nOther:\n- Portal crossings are the same (55-60 per phase mid-game).\n- Endgame: own heads within 6 of the king 0.57 vs 1.69; king deaths 0.34 vs 0.28.\n- Final king by map, Cutlery vs us: Autarky 45 vs 19, Portals 39 vs 31, Schooltime 46 vs 29, Slithery 54 vs 41.",
 "behaviours": [
  {
   "what": "Late, violent king rally: Cutlery does no king-feeding while the swarm grows until about r300-330. Then the unit count falls about 65% within 50 rounds (Portals 26->8, Schooltime 49->21, Slithery 55->19, Autarky 40->13, Trauma 33->12). Splitting effectively stops at r362-400. Feeders include L4-8 dragons (7.3 L>=4 deaths per game in r300-349 vs our 1.2-2.5). They die 3-6 tiles ahead on the king's path, and the king scavenges them. The top-5 dragons take 34% of own-corpse pearls in r300-399 (ours 16%).",
   "evidence": "onset.py: steepest unit drop starts at r294-346 on every king map; king gains +15-21 in the next 75 rounds (ours +7-14). kingsrc.py: king eats r300-399 21.1 vs 11.9, own-corpse from feeders 17.7 vs 6.8. scav.py: feeder distance peaks at 4-5, feeders approach +5.3 tiles over their last 6 rounds. curves.py (28 Cutlery vs 44 of our round-limit king-map games): longest r400 31.2 vs 22.8, r500 43.0 vs 34.5.",
   "we_do": "bot/main.cpp applyMapParams KING_V2 table: Slithery seed 170 / feed 250 / split stop 370; Schooltime 200/260/340; Portals 250/300/360. LATE_SPLIT_ROUND is 450 (params.hpp). So we feed early (r250-260 on the big boards) and keep splitting to r450-489. The v31 A/B games still drop units at r263 on Schooltime and r302 on Slithery, with 51.7 voluntary deaths per game in r100-320 against Cutlery's 3.9. Our feed-spot rule (KING_V2) makes feeders die 1-2 tiles from the king. notes/16's claim that top teams keep splitting to r450 is stale for current Cutlery.",
   "general": true,
   "impact": "Highest. It explains most of the +8 to +17 final-king gap on round-limit big boards (Slithery, Schooltime, Autarky, Portals), which are our worst maps. Suggested test: feedStart ~325, split stop ~370, LATE_SPLIT_ROUND ~370, L4-8 feeders allowed, feed 3-5 tiles ahead. Needs a server A/B, because self-play cannot show it."
  },
  {
   "what": "Tip splits with variable child size: at high unit counts and in dead ends or corridors, Cutlery grows a dragon to L5-9 and splits keeping 2 at the head, with child = min(L-2, 5). The L2 parent dies trapped at the tip and the child leaves with L3-5. This banks length in L4-9 dragons instead of L2s.",
   "evidence": "Split parent L and child k, r100-300. Slithery: L4->2 39%, L5->3 19%, L6->4 19%, L7-9->5 18% (us and v31: L4->2 69-71%, k>=3 about 2%). Schooltime: k=L-2 in about 30% of splits (us under 3%). Tip splits r60-320: 114 per game vs us 3, v31 22. Mean unit length on Slithery at r150/250: 3.1/3.6 vs 2.5/2.7. Schooltime: 3.4/3.6 vs 2.7/3.0. Total length on Slithery at r250-325: 225-230 vs 144-165. Early totals at r150: Slithery 194 vs 148, Schooltime 120 vs 77, Autarky 76 vs 56. k=2 splits 202 per game vs our 345-407, so they churn less.",
   "we_do": "Default split is always 4->2+2 (SPLIT_LEN 4, SPLIT_CHILD 2). POCKET_FACTORY in v30 ships PF_CHILD_MAX=2 (2-long children). PUMP_TIP_SPLIT is off.",
   "general": true,
   "impact": "High on crowded corridor maps near the 64-unit cap (Slithery, Schooltime, Autarky) and relevant to any unseen map with dead ends. Try PF_CHILD_MAX 5 (or 0) plus tip splits whenever units >= 56 or exits <= 1."
  },
  {
   "what": "Full sprint repertoire. Cutlery sprints to eat (8.3/game), to escape (5.5/game) and for other repositioning (10.4/game), as well as to kill (13.8/game). 26% of their sprints are 3 steps. They make 3-step rams (4.0/game) and L4-7 sprint rams (2.6/game; 3.2 vs us), and their kings sprint (3.6/game).",
   "evidence": "sprints.py and rams.py. Against us, 18.0 of their 22.9 rams per game hit a dragon that was already inside their 2-3 step reach before they moved. On QoS they rammed us 13.5 vs 2.5 per game and eliminated us at r179 and r225.",
   "we_do": "We only sprint to ram: 9.6 kill sprints per game, 0.6 other sprints, almost all 2-step L3. tryRam (main.cpp ~2620) only looks at distance 1-2 and requires myLen <= RAM_MAX_OWN_LEN 3 or theirs >= mine. MAX_THREAT_REACH is 1 for small dragons, so our L2-3s loiter inside sprint reach. EAT_SPRINT and SMALL_SPRINT_THREAT are off because self-play rejected them.",
   "general": true,
   "impact": "Medium. The ram count and corpse race are about even overall, so the value is mostly on small maps and QoS. Worth a server A/B of 3-step rams plus reach-2 for small dragons that are not locally ahead."
  },
  {
   "what": "Wider opening dispersion and harvest coverage. Cutlery's heads sit farther apart and visit more tiles. On Schooltime they farm the wrap strip (y30-39) across the full width and their home corner.",
   "evidence": "Nearest-own-head distance at r60: 4.8 vs 3.8. Share of map tiles visited r0-60: 0.278 vs 0.238. Distinct spawn tiles eaten r0-150: Schooltime 100 vs 60, Slithery 91 vs 81. zones.py on Schooltime: 82 wrap-strip spawn eats r0-150 vs our 19, and 50 home-corner eats vs 21. Schooltime spawn eats r0-150: 176 vs 96.",
   "we_do": "Our heads bunch into two mid columns on Schooltime (36 and 32 head-round units). The crowd penalty is per map (PM_*_CR). The SCH_B_KEEP flag, tested with an inconclusive result, targets the strip.",
   "general": false,
   "impact": "Medium. The dispersion part is general; the wrap strip is specific to Schooltime, our worst map at 27%."
  },
  {
   "what": "QoS: Cutlery takes the spade rooms and rams hard with local superiority.",
   "evidence": "Both QoS games vs us: 91-101 spawn eats in r61-200 (ours 2-29), units growing from 9.5 to 21 while we stayed at 6, rams 13.5 vs 2.5 per game (local odds 3.0/1.6), and we were eliminated at r179 and r225. Against the field on QoS: rams 14.6 initiated vs 3.8 received, 4/5 wins.",
   "we_do": "bot/maps/queen_of_spades.hpp gates room entry (QOS_GATE id%3) and uses one-way doors. RAM_MAX_OWN_LEN is 3.",
   "general": false,
   "impact": "Medium on QoS only."
  },
  {
   "what": "Endgame hygiene: after the rally Cutlery has few units, so the king is uncluttered (0.57 own heads within 6 vs our 1.69). They also keep second, third and fourth dragons of L15/10/8 at r400 as insurance.",
   "evidence": "agg.py end section. King deaths 0.34 vs 0.28 and enemy heads near the king 0.53 vs 0.60, both about equal.",
   "we_do": "We keep 27-30 units through r450 and crowd the king.",
   "general": true,
   "impact": "Low; mostly a by-product of the rally."
  },
  {
   "what": "Areas with no edge, or where they are worse: the opening (same r0 splits of 1.8, first later split r10-15, r50 units 14 vs 16), harvest per head-round (equal), portal crossings and portal deaths (equal), the ram corpse race (equal), Devil (0/5 in our sample, out-traded with local odds 5.2/5.4) and Default (2/5).",
   "evidence": "agg_out.txt: opening, eats, moves and rams sections, plus the per-map table.",
   "we_do": "We are at parity or better here. Our Devil, Default, Dilemma and Trauma play is stronger than theirs.",
   "general": true,
   "impact": "None. Do not copy their small-map play."
  }
 ]
}

---

The plan is in `/Users/devsingh/Developer/UNSW_Battlecode/notes/top3/PLAN.txt`. None of the changes it proposes have been tested yet; every item needs a server A/B against the top 10, because self-play and single-replay forensics have misled us before.

**1. v31 verdict: keep v31 and don't revert any flag.**
- **Trophy/Devil:** KING_CONSENSUS only runs on maps with king declaration, and it's off on Trophy and Devil. Replaying all 38 Trophy/Devil games since v30, v29, v30 and v31 make the same move every turn, so v31 can't be the cause of the dip there.
- **ESCAPE_DEADEND_FIX:** it changes a decision in only 19 lives across 98 games, all big dragons (L8+) after r244. Keep it.
- **Harder opponents:** average ranked opponent Elo went from 1990 to 2017. Against opponents rated 1990+, v31 wins 56% (25/45) and v29 won 45%. Adjusted for opponent strength, the Trophy/Devil dip is about P≈0.2 (noise) once you allow for picking the worst maps after looking.
- **Real Trophy/Devil weakness:** they're the same early swarm-war losses we had under v29, and they need their own study.
- **One cheap follow-up:** a Portals-only shorter consensus memory (`PM_POR_KCMEM`). On Portals, KC cut late feeding of the king by about 20% with no change in win rate.
- **Version tagging:** tag which version played a game with `notes/top3/regression/mech.py`, not by battle time. Games requested at 01:08–01:10 were still played by v30.

**2. What all three do that we don't.** They disagree on when to start a king: Stockfish seeds early, while cheji and Cutlery swarm until about r325. All three agree on what happens after about r330:
- splitting stops;
- units fall by about 65% within about 50 rounds;
- the mass goes into one or a few big dragons.

We still have 22–25 units at r450–500. Our king holds 0.31 of our total length at r500; theirs holds 0.45–0.47. That gap explains most of our losses on Slithery, Schooltime, Portals and Autarky.

Ranked by expected gain against effort:
- **A. Stop late small splits** (trivial, high confidence): new flag `LATE_SPLIT_KING_MAPS=340`, on king maps only. The belief that top teams split until r450 is false for all three. The Portals-only version (por32) went 5/10 against a 3/10 baseline.
- **B. Consolidation wave** (medium effort, the biggest lever): `WAVE_R=330`. Dragons up to L8 feed a visible, longer ally of ours within 3 tiles, keeping 4 in reserve, and the feed length cap is relaxed.
- **C. Earlier merge into one king** (trivial to low): `KING_V2_MERGE_ROUND` 420 to 380, then a separate step-down flag `KC_STEP_ONE`.
- **D. Cap split** (medium): at 56+ units, split only at L5+ and give children of 3 or more, including tip splits. Also try `PF_CHILD_MAX=5` on Autarky.
- **E.** `THREAT_TAIL_UNKNOWN_BIG=4` for dragons of L10+: guards against Stockfish's 3–5 step rams on our big dragons.
- **F.** A narrow corpse-pearl sprint (low to medium confidence; cheji and Cutlery disagree on whether it matters).
- **G.** An escape sprint (last).

Map-specific ideas cover Portals, Autarky, Schooltime and QoS. Leave Trauma alone.

**Test order:** start with A+C as parameter changes only on Slithery and Schooltime, then add B (plus Portals), then D, E and F. Beyond win/loss, check units at r400 (target 18 or fewer), king length at r475, and king share at r450 (target 0.40 or more).

**3. Don't copy:**
- their death style (no-action deaths; the pearls land the same way);
- their openings (we're at least as strong early);
- cheji's habit of keeping a top three too long;
- Stockfish's early king on every map (per-map only);
- Stockfish's sonar mesh;
- a global increase to `RAM_MAX_OWN_LEN` or a global `EAT_SPRINT`;
- any change to Trauma, Devil, Default or Dilemma.