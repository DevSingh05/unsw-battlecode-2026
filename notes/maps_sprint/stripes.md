# Stripes (Sprint map, 24x12), 2026-10-01
Sources: maps/sprint/stripes.map; 11 Sprint replays (ours R1-R6, plus top-16 games 806985/806992/806999/807006/807013), decoded with sim2. The pearl gaps are not in the extracted map file (every TILE is 0 0), so the food map below comes from natural spawns seen in replays 805851/806992/806999.

## 1. Structure
- 24x12, SYMMETRY xy (180-degree rotation), 154 kelp edges, 8 portal pairs. Four 3-row horizontal bands. Each band is a ring (x wraps, no kelp on the x border). Bands are separated by full kelp walls with 2 doors each:
  T(y0-2) | doors x1,22 + portal0 (x6->7) | M1(y3-5) | doors x3,20 + portals 4/5 (2-3,y4/5 <-> 20-21,y6/7) | M2(y6-8) | doors x1,22 + portal1 (x16->17) | Bot(y9-11) | wrap doors x10,13 back to T.
  Portals 2/3/6/7 are adjacent-edge pairs inside the outer bands (they only shift you sideways).
- Two sealed 2x2 boxes, (15-16,4-5) and (7-8,6-7). They hold early pearls nobody can reach. M2 narrows to one row (y8) at x7-8.
- Starting dragons: 2xL2 per team. id0=B (21,1) T band, facing W. id1=A (2,10) Bot band. id2=B (21,4) M1. id3=A (2,7) M2. Queens under the new rules are id0 and id1, one in each outer band; queen-to-queen BFS distance is 20.
- Food: almost all of it is in the outer bands. Hotspots (11-12,1) and (11-12,10) refill about every 10-13 rounds. Next come (7,1)/(16,10) and the corners near the queens. The middle bands only hold initial pearls. Natural spawns total about 150-180 per game, or 0.35 per round for both teams together. This is a starvation map.
```
  ##########-##-##########   wrap wall: doors x10,13 (next to the hotspots)
 0..oo....................
 1oo.....o...**......ooQq.   T: B queen id0
 2........................
  #-####################-#
 3........................
 4...............XX....Dd.   M1: B id2; X = sealed box
 5...............XX.......
  ###-################-###
 6.......XX...............
 7.dD....XX...............   M2: A id3
 8........................
  #-####################-#
 9........................
10.qQoo......**...o.....oo   Bot: A queen id1; * = hotspot
11....................oo..
```
## 2. Design intent
The map tests lane navigation (3-wide rings, 1-tile doors, portals that blind you) and contested food doors: each team's hotspot sits next to the wrap door its enemy enters by. It is also a swarm/attrition test. Food is too scarce to grow anything (the longest dragon ever seen was L6), so the game is decided by how many L2-3 heads each team has.

## 3. Games
Every sampled game ended by elimination (r28-r300). None reached r500.
| game | match | winner | end | r50 A n,max / B n,max | r100 | r200 |
|---|---|---|---|---|---|---|
| 804675 R1 | us(A) v Tattva | us | elim r239 | 2,2/2,3 | 3,3/3,2 | 7,3/1,2 |
| 805851 R2 | us(A) v Serendipity | them | elim r300 | 1,2/5,4 | 2,3/12,3 | 2,2/13,4 |
| 806439 R3 | us(A) v dslafkj | them | elim r77 | 1,2/11,3 | - | - |
| 806733 R4 | us(A) v Quaker Qubits | them | elim r118 | 2,3/7,3 | 1,3/15,3 | - |
| 806880 R5 | us(A) v free trip | us | elim r124 | 3,3/2,2 | 5,4/1,2 | - |
| 806950 R6 | PPP(A) v us(B) | us | elim r224 | 1,2/1,2 | 2,2/1,3 | 2,2/4,3 |
| 807013 R9 | Cutlery v PPP | Cutlery | elim r45 | r25 5,4/2,3 | - | - |
| 806999 R8 | Cutlery v cheji | Cutlery | elim r99 | 9,4/4,2 | 28,3/0 | - |
| 807006 R8 | PPP v larpmaxxing | larp | elim r116 | 3,3/8,5 | 2,3/17,6 | - |
| 806992 R7 | 中国必须 v larpmaxxing | larp | elim r187 | 2,2/5,3 | 6,2/13,3 | - |
| 806985 R7 | forgot v PPP | forgot | elim r28 | PPP hit 3 walls | - | - |
- What decided the games: the number of units. Winners split at every L4 into 2+2 (14-108 splits per game), ate 34-279 pearls (lots of them corpses: 29-132), and then won head-on trades between L2 dragons by outnumbering the enemy 5-15 to 1. Winners also lose lots of their own units (larp 27-66 HitSelf, Cutlery 8-31 NoValidAction) and do not care, because the corpses get re-eaten.
- Losers were teams that walled themselves (PPP 3 HitWall by r22) or stayed at 1-2 units. Neither side won more often: A 13, B 17 over the 30 R5+ games.

## 4. v35 on Stripes: 3/6 (wins vs Tattva, free trip, PPP; losses R2-R4 all by elimination)
- In our losses we ate only 1, 5 and 11 pearls, against their 34, 101 and 279. We never reached L4, so the split gate (SPLIT_LEN 4, main.cpp:3817-3820) never fired. We sat at 1-2 units while they had 10-17.
- Both of our dragons leave the food bands by about r13: one goes into enemy T through the wrap door, the other into M2. They then roam the empty middle bands (r19-37 heads at (2,2),(20,5),(5,3),(4,4),(10,3),(14,4)). Meanwhile the enemy colonises both outer bands, including our home Bot band (10-17 eats there by r80).
- Likely cause: on unknown maps, the hunger-driven explore (UNK_EXPLORE=1, computeExploreDesire main.cpp:3119, used at 1975/3868) sends heads to unseen tiles and through portals. The food tiles have long gaps, so countdowns give little pull to stay. The sealed boxes' early pearls may also have attracted heads (unverified).
- Fix ideas: a known-map entry for Stripes that camps the home outer band and the hotspot doors (x10-13), plus early splits at L4 with no viability gate.

## 5. New rules (queens id0/id1, free moves ceil(L/4))
- Free moves barely matter here: L <= 4 gives F=1, and nothing gets past L6.
- The queen spawn is exposed. Both queens start in their own food band, which is the band enemy swarms invade (2-4 enemy heads in our Bot band by r25-40, entering through the x10/13 doors right by the hotspot).
- Elimination still ends these games by about r300, so a queen strategy must not starve the swarm. Suggested plan: the queen steps through the home door at x1 (or x22) into her own middle band (M2 for A, M1 for B). That band has no food and the least enemy traffic. She circles at x9-14 and avoids the portal 4/5 exits (20-21,y6-7 for A), portal1 (x16-17) and the 1-row neck at x7-8. The rest of the army farms and splits as above. Queen hunting is cheap for the enemy because their hotspot door is right beside our queen's band, and the same holds for us against them.
