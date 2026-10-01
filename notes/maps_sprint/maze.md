# Maze (Sprint map) — 48x24, SYMMETRY xy (180° rotation)
Data: maps/sprint/maze.map (the map file has no pearl gaps, so spawns come from replay events) and 10 Sprint replays (6 top-16 games plus 4 of our 6 Maze games; 804674 and 805850 are early-round wins not fetched). Scripts are in scratchpad/maps/*.py.
```
...........*########-#-**##########--:::::::::::   cols 0-10 = A room, 37-47 = B room (open 11x24)
....D......*###--#############--pppp#:::::::::::   cols 11-36 = maze (624 tiles: 452 deg-2 corridors, 24 dead-end tips)
...........|###-*########-###pppppppp:::::::::::   Q = queen (id0 A, id1 B), D = 2nd dragon; all L4 facing inward
...........############-#####ppppppp*:::::::::::   ':' = room half that spawns pearls (A bottom, B top); '.' never spawns
...........#####p*p##########pppp###*::::::Q::::   * = 16 hot tiles, all in dead-end pockets (gap ~4-15, ~40 spawns/game each)
...........|######p-###########-#####...........   '-' = other pocket tiles (68 in total); p = 88 tiles reachable ONLY via portals
...........#####-###########-p#######...........   (1 char = 1 col x 2 rows; whole border is kelp, nothing wraps)
::::Q::::::*###pppp##########p*p#####...........
:::::::::::*ppppppp#####-############...........
```
**Structure.** Each team has an open home room. The rooms connect to the maze only through 5 gaps each: A's at y=7,8,9,12,14 and B's at y=9,11,14,15,16. There are 16 portal pairs, all inside the maze. Walking from room to room takes 48 steps without portals and 25 with them. The p-blocks beside each queen room can only be entered through portals whose partners are on the enemy side. Pearl spawns per game (Cutlery-PPP): about 330 in each room (199 tiles, slow, median gap ~110); maze hot tiles 507 (median 10); other maze tiles 442 (median 27). So about 60% of the pearl supply is in the maze, and a third of it sits on the 16 pocket tips. Each team has 4 hot tips 2-9 steps from its own room: (11,1),(11,2),(11,15),(11,16) for A and the mirrored (36,7),(36,8),(36,21),(36,22) for B. The contested centre tips are at (23/24,1) and (23/24,22).
**Design intent.** The map tests pocket pumping and portal routing more than combat. The open rooms are a safe but slow farm. The real income sits on dead-end tips down 1-wide corridors and behind portals, and a dead end is a trap for anything long.
**Games** (all 10 ended at r500, no eliminations; max length / units for winner vs loser):
- 807012 Cutlery>PPP 82-57: Cutlery max 10/28/82 at r300/400/500 vs PPP 21/47/57. Cutlery had 36 heads in the maze at r300.
- 806998 Cutlery>cheji 63-53: Cutlery ate 1338 pearls in the maze vs 590.
- 806970 Cutlery>calc 74-45: calc led on units until r400 (n47 vs 34) and lost the king race.
- 807005 PPP>larp 54-43: PPP had 25 at r300, ate 1437 in the maze vs 304, and made 554 portal moves vs 10.
- 806984 PPP>forgot 79-44: PPP had 32 at r300 vs 4.
- 806989 larp>中国 47-47: longest tied, larp won the tiebreak on total length (296 vs 56, 48 units).
- Ours, 806949 PPP>us 71-62: our king started at r310 (PPP's at about r250). Two escape reverse-splits, r348 and r355, cost 4 length. 18 portal moves vs 401.
- Ours, 806438 dslafkj>us 48-22: our king reached 27 by r400, then made 9 KING_ESCAPE reverse-splits (r424-482) while L2-4 heads chased it through maze corridors, and lost about 18 length. At r200 32 of our 34 heads were still in our room.
- Ours, wins 806732 (78-34) and 806879 (44-40).
- Units at r50/100/200 were about 15/30/50 for everyone, with max length 3-5 until consolidation. Consolidation started around r250 for PPP/Cutlery and around r300+ for us.

**What decided games:** (1) maze income: winners ate 1000-1400 pearls in the maze vs 400-800 for losers, with 550-770 eaten on pocket tiles vs our 250-408. (2) Portal use: top teams made 150-550 portal moves per game, we made 8-37. (3) Crowning early enough (r250-300) and keeping the king out of dead-end corridors.

**v35 (we went 4-2 on Maze).** We stayed in our room, ignored portals and crowned late.
- Unknown-map portals: main.cpp:575-583 sets `nxt=-1` ("a portal whose far side we don't know yet") because LEARN_PORTALS=0 (params.hpp:393). The planner treats every portal as kelp. It never routes through one, so the 88 portal-only tiles and the 25-step routes are invisible to it. KING_PORTAL_PENALTY is 100 (main.cpp:4061).
- tryKingEscape (main.cpp:3336-3446) ends with `SPLIT myLen-2`. In 1-wide corridors every step is "threatened", so the king chain-splits. Each split costs 2 length and CROWN_INHERIT (main.cpp:1929) re-crowns the child.
- UNK_KING_FEED/UNK_KING_SEED is 300/250 (params.hpp:605-608), so the king grows about 50 rounds after PPP's.

**New rules (queen = id 0/1).** Queen A starts at (4,15) and queen B at (43,8). Each starts inside its own pearl half of its room, 8-10 steps from the nearest gap and at least 25 steps from enemy territory, so it is safe early. But the room is open and nothing blocks a late swarm once it comes through the 5 gaps. A queen strategy here needs:
- Farm the room plus the 4 adjacent hot tips (11,15)/(11,16) (2 steps from gap y=14) with small pumpers that feed the queen. Never send the queen into the maze, where a dead end means certain death or a reverse-split.
- Disable the reverse-split escape for the queen: SPLIT k=L-2 leaves the queen's id on the 2-long head.
- Guard gaps y=12/14 (A) or 9/11 (B) with blockers.
- Teach portal routing (LEARN_PORTALS, or learn partners via symmetry) so foragers reach the maze tips 25 steps away instead of 48.
- The queen acts first each round (id 0/1), so every enemy head can react to its move. Keep a 2+ tile margin beyond the reach of enemy heads (length L-1).
