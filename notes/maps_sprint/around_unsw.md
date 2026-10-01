# Around UNSW (Sprint map), study 2026-10-01
Sources: maps/sprint/around_unsw.map plus the map embedded in replays. Neither file has pearl gaps (every TILE line is 0 0), so spawn tiles were inferred from round-start tileChange events across 11 replays.
Scripts and replays are in the session scratchpad maps/ (au_struct.py, au_games.py, au_*.replay).

## Structure
- 64x64 torus with SYMMETRY xy (180deg rotation) and 858 kelp edges. The kelp is street and campus-block outlines that fill a diagonal band: the NE quadrant (x28-63, y0-35) and the SW quadrant (x0-35, y24-63). The NW and SE quadrants are empty open water with no kelp and no pearls. Every tile is reachable.
- Portals: 4 pairs. id0 links (34,3)N and (8,29)N. id1 links (55,35)N and (29,61)N. id2 links (40,0)W and (2,37)W. id3 links (62,26)W and (24,63)W. Each pair joins a point in the NE band to one in the SW band, so they are shortcuts between the two halves.
- Pearls: about 286 spawn tiles in roughly 21 clusters. The big ones are the centre (x28-35, y24-39, 44 tiles) and two mirrored edge clusters, (0-9, 36-46) and (54-63, 17-27), with 42 tiles each. About 2030 natural spawns per game, roughly one per tile every 70 rounds, so the map is sparse.
- Dragons: 10 per team. Team B: ids 0, 2 and 14 (len 4), 4/6/8/10 (len 2), 12 (len 3), the raider 16 (len 3 at (44,35), inside A's half) and the big one 18 (len 10, an L shape at (30,41)). Team A mirrors this: ids 1, 3, 5... with the raider 17 (len 3 at (19,28)) and big 19 (len 10 at (33,22)).
- Queen (new rules): id0 is B at (20,42) and id1 is A at (43,21), both len 4 inside their own spawn cluster in a semi-walled campus block. There are 25 kelp edges in the 9x9 around each queen. A 12-tile pearl cluster sits 2 steps from B's queen. BFS distance is 35 to the nearest enemy start (the planted raider), 49 to the enemy len-10 and 62 queen to queen.
```
 sketch, 1 char = 2x4 tiles. # dense kelp, + some kelp, * pearl cluster, O portal, A/B starts, Q queen, K len-10
 0 ............+....O+#O+++........      32 .#+*#..#+....++***+#**B++#.O#+#.
 4 ...............#+:**::.##***++..      36 .O*#..B.++.....*#####**#+.++....
 8 ...............#+##+#++#++++##+.      40 #***#.B.B.Q#..+K.#+...+++++.....
12 ...............#.#+.#+.+*##..+#.      44 *:**#+#BB#**..#.##+.............
16 +............+##.#..**+AA.#+**+*      48 .+#.+##*+.+++.#.#+..............
20 ......+......+#+K#..#Q.A.A.+***#      52 .###:+:+#++#+##+++..............
24 .....#.+#**+####*+...+++.A..+*+O      56 ...#***##.::**:++...............
28 .#++O.##.A**#+***+......++..*:#.      60 ........+#++O#O+................
```
## Design intent
It is a big, sparse city-grid map. The tests are long-range foraging along street corridors, a contested pearl-rich centre, two dead empty quadrants that waste wanderers, portals as cross-half shortcuts, and seeded raiders (len 3 inside the enemy half) that threaten the enemy spawn early. Spawns are 49+ steps apart, so there is no early rush.

## Games (11 replays: ours R5/R6, all QF/SF/F, R6 Cutlery-ddabap and Stockfish-larp)
- 11/11 went to r500 with no eliminations, and the longer longest dragon won all 11. Both teams reach the 64-unit cap by r100 and kings stay at 4-13 until r300. Then they consolidate: king 25-51 at r400 and 42-84 at r500.
- Totals don't decide. Cutlery beat PPP in the final with 49 vs 45, even though PPP had the bigger total (326 vs 147) and four dragons of 32+. ddabap beat Cutlery 56 vs 54 with 6 units against 19. cheji beat zitian 84 vs 50 with 7 units.
- Winners pour the whole team into one king from r300. Cutlery's NoValidAction suicides (250-390/game) and larpmaxxing/ours' HitSelf suicides are feeding. PPP's king was ahead at every checkpoint against us (13 vs 8 at r200, 27 vs 13 at r300, 51 vs 27 at r400).
- Portals and ramming barely matter. Kings end up near the centre cluster (x26-36, y24-40) or the edge clusters.
- Old-rule queens (ids 0/1) died in every game, at r27-275 (median about r130): H2H in 13, HitWall/self/NoValid in 9.
## Our bot (v35)
- We beat 4 lower teams and "free trip" (49 vs 23), then lost to PPP 35 vs 62 (game 806952). v35 had never seen this map, so it ran the unseen path in main.cpp:838-856: UNK_KING_SEED 250 and UNK_KING_FEED 300 (params.hpp:605/608). feedReserveNow() at main.cpp:2088 also keeps a 14-segment reserve at r300 that only falls to 3 by r490. So we crowned and fed about 50+ rounds after PPP.
- Feed was split across 2 kings: 35 + 31 at r499, against PPP's 62 + 17. One king would have scored about 60+.
- Early expansion is slow on this big board: 36-37 units at r50 against 49-55 for PPP, Cutlery and cheji. The unseen-map explore lure/BFS probably wastes moves in the empty quadrants. Unverified.
## New rules (queens)
- The spawn is safe early: the queen starts deep in its own campus block with food next to it, 35+ BFS from any enemy, and the only fast threat is the enemy's planted len-3 raider. The risk is mid-game swarm traffic through the pearl clusters (that is how all 11 Sprint queens died) and the cluster next to the spawn, which draws enemy foragers.
- What a queen plan needs here: no splitting and no fighting. Move the queen into the empty open quadrant away from the raider's cluster. For B that is SE (x36-63, y40-63), about 20 steps east of (20,42); for A it is the mirror, NW. That quadrant has no kelp, no pearls and no traffic. Avoid the quadrant on the other side, where the enemy raider and its (18-23,26-30) cluster sit. Feed her corpses or pearls late and use v36q threat avoidance. With an r500 queen-length tiebreak and a 500-round grind with no eliminations on this map, a queen fed from r300 like a king should decide the game.
