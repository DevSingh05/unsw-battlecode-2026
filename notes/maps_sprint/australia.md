# Australia (Sprint, 64x64, SYMMETRY xy = 180° rotation). Our Sprint record here: 4-2 (lost R5 to free trip, R6 to PPP)
STRUCTURE: torus, mostly open water. 648 kelp edges draw two copies of the Australia coastline (SW quadrant, and NE rotated). One connected region without portals except two sealed 12-tile VAULTS ("Tasmania", (6-10,23-26) and (53-57,37-40)) reachable only by portal. 4 portal pairs, all vertical: P0 (41,14)<->(10,49), P1 (54,14)<->(23,49) = NE<->SW coast shortcuts; P2 (35,24)<->(57,40) = door to the E vault (15 steps from queen A); P3 (29,39)<->(7,23) = door to the W vault (15 steps from queen B). Each team's nearest vault sits on the *enemy* half, and its door is on your own half.
PEARLS (inferred from replay spawns, since the extracted .map has no gap data): ~314 spawn tiles, ~1100-1400 spawns/game. Mass is in the two continents (SW ~37%, NE ~34%, the open NW/SE water ~30%). The vaults are hot: 24 tiles with median gap ~22 (min 3), which is ~25% of all spawns when someone keeps them empty. Main-map gaps run from 2 to 450 and are long on average. Spawn mass is split exactly 50/50 by BFS distance to the two queens.
DRAGONS: 9 per team, total length 26 (L4 x3, L3 x2, L2 x4). Each team has a cluster in open water (A x20-32,y9-25; B mirrored) plus one lone L4 "colonist" placed in the far continent (id2 A at (24,51), id3 B at (39,12)), 22 steps from the enemy queen.
SKETCH (2x4 tiles per char; #/+ kelp, V vault, 0-3 portal, Q/q queen id0/id1, A/B others):
  .................#%###..##+.....     Top-right and bottom-left kelp blobs = the two "Australias".
  .............#####..+##.#+#+....     Open water: the NW/SE diagonals plus the centre.
  ..........++#+AA++.B..###.+##...
  .......###AAA.AA##.B0.#....1+##.
  +......#..QQQ.AAA#+######.....##
  #..3VV.##.......++......####+##%
  +.+VVV..%+.AA+###2##+...##%%%%##
  .+###%######+#+.....##%+###%%%%+
  +%%%%%##+%##.....+#+######%###+.
  ##%%%%##...+##3###+BB.+%..VVV+.+
  %##+####......++.......##.VV2..#
  ##.....######+#BBB.qqq..#......+
  .##+.0...#.1A.##BB.BBB###.......
  ...##+.###..A.++BB+#++..........
DESIGN INTENT: a big open harvest map with a long midgame. Food is scattered (no fights over a single hot spot), and there are two portal-only pearl pumps. It tests (a) whether you find and farm a sealed vault through an unknown portal, (b) unit growth / covering a 4096-tile map, (c) late consolidation into one king. Contact between queens is rare (40 steps apart).
GAMES (16 replays: our 6 plus 10 top-16; all but one ended at r500. Format: units/longest A-B at r100, r200, r300, r400, r500):
  us-PPP 806947 (PPP=A) L: 57/4-28/3, 63/11-55/4, 56/21-64/10, 62/29-36/27, 42/35-11/32. Eats 1791 vs 794, PPP vault eats 416, ours 0.
  us-freetrip 806877 (us=A) L: 29/4-33/4, 41/3-63/9, 50/9-62/14, 19/19-57/18, 18/45-7/51. Eats 699 vs 1216, their vault 160, ours 0.
  Wins vs weaker teams (Tattva by elimination at r469; Serendipity, dslafkj, Quaker): longest 55/41/55/35, vault eats 1-2 every game.
  Cutlery-ddabap W 47-10 (Cutlery vault 600); Cutlery-calc W 41-36 (vault 639 vs 2); cheji-Cutlery W 44-42; PPP-Cutlery (final) W 48-14; PPP-larp W 70-12; PPP-WeLik W 37-22; PPP-forgot W 55-15; larp-CN W 48-47.
  What decided it: (1) vault farming. All 10 top games had at least one side pumping a vault from about r15-30 (150-640 vault eats); the winner had more vault eats in 6 of 10. Losers with the vault lost on total harvest/king (CN, Cutlery x2) and hundreds of NoValidAction/HitWall deaths (deliberate pump-and-die inside the 12-tile room, recycling corpses). (2) Total harvest: winners ate 1.5-2.3x the loser. (3) A late king sprint. Units plateau at ~60-64 until r300-400, then mass feed/suicide pushes one dragon from ~20 to 45-70 in the last 100-150 rounds. Our two losses were close on longest (32 v 35, 45 v 51), so the gap was the harvest the vault would have given.
OUR BOT (variants/v35): we never entered a vault (0-2 vault eats in all 6 games). Cause: Australia is an unseen map, so portals are treated as kelp (LEARN_PORTALS=0, params.hpp:393). UNK_EXPLORE=1 only crosses when the dragon is "sealed in" or at hunger>=UNK_EXPLORE_HUNGER=100000 (main.cpp ~3120-3150, params.hpp:642). Our portal-free region is 99% of the board, so it never explores. UNK_SEALED_FOOD=0 (params.hpp:727), even though the vault pearls are visible over the kelp. Second issue: the king starts late (UNK_KING_SEED 250 / FEED 300). Our longest was 3-4 at r200 vs PPP's 11 and 9-10 at r300 vs 21, and we only caught up at r400+.
NEW RULES (queens = id0 A at (24,19), id1 B at (39,44), both L4): the start is SAFE. Open water, no kelp within 3, 61 tiles within 5 steps, 4 own L2-L3 escorts 5-7 steps away. Nearest enemy is the lone L4 colonist 22 steps away; the enemy queen is 40 away. But the queen's neighbourhood is food-poor (6 spawn tiles within 10 steps), so a queen strategy needs to: grow the queen early via escorts that feed corpses (r500 longest-queen decides, and top bots reach 35-70 by r500); NOT put the queen through the P2 door blind (the vault is a dead-end 12-tile room, where entering is fine but leaving means crossing the portal back into the unknown; send expendable L2-L4 pumpers and drop pearls to the queen outside or at the door); keep the queen off the long open diagonals late, when 60+ enemy units roam and small sprint-rammers are the main threat (free moves ceil(L/4) help a big queen flee in open water). Minimum queen-strategy needs on this map: unknown-portal crossing for small units (vault pump), and an early queen feed that starts by ~r150, not r250-300.
Files: replays aus_<gameid>.replay, aus_spawns.json, aus_cc.py, aus_games2.py and aus_games2.txt in scratchpad/maps/.
