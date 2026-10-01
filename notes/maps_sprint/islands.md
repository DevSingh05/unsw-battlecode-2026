# Islands (Sprint), 56x40, SYMMETRY y (left-right mirror), torus wrap
**Structure.** One connected sea (2192 of 2240 tiles; the rest are 1-11 tile cells). The "islands" are about 300 small kelp blobs: 1014 kelp edges, roughly 23% of edges. There are 158 dead-end tiles and 14 sealed ones. Rows 0-3 and the bottom row wrap into an open band along the north. 12 portal pairs, all on horizontal (N) edges, each joining a side region to the centre or bottom: 0:(10,11)-(24,16), 1:(45,11)-(31,16), 2:(22,13)-(15,23), 3:(33,13)-(40,23), 4:(26,24)-(16,25), 5:(29,24)-(39,25), 6:(27,26)-(15,35), 7:(28,26)-(40,35), 8:(18,36)-(1,38), 9:(37,36)-(54,38), 10:(4,39)-(26,39), 11:(29,39)-(51,39).
**Pearls.** All TILE gaps are 0 0 in maps/sprint/islands.map and in the replay's map text, so a local run spawns **no pearls**. Gaps below come from replay tileChange events, with pearls present at r0. Rich (median about 5): a 4-tile fountain at (8,6),(14,6),(8,9),(14,9) mirrored at (41/47,6/9), (1,36)/(54,36), and (13,21)/(42,21). Medium (about 10): (16,12),(16,13),(17,13) and mirrors; (12-13,36-38) and mirrors. Rare (about 50+): (21,22),(34,22),(2,1),(53,1).
**Dragons.** 5 per team (2x len 3, 3x len 2; 12 segments). Starts interleave across the halves. id0=B len3 head (10,7) facing W, **in the middle of the NW fountain**. id1=A len3 (45,7) facing E in the NE fountain. B also has (18,38)L3, (40,21), (24,14), (3,32). A has (37,38)L3, (15,21), (31,14), (52,32). Each team has a len-2 dragon next to the other side's mid fountain.
```
|  .         .  :          . |  2x2 blocks: ' '/./:/# = kelp density
|::..FQ F.:.: . ...:.F qF..#:|  Q = B queen id0, q = A queen id1
| : .F  F:..      :..F  F ...|  F = rich fountain, f = medium
|.. ..0.. .:..  ..:: ..1.. ..|  0-9,a,b = portal ends
|. . .:.:f .2 ...3 .f:.::  ..|  A/B = other starts
|......:.:   B..A  ...:.:. .:|
| .:::::.:  .0..1.  ..:.#..: |
|. . .:FA.:.      ...BF:.  ..|
| ..: . 2 : .#:::: : 3 . ..  |
| . .... 4....45 :.:5  .:.   |
|   . ..: ....67 :.. :.. .   |
| B  .. : :...:.:..:.....  A |
|..    .6   .    ..  7:    ..|
|F .   f  8  .  .  9  f.  . F|
|8 a.  .  B ..ab.. A   . .b 9|
```
(6 of 20 rows omitted; they are low-detail mid rows.) **Intent:** a scattered-rock archipelago. It tests local pathing among dead-end alcoves, blind portal shortcuts into the centre, and fights over fountains (home fountains are rich, and each team has a raider sitting on the other's mid fountain). There are no hard chokepoints.
**Games** (top-16, r5+): 31 games, side A won 21, mostly the higher seed. Ten replays (scratchpad/maps/isl_*.replay); 9 went to r500 and were decided by the longest dragon (old rules).
| game | A v B | win | r100 n/max A,B | r300 | r500 (n/L) |
|---|---|---|---|---|---|
| 806948 | PPP v **US** | A | 58/4, 41/3 | 57/26, 37/7 | 33/28 v 4/11 |
| 806878 | **US** v freetrip | A | 35/4, 55/7 | 64/6, 58/16 | 39/37 v 4/24 |
| 807011 F | Cutlery v PPP | A | 56/8, 33/4 | 61/9, 32/8 | 14/60 v 19/29 |
| 806997 | Cutlery v cheji | B | 3/3, 64/6 | elimination r142 | - |
| 807004 | PPP v larp | A | 64/4, 26/6 | 37/25, 12/4 | 20/69 v 9/6 |
| 806983 | forgot v PPP | B | 31/3, 43/3 | 23/4, 46/19 | 2/7 v 32/49 |
| 806976 / 806969 / 806990 / 806920 | cheji>zitian, Cutlery>calc, larp>zhongguo, calc>Goated | | | | L 37v18, 64v49, 33v4, 42v28 |
**What decided games:** (1) **Portal use.** The winner made more portal crossings in 9/10 games (PPP 387, cheji 760, larp 459, Cutlery 404); **we made 0 in both our games**. (2) A bigger swarm at r100 (8/10). (3) A late king fed at a fountain or in the north band (kings sat at (47,3), (42,0), (8,5), (12,9), (2,36)), grown from r300. Before r250 nobody's longest passed 12.
**v35 here (Isl 5/6; lost r6 to PPP as B).** (a) It never crossed a portal. Unknown-map exploration is gated on `UNK_EXPLORE_HUNGER 100000` (params.hpp:641-642, main.cpp:3154), so it fires only in a "closed" pocket, and Islands has none. That left v35 shut out of the centre and bottom fountains. (b) Self-deaths: 165 HitSelf in the loss (375 even in our win vs freetrip), all 1-step, len 2-3, from r8 onward. 85/165 heads were on dead-end tiles: small foragers walk into alcoves and have to reverse into their neck. Some are feed suicides (main.cpp ~3650). (c) Splitting at L4 (358/386 splits) plus those deaths kept our longest at 3-4 until r250. PPP's king was 26 by r300.
**New rules (queens).** Each queen spawns on its home 4-tile fountain, in a fairly open pocket (25 tiles within 3 steps, 3 dead ends within 8). It is 29+ walking steps from every enemy start, so **safe at r0-50**. The danger is portal 0/1, only about 4 tiles south, which drops blind arrivals from the centre (24,16)/(31,16), plus the fountain drawing every king and raider later. In Sprint, 19/20 id0/1 died by r39-120 (H2H or HitWall/HitSelf at len 2-3). A queen strategy here needs: no dead-end tiles for the queen (veto deg-1 tiles; reversing kills); avoid the N-edge portal tiles (10,10-11)/(45,10-11) and the tiles beside them; forage the home fountain early, then shift to the quieter row 1-3 band away from x≈8-14/41-47 once enemy kings show up (r250+). Portal learning is a must for the army, not the queen. Also rebuild a local Islands map with the gaps above, otherwise local tests have no pearls.
