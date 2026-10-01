# Sprint R16: PPP 4-3 us (battle 806947, games 806947-806953; PPP = team A). Replays: scratchpad/q/ppp/*.replay | scripts: scratchpad/q/ppp_an*.py | cells = PPP n,max / US n,max
| game | map (WxH, kelp edges, portal pairs, start dragons/side) | result | r50 | r100 | r200 | r300 | r400 | final |
|---|---|---|---|---|---|---|---|---|
| 806947 | Australia 64x64, 648 kelp, 4 portals, 9/side | L, r500 tiebreak 35 vs 32 | 24,3/19,3 | 57,4/28,3 | 63,11/55,4 | 56,21/64,10 | 62,29/36,27 | 42,35/11,32 |
| 806948 | Islands 56x40, 1014 kelp, 12 portals, 5/side | L, r500 28 vs 11 | 29,4/25,4 | 58,4/41,3 | 62,11/34,4 | 57,26/37,7 | 41,40/13,10 | 33,28/4,11 |
| 806949 | Maze 48x24, 620 kelp, 16 portals, 2/side | L, r500 71 vs 62 | 12,4/16,3 | 31,4/24,4 | 55,4/52,4 | 34,17/44,4 | 21,56/31,25 | 12,71/4,62 |
| 806950 | Stripes 24x12, 154 kelp, 8 portals, 2xL2/side | W, PPP eliminated r224 | 1,2/1,2 | 2,2/1,2 | 2,2/4,3 | - | - | 0/4,2 |
| 806951 | Tower Defense 32x16, 292 kelp, 0 portals, 2xL2/side | W, PPP eliminated r150 | 3,3/5,3 | 1,2/26,4 | - | - | - | 0/33,4 |
| 806952 | Around UNSW 64x64, 858 kelp, 4 portals, 10/side (one L10) | L, r500 62 vs 35 | 49,3/36,3 | 62,8/59,4 | 64,13/64,8 | 49,27/62,13 | 56,51/56,27 | 43,62/36,35 |
| 806953 | weakhold 40x15, 305 kelp, 0 portals, 2/side | W, r500 43 vs 23 | 7,3/6,5 | 9,3/19,5 | 11,3/34,5 | 7,9/31,8 | 9,13/12,25 | 3,23/11,43 |
Decisive moments
- Australia: PPP ate 193 pearls to our 54 in r1-100 (57 v 28 units at r100). We caught up on max (32 v 29 at r450), then our king stalled at 30-32 while theirs went 29->35 in r450-500. Our 23-long #2 suicided into the king at r432; it would have been worth more kept alive.
- Islands: we never got a king (max 4 until r275, 13 at r350). Units fell 37->13 between r300 and r400 (feeding plus head-on trades) while PPP held about 57. PPP even rammed its own 42-long king at r406 and still won 28 v 11.
- Maze: PPP's king took off at r250-275 (15 at r275, 38 at r350) and ours at r325 (14, then 18 at r350). We were always about 20 behind and closed only to 9.
- Around UNSW: PPP's king passed 27 by r300 and we never caught it. Our 20-long and 17-long dragons were killed head-on by PPP 3-4s (r357, r370), so they never became feeders.
- Wins: tiny or kelp-dense maps. PPP had 120 HitWall deaths on weakhold and walled/rammed itself out on Tower Defense and Stripes. **PPP's pathing is weak in narrow kelp**; it is strong on big open maps.
What lost the 4 games (the same pattern each time, map-independent)
1. **We give up territory late.** Natural pearls eaten r251-500, on our side of the map: PPP 283 v us 76 (Australia), 288 v 76 (Islands), 184 v 295 (UNSW), 142 v 246 (Maze). We barely invade theirs (Islands: 7 pearls on PPP's side by r250).
2. **Our unit count collapses after r300** (SPLIT_STOP 350 plus UNK_KING feeding plus head-on trades): r401-500 splits PPP 118/157 v us 17/12 (Australia/Islands). Fewer heads means fewer pearls and less defence, so PPP's mid-size dragons graze our side.
3. **Our king starts later and gets a smaller feed supply** (unknown-map UNK_KING seeds around r250-325; PPP's max is already 9-13 by r150-200). We lose the final race by 3-27.
4. Early foraging on the big many-dragon maps: eats per head-round in r1-100 were 0.03 v 0.06 on Australia. PPP also crossed the wrap edge/portals into neutral areas (visited 1188 tiles v our 872 by r100).
What PPP does that is distinctive
- **It keeps about 60 units all game and never stops splitting.** Mid-size dragons (9-14) keep shedding 2-long head pieces (split k = L-2, so the tail continues as the new dragon), 36-81 times per game against our 1-17. It still splits 120-200 times per 100 rounds after r300.
- **It grows several big dragons, not one.** Final top lengths: Australia 35/30/27/23, Islands 28/24/20/19. These are insurance plus late feed, and it loses nothing when one dies (its 42 king at r406).
- **It feeds by over-sprinting (NoValidAction).** 40-76 NVA deaths per 100 rounds after r200, often 10-37 long, 2-10 tiles from its king, so the dropped pearls land for the king to eat. Its feeding also starts at r200, earlier than ours.
- It churns a lot (525-730 deaths per game, about half from walls/NVA/self) but recycles the corpses (about 50% of its eats are corpses), and it trades head-on 1:1 with us.
- Its weakness: kelp-dense or narrow maps (many HitWall deaths) and 2-dragon tiny starts.
Implications for the Qualifier (general): keep splitting/foraging units near the cap through r450 rather than collapsing into feeders; seed the king by r150-200 on unseen maps; keep 2-3 big dragons as insurance and feed only small ones (not a 23-long #2); contest and defend natural-pearl territory late.
