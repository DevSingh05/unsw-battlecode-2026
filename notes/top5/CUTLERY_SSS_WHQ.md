# Cutlery (#3), SSS (#4), WeHaveQuizzes (#5) under the new rules (games 2026-10-02 04:58-07:06 UTC)
Data: 20 replays, 15 maps. Battles: WHQ v Cutlery 859659-63, WHQ v SSS 859326-30, v40 v WHQ 860365-69, v38m v Cutlery 857158/60, v38m v SSS 857165/66, Sponge v Cutlery 860449. Team-games: WHQ 15, Cutlery 8, SSS 7, v40 5.
Files: scratchpad top5b/{an.py,agg.py,ex.py,qc.py}, rows.pkl (sim2). "Free" = steps <= ceil(L/4). Side mapping is by API winner; a draw would be ambiguous (none occurred).
## Outcomes and queens
- WHQ 8-7 (elim 4/6, r500 4/9), Cutlery 3-5, SSS 3-4. v40 3-2 vs WHQ.
- Every r500 game with a living queen went to that team (6/6), even v40 weakhold: our longest 5 / total 16 beat their 32 / 75 on queen L3 vs dead.
- **WHQ ignores the queen.** It splits her at r0 (L5 -> 2) and she dies in 14/15 games, median r60 (r21-172): 8 to enemy head-ons, 5 HitWall (fed). Their 4 r500 wins all came when the enemy queen was dead too.
- **Cutlery grows the queen as king.** No split before r250 in 6/8 games, and she stays L4-5 early. She is the team's longest at r500 in 2/8 (Trauma L42, Australia L92). 76% of queen eats are own corpses (199/263) vs 43% for the team.
- Cutlery's flaw: once the queen is the king (L23-56) it hands the body to a split child, keeping 2-3 (r251 30->3+27, r365 56->3+53, r353 23->7+16). The queen remnant then suicides by NoValidAction (r392, r411, r417). That cost weakhold (both queens dead, lost 9 vs 32) and Portals.
- **SSS:** the queen churns 4->2+2 early (5-8 splits) and roams (mean 17-19 from spawn). In Islands 859329 she stayed L2-3 until r325, then ate 49 own corpses: L2 -> 55 by r475, king, won. Dead in 4/7 games (3 to enemy head-ons, 1 at r0 on Schooltime).
- **v40:** the queen lived 2/5. Both v40 losses (Around UNSW, Maze) were r500 games where her early death cost the queen tiebreak (WHQ's queen also died, at r143 / r140). She splits 4->2+2 into dead ends (Maze splits at r19/r22 with 1 and 0 free exits) and then dies HitSelf at L2 (r7 boxed by ally + 2 kelp; r23 in a 3-kelp dead end). Fix: forbid a queen split when free exits <= 1, or when it leaves her L2 next to kelp or ally body.
## Movement and fighting (per game)
- Share of L5-8 / L9+ turns using 2+ steps: SSS 74/77%, WHQ 65/60%, Cutlery 50/57%, **v40 0.2/0.3%**. About 2/3 of their multi-steps use exactly ceil(L/4). Under 1/20 are paid.
- Paid steps are lunges by L3-4. WHQ: 28/game, 53% eat a pearl, 73% kill. Cutlery 43/game (44% eat, 48% kill). SSS 78/game. v40: 15/game, 97% kills, never paid for food.
- Head-on kills per game: SSS 49, v40 39, WHQ 33, Cutlery 29. Sprint (2+ step) kills: about 21/game for all three vs v40 14.
- Enemy queen killed: WHQ 6/15, SSS 4/7, Cutlery 2/8, v40 2/5. These look like ordinary swarm head-ons on L2-3 queens, not hunting.
- Portal crossings on Sprint maps (mostly L2 units): Australia Cutlery 201 (34 by r100), WHQ 54-76, **v40 2**. Around UNSW WHQ 26-54, SSS 37, v40 4. Maze WHQ 345, v40 13. Islands SSS 188-223, WHQ 90, v38m 5. v40 does cross on Trauma (248), so the gap is in unseen/route portals.
## Growth and endgame
- WHQ outgrows early: total at r100 vs Cutlery 41/59/99/71/52 vs 17/56/96/13/3. vs v40: ahead on 4/5 maps (weakhold 48 vs 21, Around 230 vs 92, Maze 116 vs 80).
- Cutlery's early economy is weak now: units at r50 were 2-9 in 6/8 games, and it lost 3/4 elimination games (Devil x2, Dilemma), each finishing with 1-4 units.
- WHQ consolidates late. Units r300 -> r400 go 25->6, 18->5, 27->11, 15->5, while longest r300 -> end goes 8->32, 24->50, 30->59, 15->85. Feed deaths are mostly HitWall (86/game).
- SSS stays at the unit cap (59-63 at r300-400) and still ends with longest 57-84. Feeding is HitSelf (81/game); 17% of late deaths are within 3 tiles of the king.
## Most distinctive, transferable behaviours
- **Cutlery:**  1. Never split the queen early; she is the king seed (L4-5 to r150, then L40-92).  2. Feed the queen own corpses (76% of her eats).  3. Sprint rams and paid eat-lunges by L3-4.  Weakness: late king hand-off by tail-split, then queen suicide. Beat it by keeping ours alive.
- **SSS:**  1. Free ceil(L/4) steps on 3/4 of L5+ turns.  2. Stay at 62-64 units to the end, with the most head-on kills (49/game).  3. Late queen coronation: a tiny L2-3 queen is fed to king size from r325.
- **WHQ:**  1. Strong early mass (ahead on total length at r100 in 13/15).  2. Late consolidation: units fall about 4x after r300 as the king doubles.  3. Lunges that pay for a step to eat or kill (73% kill rate).  Weakness: dead queen in 14/15; any surviving queen beats them at r500.
## For v40 (largest gaps, all map-independent)
- (a) Queen survival on unseen maps: no queen split with <= 1 exit or into kelp or ally pockets (2 lost games here).  (b) Free ceil(L/4) multi-steps for L5+ (0.2% vs 50-77%).  (c) Portal crossing by small foragers (2-13 vs 26-345 per game).  (d) A late queen coronation (SSS/Cutlery style) only if (a) holds.
