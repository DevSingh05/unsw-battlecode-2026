# Tower Defense (Sprint), 32x16, SYMMETRY xy (180 deg rot), 292 kelp edges, 0 portals. 13 Sprint replays (6 ours, 7 top-16 R6-R9). Scripts+replays: scratchpad/maps/td_*.py, td_*.replay
Map file has no TILE gaps; pearl data below comes from replay spawn events (lower bounds). 149 spawn tiles: mid 83 (~0.66 spawns/rd), each home ring 24 (~0.06/rd, gaps 50-140), corridors 18 (gap ~25).
Q=queen head (id0 A @5,4; id1 B @26,11), k=dragon id2/id3, all L2. D=only door of home room. o=pearl tile, x=dead end, '='=1-wide corridor, '.'=open.
```
   01234567890123456789012345678901
 0 ooooxx.===x....................=      Home "tower" A = 7x7 room x2-8,y2-8: pearl ring on its walls, empty 5x5 interior.
 1 o=D======.=..oooooo.............      Single door (2,2)<-(2,1). B's mirror: room x23-29,y7-13, door (29,13)->(29,14).
 2 o=ooooooo==..oooooo..=.===......      Mid field x13-18,y1-14 = 55% of all pearl tiles, the only real economy.
 3 o=o.....o=...oooooo..===x==.....      Route home->mid is 41 steps (out the door, down col 1, along row 14, up col 11).
 4 ==o..Q..o==..oooooo..ox==.x=....      Queen->enemy queen 72 steps. 12 dead ends; (9,11)-(10,11) and (21,4)-(22,4) are
 5 ==o.....o==..oooooo..======.....      2-tile pearl pockets (fast refill) = death traps for L2 (23 HitWall deaths there).
 7 ==o..k..o==..oooooo..==ooooooo..
 8 ..ooooooo==..oo.ooo..==o..k..o==
11 ....=x.==xo..oooooo..==o..Q..o==
14 .............oooooo..=.======D=o
15 =....................x===.xxoooo
```
Intent: fortified home rooms with one door (defend/turtle) vs a large contested centre reached only by long 1-wide corridors; tests pathing in narrow kelp, traffic jams, pocket traps, and whether you can crack a turtle.
Games (Rn = bracket round; A/B units/longest):
- 804676 R1 us>Tattva elim r181 (r100 18/4 v 2/2). 805852 R2 us>Serendipity r500 30 v 6 (r100 26/4 v 2/2; enemy kept 2-4 L2-3 alive in homeB r250-500, we only won via a late king).
- 806440 R3 us>dslafkj elim r221. 806734 R4 us>Quaker elim r298. 806881 R5 us>free trip elim r284. 806951 R6 PPP<us elim r150 (r60 we had 7 in mid, PPP 0; PPP walled itself out).
- 807014 Final PPP>Cutlery elim r162 (r100 9/4 v 2/3; Cutlery stuck at home). 806972 calc>Cutlery elim r195 (r100 17/4 v 4/2). 806986 FTM>PPP elim r169. 806993 larp>CN elim r264. 807007 PPP>larp elim r164.
- 806916 Cutlery>ddabap and 807000 Cutlery>cheji: both r500. The loser turtled 3-7 small units in its home room. Cutlery swarmed (25-41 units at r200-300), then merged into a king (75 and 69 at r500).
What decided it: the race to the mid field. In every game the winner had units in mid by r60 and 9-26 units at r100, while the loser had 1-4. The winner's eats were 60-90% from mid. 11/13 games ended by elimination at r150-300. The loser either never left home or lost its L2s to walls/pockets (PPP 19-20 HitWall). Home rooms are slow food (~0.06/rd) and nobody won from them, but they let a loser survive to r500.
v35 here: 6/6 wins, but wasteful. 389 of our own deaths in 6 games were HitSelf (302 at L2). 194 of those were L2s boxed in by ally+kelp+kelp in 1-wide corridors (traffic jams in cols 1/11, row 14). 47 were pocket dives at (9,11)/(22,4) (pocket pump/factory, main.cpp ~2406-2790, pocketWorthPumping l.2476). There is no per-map crowd setting for TD (crowd() list l.91-101). We also could not crack Serendipity's 2-unit turtle in homeB for 250 rounds; the door is 1 tile and our L3 swarm never sieged it. Our eliminations came at r181-298 vs r150-195 for the top teams.
NEW RULES (queen = id0/1, longer queen wins r500, free moves ceil(L/4)):
- The spawn is the safest queen spot on any Sprint map. Q starts in the room's open 5x5 interior, 6 steps from a single 1-tile door, and the enemy is >=72 steps away. Old-rule data: our id0/1 survived to game end in 4/6 TD games, and Serendipity/cheji kept units alive in their home room for 250-400 rounds against 30-40-unit swarms.
- Queen plan: shed to L2-4 like v35, stay inside the room, and eat only the room's 24 ring tiles (enough to grow slowly with no traffic). Never take the door corridor or the (9,11)/(22,4) pockets. Free moves let an enemy L5+ reach 2 tiles per turn, so leave the room only if the door is breached and the enemy is near.
- Threat: the turtle is now a winning strategy for opponents too (alive queen beats queen-less swarm at r500). We need a siege: send L4+ units through the enemy door (29,14)/(2,1) after r150 to hunt the queen inside the room, not just clear corridors.
- Keep the army doing v35's mid rush; that alone decided Sprint. The risk is the queen's sibling (id2/3, also inside the room at (5,7)) jamming the door.
