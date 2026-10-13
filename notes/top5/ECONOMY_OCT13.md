# Early and mid-game economy of aAah, larp and dev test 1 on our six worst maps (13 Oct 2026)

Read-only replay study. Nothing under bot/, variants/ or tools/ was changed, nothing uploaded or challenged, no local games run.
Scripts, per-game rows and full output tables are in `work/top_oct13/economy/` (rerun commands in section 10).

## 0. Answer

The three teams do not share one economy, but the same four things separate all of them from us. (1) **They stop splitting at 4 as the
team fills up** (aAah fades it out between 52 and 58 units, dev test 1 stops dead at 62) and from then on split only when the head is
boxed, keeping a 2-long stub and reversing the long part; by r250 aAah and dev test 1 hold 25-32 units of length 5+ that take two steps in
64-82% of their moves, have stood on 3,070-3,450 of the 4,096 tiles of Around UNSW and Australia (we: 840-1,280) and eat 1.7-2.2 times our
new pearls. We split 4 into 2+2 in 91-95% of our splits at any unit count up to 59. (2) **Hot corridors are pumped the same way by everybody**
(enter at L2-3, eat, split at the tip, the stub dies: +1.0 length a visit on Autarky, +1.0 to +1.8 on four-tile all-hot corridors); the
gap is the visit rate (Autarky after r100: dev test 1 7 visits per pocket per 100 rounds against aAah and 12-15 against us, we 1.6-2.5) and that they pump the
enemy's pockets from about r45-70. (3) **Nobody else walks into foodless dead ends**: we do it 58 times a game on Islands before r250
(dev test 1 11, aAah 7, larp 9), three quarters of the time for one corpse pearl, and lose about 100 length there. (4) **On Slithery
Fight our economy is level with dev test 1's until r250** (total 194 against 164 in our favour); we lose on the queen: theirs is fed from
r200 (length 10 / 34 / 57 at r250 / r350 / end, ours 3 / 6 / 4) and they cut voluntary splits to a third at exactly r350.
None of them avoids zero-net pockets and none times its visits to the spawn; dev test 1, and less often aAah, follow in while the last unit is still leaving.

## 1. Sample and definitions

- **420 games on the six maps**, one pass each (`extract.py`). aAah: 16-18 per map (100), 10-12 Oct, of which 46 against dev test 1. larp: 21 /
  14 / 10 / 15 / 12 / 14 (86), 10-12 Oct, mostly ranked against teams rated 2300+. dev test 1: its 91 games against us since 13 Oct 07:00 UTC
  (Slithery 22, Autarky 2, Islands 23, Around UNSW 13, Australia 18, Thermopylae 13) plus the 46 against aAah. Us: the same 91 games plus 90
  against other teams since 13 Oct 07:00 UTC ("us v others"; several km builds). 119 new replays were downloaded (120 GETs, 1.4 s apart).
- Every cell is **focus / opponents in the same games**; medians unless marked mean. In "dev1 v us" rows the second number is us.
- **Pocket** = the small side (at most 12 tiles) of a bridge of the tile graph: dead-end corridors and one-door rooms (`mapgeo.py`). **Hot
  tile** = spawn gap of mean 15 or less. **Visit** = a head entering a pocket, with the children split off inside, until all have left or
  died; **net** = length that leaves minus length that entered. **Forced split** = the head had no free neighbour.
- Two parser facts: the replay's own map text has all spawn gaps zeroed (classes come from `maps/server_live31/`), and in half the games
  dragon 0 belongs to team B (the replay's DRAGON lines say which).
- Autarky has only 2 games of dev test 1 against us; its Autarky numbers below also use its 9 games against aAah (dev test 1 won 5).
- dev test 1 never dies by self hit on Slithery Fight: a boxed unit sends the suicide action from round 0 (240-280 length per 50 rounds, the
  same rate as our self hits plus ally-body hits). It is its way of dying, not a feeding plan, until r250.

## 2. Question 1: spread and income

| map | team (n, wins) | units r50 | r100 | r250 | length r100 | r250 | tiles visited r100 | r250 | new pearls r100 | r250 | corpse pearls r250 | 2+-step moves r250 | portal crossings r100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Slithery | aAah (16, 11) | 57/50 | 61/60 | 62/62 | 226/146 | 323/164 | 902/726 | 1059/806 | 464/317 | 1254/720 | 692/627 | 2689/58 | 18/16 |
| Slithery | larp (21, 15) | 57/51 | 63/61 | 63/61 | 170/160 | 219/196 | 797/744 | 958/892 | 307/329 | 788/772 | 666/645 | 798/258 | 14/16 |
| Slithery | dev1 v us (22, 19) | 54/46 | 61/56 | 62/61 | 154/138 | 164/194 | 771/487 | 988/739 | 339/306 | 809/763 | 697/702 | 98/218 | 16/20 |
| Autarky | aAah (17, 7) | 13/16 | 16/18 | 18/28 | 41/46 | 44/63 | 482/505 | 636/655 | 57/68 | 152/186 | 109/174 | 29/12 | 40/21 |
| Autarky | larp (14, 10) | 16/15 | 17/18 | 29/12 | 42/42 | 68/28 | 482/510 | 668/622 | 58/63 | 162/148 | 150/115 | 12/17 | 22/30 |
| Autarky | us v others (15, 3) | 15/17 | 18/24 | 15/44 | 44/58 | 30/110 | 381/545 | 554/722 | 54/72 | 111/215 | 88/191 | 0/11 | 2/23 |
| Islands | aAah (16, 16) | 38/8 | 58/14 | 60/17 | 214/36 | 322/42 | 1232/266 | 1878/585 | 249/64 | 656/245 | 308/231 | 2434/53 | 58/12 |
| Islands | larp (10, 8) | 30/22 | 54/38 | 61/33 | 126/92 | 202/78 | 880/697 | 1642/1234 | 168/152 | 472/395 | 366/312 | 476/47 | 34/33 |
| Islands | dev1 v us (23, 18) | 24/30 | 39/47 | 60/49 | 97/112 | 181/121 | 630/537 | 1324/824 | 143/191 | 444/470 | 326/407 | 282/43 | 46/51 |
| Around UNSW | aAah (16, 7) | 40/30 | 58/49 | 60/56 | 229/134 | 348/176 | 1440/1100 | 3070/2430 | 300/192 | 807/490 | 393/338 | 3287/486 | 12/8 |
| Around UNSW | larp (15, 9) | 34/28 | 61/54 | 63/61 | 157/138 | 256/175 | 1059/992 | 2594/2269 | 215/200 | 591/488 | 430/296 | 1167/193 | 10/7 |
| Around UNSW | dev1 v us (13, 13) | 45/30 | 60/35 | 60/42 | 261/87 | 427/108 | 1568/506 | 3452/839 | 312/150 | 820/371 | 379/355 | 3670/1 | 10/2 |
| Australia | aAah (17, 16) | 26/19 | 52/25 | 60/20 | 143/64 | 382/52 | 1348/930 | 3386/1766 | 190/91 | 634/245 | 248/154 | 2508/42 | 31/17 |
| Australia | larp (12, 9) | 21/21 | 46/28 | 62/24 | 110/70 | 280/66 | 1080/959 | 2732/1766 | 112/123 | 467/298 | 262/207 | 1357/36 | 18/24 |
| Australia | dev1 v us (18, 17) | 18/20 | 47/31 | 58/27 | 120/74 | 344/70 | 1264/760 | 3336/1282 | 124/104 | 516/294 | 194/300 | 1915/0 | 15/16 |
| Thermopylae | aAah (18, 16) | 20/12 | 38/10 | 59/3 | 94/22 | 217/6 | 773/490 | 1988/957 | 80/21 | 267/32 | 101/28 | 553/3 | 69/27 |
| Thermopylae | larp (14, 8) | 17/14 | 22/23 | 23/37 | 52/56 | 57/91 | 666/595 | 1220/1353 | 52/44 | 146/128 | 83/128 | 12/11 | 34/40 |
| Thermopylae | dev1 v us (13, 12) | 15/17 | 20/20 | 26/25 | 47/48 | 64/62 | 533/434 | 1362/689 | 37/45 | 106/137 | 95/138 | 5/0 | 28/32 |

Rows at r25 and r150 and the "us v others" rows are in `out_q1_spread.txt` and `out_t1.txt`. Where the gap opens: Around UNSW between r25 and
r50 (dev test 1 23 to 45 units and 317 to 688 tiles; we 22 to 30 and 262 to 381, with 19 own deaths before r50 against 11 and 0 portal
crossings against 3). Islands: we lead until r100 (more splits, 43 before r50 against 24) and are passed by r150. Australia: level at r50,
lost by r100. Slithery, Thermopylae against dev test 1: no income gap at all (Thermopylae: we eat 152 new pearls by r250, they 99, and lose 12 of 13).

**Where the income comes from** (new pearls, mean per game, `out_q1_income.txt`):
- Slithery (52 pearls a round could spawn, 8 are eaten): open fields, not pockets. r100-249 aAah / its opponents: 1-5 class 367 / 239, 1-10 class
  288 / 86, hot pockets 62 / 57, in the enemy half 199 / 72. dev test 1 against us: all classes level (476 / 461).
- Autarky: the four pockets hold 8.7 of the map's 9.4 pearls a round. r100-249 from pockets: dev test 1 92, larp 58, aAah 52, we 23 (our opponents 106).
- Islands: the 20 tiles that spawn every round give about two thirds of all new pearls (58-92% by team and phase); only 8 of them are in the two corridors (aAah 32 of its 165
  by r100 from the corridors). Three open pairs matter: two at 3 and 5 steps from the queen and one in the middle at 20 steps from both.
- Around UNSW, dev test 1 / us: centre field (10-30 class, 34 tiles) 92 / 22 by r100 and 141 / 24 in r100-249; pearls eaten in the middle band
  of the map (within 6 steps of equidistant) 112 / 31 and 188 / 20; hot pockets 45 / 32 and 95 / 40.
- Australia, dev test 1 / us, r100-249: slow open tiles 40-200 class 94 / 31 and 1-200 class 59 / 20; middle band 158 / 54; the two 12-tile rooms 43 / 105.
- Thermopylae (1.5 pearls a round on the whole map): aAah takes 25 pearls in the enemy half by r100 and 65 in r100-249 (opponents 5 and 9).

**Richest fields: arrival and units** (first round a head stood on it, median; distinct units that had; new pearls there; `out_q1_fields.txt`):

| field (steps from own queen) | team | first head | units by r50 / r100 / r150 | new pearls before r100 / r250 |
|---|---|---|---|---|
| Around UNSW centre, 30 tiles (28) | aAah ; larp ; dev1 ; us (v dev1) | 16 ; 21 ; 18 ; 14 | 14/32/46 ; 10/27/46 ; 17/35/47 ; 8/12/14 | 70/173 ; 47/147 ; 89/222 ; 19/38 |
| Australia home room, 12 tiles 1-10 (17) | aAah ; larp ; dev1 ; us | 13 ; 40 ; 74 ; 58 | 11/25/38 ; 2/12/20 ; 0/1/2 ; 0/15/30 | 57/131 ; 27/69 ; 12/41 ; 25/82 |
| Islands home corridor, 4 tiles 1-1 (14) | aAah ; larp ; dev1 ; us | 40 ; 72 ; 54 ; 45 | 2/8/14 ; 0/2/8 ; 0/5/11 ; 1/7/12 | 24/64 ; 8/37 ; 13/51 ; 17/58 |
| Islands middle pair (1,36)+(54,36) (20 from both) | aAah ; larp ; dev1 ; us | 3 ; 3 ; 3 ; 5 | 7/11/14 ; 6/11/17 ; 5/11/18 ; 1/1/1 | 35/71 ; 26/68 ; 39/99 ; 2/2 |
| Slithery centre, 7 tiles x30-32 y12-14 (61 from both) | aAah ; larp ; dev1 ; us | 64 ; 105 ; 86 ; 444 (2 of 22 games) | 0/2/5 ; 0/0/1 ; 0/1/7 ; 0/0/0 | 15/48 ; 2/15 ; 4/48 ; 0/0 |
| Slithery three 1-5 fields on the own side, summed (39-47) | aAah ; larp ; dev1 ; us | 3-11 ; 3-12 ; 3-13 ; 3-10 | 27/52/76 ; 24/43/65 ; 29/56/82 ; 26/48/72 | 215/521 ; 148/350 ; 158/290 ; 148/342 |
| Thermopylae enemy-side field, 8 tiles 10-35 (36) | aAah ; larp ; dev1 ; us | 24 ; 12 ; 282 ; 160 | 2/8/14 ; 1/1/2 ; 0/0/0 ; 0/0/0 | 13/44 ; 7/22 ; 0/1 ; 1/11 |

We reach the Around UNSW centre first and then send a quarter of the units. dev test 1 ignores the Australia rooms and still out-eats us there.

## 3. Question 2: dead ends

Hot pockets, r100-249 (`out_q2_visits.txt`, `out_q2_timing.txt`). Order in every cell: aAah ; larp ; dev1 ; us (dev1 and us from their games against
each other, except Autarky: dev1 as aAah's opponent in 9 games, us from "us v others").

| pocket class (map, count) | visits per pocket per 100 rounds | entry length, median | pearls per visit new + corpse | ends: split and stub died % / whole unit died % | net per visit |
|---|---|---|---|---|---|
| corridor 4 deep, 2-3 hot (Autarky, 4) | 4.7 ; 5.4 ; 7.2 ; 2.1 | 2 ; 2 ; 2 ; 2 | 2.0+1.0 all | 97-100 / 0-2 | +0.95 ; +0.97 ; +0.98 ; +0.98 |
| corridor 4 deep, 4 hot (Islands, 2) | 10.3 ; 4.2 ; 5.4 ; 6.3 | 2 ; 2 ; 3 ; 2 | 2.8+1.1 ; 2.7+1.3 ; 2.3+1.3 ; 2.5+1.4 | 98/0 ; 89/10 ; 90/10 ; 99/1 | +1.72 ; +0.93 ; +1.02 ; +1.39 |
| corridor 4 deep, 4 hot (Around UNSW, 2) | 6.6 ; 5.2 ; 6.6 ; 4.5 | 3 ; 3 ; 3 ; 2 | 2.8+1.1 ; 2.5+1.5 ; 2.8+1.1 ; 2.8+1.2 | 94/6 ; 85/15 ; 94/6 ; 100/0 | +1.11 ; +0.33 ; +1.23 ; +1.71 |
| corridor 3 deep, 2 hot (Slithery, 10) | 2.8 ; 1.8 ; 3.4 ; 1.0 | 5 ; 3 ; 2 ; 2 | 1.4+1.2 ; 1.3+1.4 ; 0.9+1.6 ; 1.2+1.2 | 93/7 ; 77/23 ; 51/49 ; 82/18 | -0.43 ; -0.50 ; -1.09 ; -0.14 |
| corridor 2 deep, 2 hot (Around UNSW, 4) | 2.4 ; 0.3 ; 4.0 ; 0.1 | 4 ; 5 ; 5 ; 2 | 1.0+1.0 all | 96/4 ; 62/38 ; 94/6 ; 100/0 | -0.74 ; -2.08 ; -0.57 ; 0.00 |
| corridor 5 deep, 2 hot at the end (Around UNSW, 2) | 3.9 ; 3.2 ; 5.1 ; 0.4 | 3 ; 3 ; 3 ; 2 | 1.0+1.1 ; 1.0+1.3 ; 1.0+1.1 ; 1.0+1.1 | 93/7 ; 77/23 ; 92/8 ; 94/6 | -0.41 ; -0.93 ; -0.36 ; -0.06 |
| single hot tip (Around UNSW, 2) | 1.4 ; 0.7 ; 1.7 ; 0.1 (us v others 2.9) | 4 ; 4 ; 4 ; 3 | 0.1+0.9 all | 93/7 ; 45/55 ; 92/8 ; 50/50 | -1.85 ; -2.55 ; -1.59 ; -1.50 |
| room, 12 tiles 1-10, one portal door (Australia, 2) | 4.3 ; 1.8 ; 1.9 ; 4.1 | 2 ; 2 ; 2 ; 2 | 7.0+3.0 ; 8.5+4.0 ; 6.2+3.0 ; 10.5+11.4 | 55/37 ; 62/23 ; 47/46 ; 67/33 | +3.03 ; +4.80 ; +2.28 ; +1.13 |

- **The arithmetic everyone follows**: a dive ends with a split that leaves 2 at the tip, so net = pearls eaten inside minus 2; if length
  plus pearls is under 4 the whole unit dies. The stub drops one pearl on the tip tile, and while it lies there that tile cannot spawn. So a
  corridor's steady value per visit is (hot tiles other than the tip) + 1 - 2: Autarky +1, 4-hot corridors +2, Slithery's 3-deep and Around
  UNSW's 2-deep and 5-deep corridors 0, a single hot tip -1. The measured nets in the table are these values less the odd whole-unit death.
- **Zero-net pockets are not avoided.** Slithery's ten 2-hot corridors cost aAah 18, larp 13 and dev test 1 56 length a game in r100-249, and
  dev test 1 still enters each one 3.4 times per 100 rounds; all three enter the single hot tips and the 2-deep corridors with units of
  4-5 and lose 0.6-2.5 a visit. We enter those less than they do. Skipping them is worth 10-60 length a game to them, not a reason for our gap.
- **Queueing**: 6 rounds inside a 4-deep corridor for everybody. Rounds between own visit starts at one pocket: dev test 1 6-7, aAah and larp
  8-10, we 9-10. Visits that start while an own unit is still inside: dev test 1 31-39% (Autarky, Islands), aAah 13-21% (Islands, Around
  UNSW) and 1-2% (Autarky), larp 0-6%, we 0-3%. No waiting at the door and no timing to the spawn was found; enemy visits never overlap in
  a corridor (0%), in the Australia room 4-22% do.
- **Foodless dead ends are where we differ** (`out_q2_cold.txt`, `out_extra.txt`). Islands has 132 (116 single tips). Entries per game r0-99 /
  r100-249 / r250-499: us 12.8 / 44.9 / 40.3 (against others 8.9 / 32.9 / 36.3), dev test 1 1.3 / 10.0 / 16.6, aAah 0.4 / 6.2 / 14.2, larp 1.0 /
  8.1 / 8.0. Ours are 63% length 2 and 37% length 3, 75% eat a corpse pearl inside, 61-77% end with the whole unit dead (it leaves two
  pearls for the next one). Net length: us -24 / -76 / -65 a game, dev test 1 -2 / -17 / -32. aAah's rare entries are 79% length 4+ (a turn-around).
- **The Australia rooms**: we send 15 units by r100 and 30 by r150 into the home room and as many into the enemy's, eat 130 new pearls there
  in r100-249 and 11.4 corpse pearls a visit, and net +1.1 a visit: 14 length leaves the rooms in that phase, 11% of the new pearls eaten.
  aAah converts 44% (89 eaten, +39 out), larp 57% (46, +26), dev test 1 37% (35, +13) and has only 2 units there by r150.

**Splits that lose a half within two rounds, before r250, per game** (`q2.py bad`; "own" = self / ally body / no action, the badsplit.py definition):

| map | aAah own / wall | larp own / wall | dev1 own (v us) | us own (v dev1) | us: outside pockets / hot pocket / foodless pocket | dev1: same |
|---|---|---|---|---|---|---|
| Slithery | 289 / 0 | 118 / 106 | 197 | 305 | 269 / 33 / 3 | 126 / 69 / 2 |
| Islands | 64 / 0 | 8 / 22 | 48 | 123 | 76 / 29 / 18 | 23 / 20 / 5 |
| Around UNSW | 118 / 0 | 30 / 51 | 146 | 88 | 52 / 35 / 1 | 25 / 117 / 4 |
| Australia | 50 / 0 | 20 / 14 | 23 | 96 | 8 / 87 / 1 | 5 / 17 / 1 |

The count alone misleads: aAah has as many as we do on Slithery and more on Around UNSW. Theirs are forced turn-arounds of units of 6-7 that
drop a 2-long stub; ours are 4 into 2+2 where either half dies (parent 150, child 127 a game on Slithery; dev test 1 85 and 45). larp's stubs
die on the wall instead of on themselves, which is what LARP_OCT12.md recorded as "103 wall deaths a game, cause unknown".

## 4. Question 3: splitting policy

Splits by the team's unit count just before the split (Slithery, Islands, Around UNSW, Australia pooled; queens excluded). Cell: splits per game /
median length / % at length 4 / % forced / % where the child is the longer part.

| own units | aAah (65 games) | larp (58) | dev1 v us (76) | us v dev1 (76) |
|---|---|---|---|---|
| under 40 | 49 / 4 / 73 / 19 / 18 | 148 / 4 / 65 / 19 / 32 | 116 / 4 / 60 / 37 / 34 | 273 / 4 / 91 / 28 / 8 |
| 40-51 | 29 / 4 / 70 / 21 / 18 | 147 / 4 / 72 / 19 / 27 | 65 / 4 / 73 / 34 / 23 | 199 / 4 / 95 / 32 / 5 |
| 52-55 | 37 / 4-5 / 44 / 23 / 30 | 54 / 4 / 74 / 18 / 25 | 40 / 4 / 67 / 28 / 23 | 63 / 4 / 94 / 36 / 5 |
| 56-59 | 162 / 6-7 / 23 / 46 / 44 | 58 / 4 / 72 / 15 / 24 | 91 / 4 / 52 / 32 / 32 | 68 / 4 / 90 / 31 / 4 |
| 60-61 | 175 / 7 / 16 / 72 / 53 | 138 / 4 / 65 / 10 / 28 | 208 / 4 / 55 / 35 / 25 | 82 / 4 / 77 / 27 / 13 |
| 62-63 | 188 / 7 / 17 / 71 / 61 | 228 / 5 / 40 / 34 / 60 | 58 / 10-11 / 11 / 72 / 65 | 34 / 4 / 67 / 37 / 31 |

- **aAah**: 4 into 2+2 while under about 52 units; between 52 and 58 the voluntary split fades (share at length 4: 54% at 52-53, 40% at 54-55,
  30% at 56-57, 19% at 58-59); from 58 units on, 53-77% of its splits are forced, at a median length of 7, and the child is the longer part.
- **dev test 1**: 4 into 2+2 up to 61 units, then nothing voluntary: at 62-63 units it makes 58 splits a game, median length 10-11, 72% forced.
  It keeps the last two slots for turn-arounds (FTM's rule in TOP3_SYNTHESIS_OCT12.md). On Slithery, Islands, Autarky and Thermopylae its army
  stays at mean length 2.5-3.1 at r250 even at 62 units (inference: units die before they grow; 270 length per 50 rounds on Slithery).
- **larp**: 4 into 2+2 all the way to 64 units; at 62-63 the median is 5 and 60% are reversals.
- **By phase** (`out_q3_splits.txt`): aAah's median split length on Slithery is 4 before r50 and 6 from r50 (the round it reaches 60 units: r53);
  on Islands, Around UNSW and Australia it is 4 until r100-150 and 6-9 after. dev test 1 on Around UNSW: 4, 5, 6, 8, 10, 11 over the six phases.
- **Units of 5-8 are kept and used.** Share of living units at length 5-8 / 9-15 at r250: aAah 21-26% / 12-20% on the four big maps (25-31 units of
  length 5+, mean length 5.2-6.6); dev test 1 on Around UNSW and Australia 23-24% / 19-21% (31-32 units, mean 6.4-6.8); larp 14-18% / 4-11% until its
  r250 suicides; we 1-10% / 0-3% against dev test 1 (0-7 units, mean 2.4-3.1). Moves of 5-8-long units that take 2+ steps: aAah 64-82%, dev test 1
  75-81% on the two big maps, larp 51-79%, we 40-56%.
- **Paid steps** per 50 rounds: aAah 71-83 on Slithery and 9-30 elsewhere, dev test 1 8-22 on the big maps, larp 6-14, we 0 in every game. What
  they buy with them was not measured (unverified: lunges and contested pearls).
- **At the cap**: rounds at 62+ units in r100-249: aAah 67 (Slithery) and 28 (Around UNSW), larp 96-141, dev test 1 60-84. Units of 4+ lost to self
  hits or walls while at 62+ units, per game: aAah 93 on Slithery and 27 on Around UNSW, larp 72 and 30, dev test 1 53 on Around UNSW. That is the
  price of sitting at the cap; aAah pays it and still nets +25 to +50 length per 50 rounds until r250.

## 5. Question 4: the mid game

**Slithery Fight, dev test 1 / us** (22 games; mean per game per 50 rounds; units, total and longest are medians at the end of the window):

| rounds | units | total | longest | queen | new pearls | own-corpse pearls | lost in deaths | splits | voluntary 4-splits | pearls eaten by 10+ units, new + own corpse |
|---|---|---|---|---|---|---|---|---|---|---|
| 150-199 | 62/62 | 158/182 | 6/8 | 2/4 | 153/155 | 156/147 | 310/298 | 86/107 | 46/55 | 0+0 / 0+0 |
| 200-249 | 62/61 | 164/194 | 11/11 | 10/3 | 151/152 | 162/152 | 315/298 | 95/98 | 57/48 | 0+3 / 3+1 |
| 250-299 | 61/50 | 178/175 | 22/24 | 22/6 | 164/154 | 160/202 | 307/384 | 102/141 | 61/83 | 3+10 / 5+24 |
| 300-349 | 55/40 | 202/170 | 35/33 | 34/6 | 151/151 | 159/183 | 297/351 | 111/134 | 61/78 | 8+30 / 7+23 |
| 350-399 | 32/40 | 210/167 | 48/41 | 40/6 | 143/147 | 131/167 | 260/326 | 80/132 | 19/74 | 14+39 / 6+22 |
| 400-449 | 18/41 | 194/181 | 62/48 | 51/6 | 120/151 | 121/154 | 255/301 | 74/126 | 15/72 | 27+50 / 6+19 |

- Income is identical on both sides through r349. Their total does not grow from eating more; it holds near 200 while their unit count
  falls from 61 to 18, because the length moves into the queen. 13 of their 19 wins are "queen longer", 5 "queen alive against dead"; both
  queens are alive at r500 in most games (theirs 18, ours 16 of 22). Ours also builds a long dragon (longest 47 at the end), but it is not the queen.
- **What changes for them and when**: the queen starts to grow at r200-250; voluntary 4-splits drop from 61 to 19 per 50 rounds at exactly r350
  and to 4 from r450, forced turn-arounds continue; share of their no-enemy deaths with a longer ally of 10+ in the 7x7 view: 2% (r150-249), 11%,
  26%, 31%, 40% (r400+). Ours: 1%, 25%, 26%, 26%, 24%, while our voluntary splits stay at 72-83 until r450 and we still lose 300-350 length per 50 rounds.
- larp on Slithery does the same from r250 (queen 3 / 19 / 37 / 50 at r250 / r300 / r350 / r400; suicide action 143-216 length per 50 rounds from r250).
- aAah has no merge at all: queen 2-4 all game, longest 18-23. It wins Slithery with mass (new pearls 247-272 per 50 rounds against 138-151,
  paid steps 71-83) and by the opponent's queen dying (9 of its 11 wins), and loses when she lives (0-2 on queen length).

**Islands, dev test 1 / us** (23 games), length lost per 50 rounds from r50 to r349: self hits 26/66, 41/83, 60/97, 72/98, 79/95, 85/120; ally body or
head 3/13, 7/22, 12/25, 15/25, 20/24, 22/20; head-ons where the unit moved in 30/24, 53/33, 49/30, 42/33, 39/32, 40/24; was hit 21/26, 30/49, 32/44,
36/38, 39/34, 30/38. New pearls 84/104, 92/97, 101/94, 99/89, 96/86, 98/69. We eat as much and trade evenly; we lose 40-50 more length per 50
rounds to ourselves (the foodless dead ends of section 3 and 2+2 splits in the open: 76 bad ones a game against 23). Total at r250: 181 / 121.
Decided by the longest with both queens dead (13 of their 18 wins): longest at the end 47 / 32; from r350, 50-57% of their no-enemy deaths have a 10+ ally in view.

**Autarky**: units stay at length 2-3 for everybody all game (92-98% of units); only larp builds a long dragon, from r250 (longest 18 at r350); 24
of the 31 aAah and larp games end by elimination (median last round 240-275). The mid game there is section 6.

## 6. Question 5: Autarky

Each side has two home pockets (15 and 26 steps from its queen; the 14-long starting dragon lies between them). One cycle: enter at length 2-3,
eat 2 new pearls and the last stub's corpse pearl, split at the tip (5 into 3+2 or 4 into 2+2), child out after 6 rounds: +1.0 length and one corpse
pearl banked. A pocket can take a visit every 6-7 rounds, about 15 per 100 rounds. Per 50 rounds (`out_q5_autarky.txt`):

| rounds | us v others (15): units us ; them | home-pocket visits | visits to the other side's pockets | net length from pockets | head-on deaths: moved in / was hit (us) | deaths within 4 steps of the home pocket doors, head-on / other | dev1 as aAah's opponent (9): home ; away visits |
|---|---|---|---|---|---|---|---|
| 0-49 | 15 ; 17 | 10.7 ; 10.1 | 0.3 ; 0.7 | +10.0 ; +8.7 | 1.9 / 3.5 | 1.5 / 10.4 ; 0.4 / 9.4 | 12.0 ; 1.4 |
| 50-99 | 18 ; 24 | 6.0 ; 11.3 | 0.1 ; 3.6 | +6.2 ; +13.8 | 2.9 / 4.8 | 2.4 / 6.1 ; 0.9 / 12.1 | 11.3 ; 2.9 |
| 100-149 | 20 ; 30 | 4.7 ; 11.7 | 0.0 ; 4.8 | +4.5 ; +14.7 | 4.3 / 7.2 | 3.0 / 4.9 ; 0.7 / 12.1 | 10.4 ; 2.8 |
| 150-199 | 16 ; 36 | 3.5 ; 10.9 | 0.3 ; 6.1 | +3.7 ; +16.6 | 4.7 / 7.5 | 3.2 / 3.7 ; 1.2 / 11.7 | 9.7 ; 3.8 |
| 200-249 | 15 ; 44 | 3.5 ; 11.1 | 0.6 ; 7.1 | +4.1 ; +16.7 | 5.5 / 8.2 | 2.8 / 3.8 ; 0.2 / 11.4 | 14.7 ; 6.7 |

- **Our home pump halves at r50 and never recovers**; theirs runs at 10-12 visits per 50 rounds (65-70% of what two pockets can take) all game. dev
  test 1 against us (2 games): 14-16 home visits per 50 rounds from the start, 7 visits to our pockets in r50-99 and 13-15 from r200.
- **They raid.** First visit to one of the other side's pockets, median round: our opponents r56 (before r100 in 12 of 15 games), dev test 1 r42-47,
  aAah r66, larp r69, we r98 (2 of 15). In r100-249 an enemy unit is inside one of our home pockets in 35% of the rounds; we are inside theirs in 2%.
- **The trade war is even and they still win it.** Head-on deaths are one for one by definition; r50-249 both sides lose about 45 units to them. Our
  opponents start 61% of them and 20-31% of ours happen within 4 steps of our own pocket doors (theirs near their doors: 2-12%). Meanwhile pockets
  give them +62 length against our +18, so units go 24 to 44 for them and 18 to 15 for us. There is no defence: nobody guards a pocket, the "other"
  deaths at their doors are their own stubs (11-12 per 50 rounds).
- larp wins Autarky the same way, later: level with its opponents until r150 (17 / 18 units at r100), then home 8-10 and away 4-5 visits per 50
  rounds from r200 while the opponent's home visits fall to 5; units 29 / 12 at r250. aAah is the weak one here (7 wins in 17; home visits 6-9).

## 7. The six maps in short

- **Slithery Fight**: level with dev test 1 until r250; lost on queen length. Economy gap exists only against aAah-style mass (their 323 total at
  r250 against 164). Free extras we skip: the centre field (48 pearls by r250 for dev test 1 and aAah, 0 for us).
- **Autarky**: pump both home pockets without pause and raid from r50. Everything else is even.
- **Islands**: we start faster and then lose 40-50 length per 50 rounds more than dev test 1 to self hits (roughly 20 of it in foodless tips, an
  estimate); we never touch the middle pair (99 pearls by r250 for dev test 1). aAah eliminates everyone (16 of 16): 58 units, 214 length at r100.
- **Around UNSW**: lost between r25 and r50. dev test 1 has 45 units at r50 and 17 of them have been on the centre field; we have 30 and 8, and 0
  portal crossings. From r100 it sits at 60 units, 31 of them of length 5+ by r250. dev test 1 also beats aAah here (5 of 7) with the same play.
- **Australia**: our units go into the two rooms and die on each other (net +1 a visit); dev test 1 walks the open slow tiles with two-step units
  (3,336 tiles by r250, we 1,282) and holds the middle band (158 pearls against 54 in r100-249).
- **Thermopylae**: against dev test 1 our income is higher and we lose 12 of 13 on the queen (theirs alive at the end in 12, ours in 2): not an
  economy map for that pairing. aAah's economy there is portals: 26 crossings by r50 and 69 by r100 (others 14-18 and 27-40), 14 units on the enemy-side
  field by r150, 38 units at r100 against 10, elimination in 16 of 18 (median r298).

## 8. Rules to implement, by expected value

1. **No foodless dead ends, and no dead end worth less than +1.** Condition: the next tile lies in a static pocket (small side of a bridge, at most
   12 tiles). Its static value is (hot tiles other than the tip) - 1; P = pearls on its tiles now. Action: enter only if the static value is >= 1
   or P >= 3, and length + P >= 4; otherwise treat its tiles as walls, corpse pearls included. Evidence: Islands, 58 entries a game before r250
   against 7-11 for the three teams, -100 length before r250 and -165 a game (section 3); single hot tips cost every team 1.5-2.5 a visit.
2. **Keep every hot corridor on the own side busy.** Condition: a corridor pocket with 2+ hot tiles and depth 3-5, no allied head inside (or only a
   child on its way out), my length 2-3 and my path to the door at most 8 steps. Action: go in, eat to the tip, split keeping 2, child walks out;
   a unit that sees an ally inside waits one or two tiles off the door instead of leaving. Target 12+ visits per pocket per 100 rounds. Evidence:
   +1.0 net a visit on Autarky and +1.0 to +1.8 on Islands and Around UNSW (larp less after r100); our Autarky rate falls from 10.7 to 3.5 visits per 50
   rounds while every opponent holds 10-12 (section 6); dev test 1 starts 31-39% of its visits while its last unit is still inside.
3. **Raid the other side's hot corridors from r50.** Condition: round >= 50, own units >= 16, my length 2-3, both home pockets occupied or queued.
   Action: walk to the nearest hot corridor on the enemy side and run rule 2 there. Evidence: opponents r56 (12 of 15 games before r100), we r98;
   their raids add 7-14 pearls per 50 rounds and put a unit in our pockets in 35% of rounds; pocket net r50-249 +62 against +18.
4. **Unit-count gate on the 2+2 split, and reverse splits.** Condition and action: under 52 own units split 4 into 2+2 as now; from 52 to 61 split
   only at length 6+ or when the head has no exit; at 62+ only when the head has no exit (never fill slots 63 and 64 voluntarily); a forced split of
   length L keeps 2 at the head and sends L-2 back out. Units of 5-8 take the free second step whenever it does not end next to an enemy head.
   Evidence: section 4 table (our 91-95% at length 4 up to 59 units; child longer in 5% against 44-65% for aAah and dev test 1 near the cap);
   25-32 units of 5+ at r250 against our 0-7; tiles visited and new pearls on Around UNSW and Australia 2.6-4.1 and 1.8-2.2 times ours.
5. **Fixed mid-field targets with a head count.** Condition: I am a new child, no pearl within 3 steps and 2+ allied heads in view. Action: head for
   the best static fast field by spawn rate over path length that has fewer than 3 allied heads in my view near it, crossing portals on the way.
   Known targets: Around UNSW centre x28-35 y27-36 (14+ units by r50, 32+ by r100), Islands (1,36) and (54,36), Slithery x30-32 y12-14, Thermopylae the
   enemy-side field through the portals. Evidence: section 2 field table (Around UNSW 8 units by r50 against 14-17; Islands middle pair 2 pearls
   against 68-99; Slithery centre 0 against 48).
6. **Slithery (and any map where both queens live): the queen is the king from r200, and stop the 2+2 split at r350.** Condition: round >= 200 and
   queen alive: units of 2-3 with the queen's head in view and no enemy head within 4 die in her path (or she eats corpses first); round >= 350:
   no voluntary splits. Evidence: section 5 table; queen 10 / 34 / 57 against 3 / 6 / 4; 18 of dev test 1's 19 wins and larp's 11 of 15 are queen results.
7. **Cap the heads in a one-door room.** Condition: target tile is in a room pocket and 3+ allied heads are visible inside or at its door. Action: do
   not enter; take the nearest open spawn tile instead (the threshold 3 is a proposal, not measured). Evidence: Australia, we turn 11% of the
   rooms' new pearls into length that leaves them, the three teams 37-57%; dev test 1 stays out and wins 17 of 18.
8. **Do not dive a pocket of static value 0 with a unit of 5+.** Evidence: on 2-3-deep hot corridors entrants of 5+ net -0.9 to -2.6 a visit for
   every team; small value (10-60 length a game), and rule 1 already covers it once the static value is used.

## 9. Not determined or unverified

- Why our Autarky home visits halve at r50 (our units leaving, or enemy pressure at the doors): only the rate and the door deaths were measured.
- What the top teams' paid steps are spent on, and whether dev test 1's waiting at pocket doors is a rule or a side effect of density.
- dev test 1's Autarky pump rate against us rests on 2 games; larp and aAah were sampled on 10-12 Oct and may have changed since.
- Rule 6 overlaps the queen items of TOP3_SYNTHESIS_OCT12.md; its r200 and r350 rounds are dev test 1's on Slithery only.
- Per-map rows rest on 10-23 games per team; pocket rows on 100-2,000 visits. Nothing here was built or tested.

## 10. Rerun (from `/Users/devsingh/Developer/UNSW_Battlecode`; `python3 -I`, 2 worker processes, no network except fetch.py)

```
python3 -I work/top_oct13/economy/fetch.py --dry      # selection only; without --dry downloads (public replay GETs, 1.4 s apart, capped)
python3 -I work/top_oct13/economy/index.py            # games.json (420 games)
python3 -I work/top_oct13/economy/extract.py          # rows/<gid>.json, about 4 minutes
python3 -I work/top_oct13/economy/q1.py spread|income|fields [MAP]     # section 2;  t1.py: the condensed table
python3 -I work/top_oct13/economy/q2.py visits|timing|cold|bad [MAP]   # section 3
python3 -I work/top_oct13/economy/q3.py lens|splits|speed|cap [MAP]    # section 4
python3 -I work/top_oct13/economy/q4.py ledger|causes|merge [MAP]      # section 5
python3 -I work/top_oct13/economy/q5.py Autarky                        # section 6;  decide.py: how games end;  extra.py: follow-ups
```
