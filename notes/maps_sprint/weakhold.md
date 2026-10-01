# weakhold (Sprint map), 40x15, SYMMETRY xy (180-degree rotation), studied 2026-10-01
Sources: maps/sprint/weakhold.map (has kelp and dragons, but no pearl gaps: every TILE line is 0 0, the same on all maps/sprint files) plus 20 Sprint replays in scratchpad/maps/weakhold/ (6 ours + 14 from top-16 rounds 6-9). Spawn tiles and rates come from replay tileChange events. Scripts: scratchpad/wh_*.py.
```
:,a,,,,,,,,PPoppp,ppp:,:oPP:,,,,,,,,,b,:   0/1 = queens (ids 0/1) under the new rules, 2/3 = other heads, a/b = bodies
,.a.....,,::,:ppp.ppp,..,,,::,.......b.,   P = fast spawn (gap ~4-10, 9-43 spawns/game)
,.a....:#::::::,,,,,,:.....,::#:,....b.,   p = slow pad (gap ~55-70, ~6 spawns/game per tile)
,.0..,::,::,:,::::::.:.....,:::##:,..3.,   o = pearl at r1 only (centre field, ~35 tiles), rare respawn
,...,#::#,::::::::::::...oo,:,::,:#,...,   tiles: . 4 exits  , 3  : 2  # dead-end (28 on the map)
,...,::oP#:::::#:,:,,....oo.::#Po::,...,   border is solid kelp (no wrap), 0 portals
,....,::P:::,,,.,...oooo..o.,,:,::,....,
,.....:,:::,.o..oooooooo..o.,:::,:.....,
,....,::,:,,.o..oooo...,.,,,:::P::,....,
,...,::oP#::.oo....,,:,:#:::::#Po::,...,
,...,#:,::,:,oo...::::::::::::,#::#,...,
,.2..,:##:::,.....:.::::::,:,::,::,..1.,
,.a....,:#::,.....:,,,,,,::::::#:....b.,
,.a.......,::,,,..,ppp.ppp:,::,,.....b.,
:,a,,,,,,,,,:PPo:,:ppp,pppoPP,,,,,,,,b,:
```
1. Structure. Each team has 2 L4 dragons in an open home bay (x 0-5 / 34-39, about 90 tiles) that has **zero pearl spawns**. A: id0 head (2,3) facing S, id2 head (2,11) facing N. B: id1 (37,11) N, id3 (37,3) S. The queens are 73 BFS steps apart. Next comes a kelp-maze band (x 5-12 / 27-34) full of 2-exit tiles and dead-end pockets. Each side's fast food sits in it: (11,0),(12,0),(13,14),(14,14),(8,5),(8,6),(8,9) for A, at 12-24 steps from the A spawns and 57-84 from B's (about 185 spawns/game per side). The open top/bottom lanes (rows 0-2, 12-14) run from the bay to two slow 6-tile pads, but a kelp wall cuts each lane at x 21-24. Top pad: 34-41 steps from A, 43-48 from B (the bottom pad mirrors this). The centre room (x 12-27, y 3-11) holds about 35 pearls at r1 and is then almost dry.
2. Design intent ("weak hold"): holding home earns nothing. The map tests (a) pathing and pocket-farming in narrow kelp without suiciding (top teams log 100-250 HitWall/NoValidAction deaths per game here; PPP in particular), (b) the r1 grab of the centre field, and (c) the late consolidation race. There are no portals and no wrap. Long 73-step routes mean early contact is rare.
3. Games (20). Five ended by elimination: our r1-3 games (r216-264), cheji-SKKU r270, 中国-UnderTheC r270, larpmaxxing r498. The other 15 went to r500, and in all of them max length stayed at 3-9 until ~r300 (swarm farming). Kings were then built r300-500 by mass suicide-feeding, ending at 24-46. **Total mass decided it:** the total-length leader at r200 won 13/14 r500 games (14/14 at r450). Examples: cheji 46 units/106 total at r300 -> 46-long king vs Cutlery's 7; calc 43/108 -> 31 vs 3; zitian 33 units at r300 vs SSS 3 -> 20 vs 2; Cutlery-PPP final 15 vs 24 (PPP mass 43 vs 46 at r300, then fed better). No side advantage (B 18 / A 13 wins in rounds 5-9).
   Per game: units/max at r50,100,200,300,400 -> final max (more in scratchpad/wh_an.py output):
   - 806953 PPP v us (W 23-43): us 6/5, 19/5, 34/5, 31/8, 12/25 vs PPP 7/3, 9/3, 11/3, 7/9, 9/13. PPP walled itself 120x.
   - 806883 us v free trip (L 22-28): us 5/5, 11/5, 16/3, 18/6, 12/18 vs them 5/3, 14/3, 20/3, 16/4, 16/7.
   - 807002 Cutlery v cheji (B 46-7): cheji 9/6, 21/3, 38/4, 46/5, 6/23; Cutlery fell to 3 units by r400.
   - 806736 us v Quaker (W 16-3 at r500); our r1-3 games: 29-38 units vs 0 by r216-264 (opponents never left the bay).
4. Our bot (v35 sees weakhold as an unknown map, so UNK_KING runs). Record 5/6. The one loss (806883) was a conversion failure: we led mass 47-41 at r300 and max 18-7 at r400, then our king stalled at 19-22 from r380 to r499 while theirs grew 7->28 (r400->r499). Causes: (a) UNK_KING crowns at r250 and feeds from r300 (params.hpp:605/608 UNK_KING_SEED 250 / UNK_KING_FEED 300). feedReserveNow (main.cpp:2086-2091) shrinks the reserve 14->3, so our foragers drained from r300 on (units 18 -> 5 by r475) and the fast pockets went unfarmed for 150 rounds. (b) From r440 the king sat in the barren home bay (x 2-7), which has no natural pearls; it ate only corpses (13 eats at L>=12 after r350). (c) Our L6 and L8 mid dragons died head-on in the centre at (24,5)/(24,7) at r449/453. Their king roamed the centre and our side ((16,6)->(13,6)) and ate 20 times at L>=12. Fix direction: start feeding later on this map (r420+, like the winners) and keep the king grazing the P pockets/pads, not the bay.
5. New rules (queens id0/id1). The queen spawn is **safe from enemies**: she starts in the far bay, 73 steps from the enemy queen, and every enemy fast spawn is 57+ steps away, so enemies rarely enter the bay before the midgame. The real risks are our own swarm (ally H2H/body, self-coil) and the kelp pockets (2-exit/dead-end tiles, HitWall). A queen plan here should:
   (1) not split her below L4; keep her in the open bay rows 3-11 (deg-4 tiles), or graze only (11,0)/(12,0) and (8,5)/(8,6), which are 12-24 steps away and on our side;
   (2) post 1-2 guards at the bay mouths: the lanes (rows 0-3 and 11-14 at x 5-7) plus the x6->7 crossings at rows 4, 6, 8, 10;
   (3) feed her from ~r420 inside the bay. Our foragers' death-drops there are uncontested because the bay spawns nothing.
   Hunting the enemy queen is a 70+ step trip. For A, B's queen id1 sits bottom-right at (37,11). Our bottom lane is cut at x 21-24, so the route goes through the centre room and then B's bottom lane. Send L2-3 rammers only once the swarm is big; with free moves (ceil(L/4)), an L5+ escort can cover the lanes at 2 tiles/turn.
