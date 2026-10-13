# Queens of aAah, larp stock zi balls and dev test 1: where she stands, how she lives, how she's fed (13 Oct 2026)

**Short answer.** None of the three guards the queen, hides her, or hunts ours. She's a length-2 or 3 unit from round 0 that
walks around her own half, 7 to 17 walking steps from her start tile, with one own head within 4 steps and 3 to 5 within 8
(7 to 11% of the team, passers-by: 80% of them are gone ten rounds later). An enemy head comes within 5 steps of her about
twice per 100 rounds, the same rate as for ours, and she steps away exactly as ours does; what differs is the ending: 9 to
12% of those approaches end with their small queen dead, 30% with ours. Their queen stands in open ground (60% of her rounds
on tiles with 41+ tiles inside 5 steps, ours 29% because our hide blocks are pockets), and one of their heads is within 5
steps of the enemy queen's start tile by r88-135 in 138 of 139 games on the three 64x64 maps, one of ours in 50 of 99, at r219-315.
larp and dev test 1 feed her from r212-254 by letting length-2 and 3 units die 1 to 3 steps from her head: dev's queen eats
64 to 85% of pearls dropped at 1-3 steps but 30 to 37% of those dropped at 4-5 (larp 43-65% and 31-32%), and 57% of our
feeder pearls drop at 4-5. That gives them 0.24-0.26 length per round and 58-84 at r500 on Slithery Fight against our 6.5. aAah still doesn't
feed (queen ends at 3) and wins on mass. Enemy queens die to ordinary length-2/3 units that lunge with a paid step.

## 0. Sample and method
- **aAah** (454): 191 games = 112 ladder games of 10-12 Oct from the earlier study (losses and strong opponents over-sampled,
  75-37) + 21 Qualifier games + 56 new downloads + 2 of our games against them on 13 Oct. **larp** (157): 190 = 122 (79-43)
  + 56 new + 12 of our games on 13 Oct. The 112 new downloads are the latest 8 ranked games per team on each of the seven
  maps up to 12 Oct 3:37 PM EDT, picked without looking at result or opponent (aAah 49-7, larp 48-8). Each team now has 11
  to 15 games per focus map. No game list newer than 12 Oct 3:45 PM EDT was crawled.
- **dev test 1**: 275 of our own server games, 12 Oct 3:58 PM to 13 Oct 3:18 PM EDT (dev 194-81); Autarky 2 games, Maze 0.
  **us**: 554 server games from 12 Oct 11:37 PM EDT (207-347; 226 against dev test 1, mixed km builds).
- F = the named team, O = its opponents in the same games. "Steps" = walking steps on the map graph (kelp blocks, portals
  connect, bodies ignored). Hazard tables in section 2 leave out the sealed-room maps (Detention, Schooltime).
- Scripts and per-game cache: `work/top_oct13/queen/` (section 9). Starting lengths are corrected (no +1).

## 1. Where she is, how long, who's around her
Alive / games that reached the round; walking steps from her start tile, median (q1-q3); length, median.

| round | aAah | larp | dev test 1 | us |
|---|---|---|---|---|
| r25 | 190/191; 11 (8-17); L2 | 190/190; 10 (6-13); L2 | 271/275; 10 (6-16); L2 | 541/554; 10 (6-17); L3 |
| r50 | 184/191; 15 (10-23); L2 | 184/188; 11 (7-15); L2 | 264/275; 7 (3-17); L3 | 519/551; 7 (5-15); L3 |
| r100 | 171/189; 17 (7-29); L3 | 165/186; 13 (8-21); L3 | 229/274; 11 (3-24); L3 | 436/548; 7 (4-15); L3 |
| r200 | 128/169; 13.5 (5-29); L3 | 116/165; 9 (5-12); L3 | 179/271; 7 (3-20); L3 | 325/525; 7 (3-13); L3 |
| r300 | 86/136; 12.5 (5-25); L3 | 93/144; 9 (5-15); L16 | 145/265; 9 (3-19); L9 | 243/490; 6 (3-11); L3 |
| r400 | 69/119; 7 (4-20); L4 | 75/132; 8 (4-16); L38 | 131/263; 11 (3-22); L11 | 178/470; 6 (2-13); L5 |
| r500 | 54/101; 9 (3-24); L3 | 55/118; 13 (7-24); L33 | 103/254; 11 (3-27); L11 | 130/455; 6 (2-11); L4 |

- **She doesn't follow the swarm.** Her team's units are a median 23 to 33 steps from her start from r100 on; she's at 7-17.
- **She keeps moving.** Small queens (mean length under 5), 50-round windows from r50, all maps: different tiles per window,
  median: aAah 30, larp 35, dev 25, us 10. Windows spent on 8 tiles or fewer: 13%, 16%, 21%, **us 41%**; windows that range
  more than 10 tiles from their first tile: 46%, 60%, 40%, us 16%. At length 12+ everybody travels (85-87%, 43-49 tiles).
- Portals: the queen crosses 0.36 (aAah), 0.26 (larp), 0.00 (dev, one crossing in 275 games) and 0.18 (us) times a game.
- **No guard ring.** Per living-queen round:

| phase | own heads within 4 / within 8: aAah | larp | dev | us | enemy heads entering 4 steps per 100 rounds: aAah / larp / dev / us | their opponents (aAah's / larp's) |
|---|---|---|---|---|---|---|
| r50-99 | 1.0 / 3.2 | 1.1 / 3.7 | 0.9 / 3.0 | 0.7 / 2.9 | 2.2 / 1.8 / 2.2 / 1.7 | 3.9 / 2.5 |
| r100-199 | 1.2 / 3.9 | 1.6 / 5.1 | 1.0 / 3.4 | 0.8 / 3.3 | 1.6 / 1.3 / 1.6 / 1.3 | 4.9 / 2.4 |
| r200-299 | 1.4 / 4.2 | 1.5 / 5.2 | 0.6 / 2.6 | 1.0 / 3.9 | 1.1 / 1.3 / 1.5 / 1.5 | 3.2 / 2.4 |
| r300-399 | 1.3 / 4.1 | 0.8 / 2.9 | 0.4 / 1.7 | 0.4 / 1.8 | 0.9 / 0.8 / 1.1 / 1.2 | 1.8 / 2.5 |

  The units within 8 steps are 7-11% of the team at r100-199 and 3-8% later; of the heads within 4 steps about 20% are still
  there ten rounds on before r200 (aAah 22%, larp 17-20%, dev 18-19%), fewer later. A fed queen has less company: larp 0.5 / 1.7 at r400+.
- **How near home, by map** (share of her living rounds within 10 steps of her start, r150-249):

| | Thermopylae | Autarky | Around UNSW | Australia | Maze | Slithery | Islands | all maps |
|---|---|---|---|---|---|---|---|---|
| aAah | 67% | 54% | 12% | 14% | 79% | 65% | 68% | 40% |
| larp | 14% | 86% | 40% | 42% | 97% | 76% | 79% | 60% |
| dev test 1 | 99% | (2 games) | 8% | 10% | - | 80% | 25% | 52% |
| us | 0% | 90% | 12% | 12% | 92% | 98% | 7% | 66% |

## 2. When an enemy head approaches
An "approach" starts when an enemy head comes within 5 walking steps of her head and ends when it leaves, dies, or she dies.
Rate per 100 queen rounds: aAah 1.8, larp 1.6, dev 2.2, us 1.7 (aAah's opponents 4.6, larp's 3.0). Queens of length 2-3:

| ending | aAah (714) | larp (662) | dev (791) | us (937) | our opponents (2,319) |
|---|---|---|---|---|---|
| intruder leaves, both alive | 73% | 73% | 79% | 63% | 81% |
| an ally rams the intruder | 8% | 11% | 6% | 4% | 5% |
| intruder moves into an ally's head | 5% | 4% | 2% | 2% | 2% |
| intruder dies on a body or alone | 3% | 2% | 2% | 1% | 1% |
| **queen dead** (by it / walked into it / other cause during the approach) | **12%** (5/1/6) | **9%** (6/0/3) | **11%** (7/0/4) | **30%** (17/3/10) | 11% |

- **Her own move is the same everywhere.** Share of a small queen's moves that increase the distance to the nearest enemy
  head, at distance 1 / 2 / 3 / 4 / 5: aAah 89 / 88 / 78 / 73 / 61%, larp 98 / 88 / 84 / 80 / 63%, dev 100 / 90 / 87 / 74 / 59%,
  us 95 / 91 / 90 / 81 / 66%. Ten rounds after an approach begins she's a median 4-6 tiles away (us 6). But the enemy head is
  at distance 1 or 2 in **23%** of our queen's threatened turns (1,156 of 5,098); aAah 12%, larp 8%, dev 5%.
- **Allies don't defend her on purpose**: rams on the intruder are 4-11% of endings, bodies 1%.
- **Room decides the ending.** Room = tiles within 5 walking steps of her tile on the empty map (61 in the open). Small
  queens, r50-299, first approach after 10 quiet rounds, dead within 10 rounds:

| room | top three (680 episodes) | everyone but us (1,770) | us (412) | share of small-queen rounds there: top three / us | deaths per 100 rounds there: top three / us |
|---|---|---|---|---|---|
| 25 or fewer | 35% of 49 | 37% | 60% of 10 | 12% / 11% | 0.30 / 0.37 |
| 26-40 | 19% of 176 | 19% | 33% of 159 | 28% / **60%** | 0.30 / 0.25 |
| 41-55 | 11% of 248 | 12% | 16% of 117 | 36% / 20% | **0.16** / 0.61 |
| 56-61 | 14% of 207 | 14% | 24% of 126 | 24% / 9% | 0.26 / 0.68 |

  Read both right-hand columns together. Their queen is safest per round in open ground; ours is safest in the 26-40 rooms
  (the hide blocks, where only 0.49 approaches per 100 rounds arrive against 1.08 and 2.58 in the open), and in the open she
  meets heads 1.3 to 2.4 times as often as theirs and dies more per meeting. Totals: 0.37 deaths per 100 small-queen rounds
  for us, 0.24 for the three teams. Tiles with 4 exits against 3: aAah 8% v 17% dead per approach, larp 12% v 30%, us 23% v 35%.
- Enemy pressure is what predicts death, allies nearby don't: a small queen with no enemy head within 8 steps during
  r100-199 is dead by r300 in 4-8% of cases (us 18%), with one in 25%+ of rounds in 33-44% (us 68%); grouping by own heads
  within 8 gives no consistent trend (6+ heads around her: aAah 6%, larp 9%, dev 24%, us 40% dead). Distance from start matters too: alive at r100 and 20-29 steps out, dead by r200 in
  27-50%; within 4 steps, 0-23% (aAah 0 of 12, us 8% of 25).

**How queens die** (all lengths):

| | aAah | larp | dev test 1 | us |
|---|---|---|---|---|
| dead / games; round quartiles | 85/191; 100 / 159 / 257 | 92/190; 101 / 151 / 297 | 158/275; 93 / 152 / 273 | 404/554; 89 / 176 / 315 |
| rammed by an enemy head | 64 | 72 | 131 | 313 |
| died on her own move (of those, zero free neighbours) | 21 (15) | 20 (19) | 27 (23) | 89 (64), 2 more on an enemy body |
| ... into an enemy head / an ally's body | 5 / 0 | 1 / 2 | 0 / 0 | 24 / 29 |
| her length when rammed: 2-3 / 4-7 / 8+ | 47 / 12 / 5 | 48 / 9 / 15 | 77 / 23 / 31 | 175 / 85 / 53 |
| killer length 2-3 / 4-7 / 8+ | 46 / 16 / 2 | 40 / 20 / 12 | 45 / 55 / 31 | 179 / 92 / 42 |
| kill on step 2 or later; needed a paid step | 40; 40 | 57; 54 | 114; 106 | 222; 208 |
| killer's Manhattan distance 10 / 5 / 2 / 1 rounds before | 10 / 8 / 5 / 5 | 11 / 8 / 6 / 5 | 13 / 10 / 7.5 / 6 | 10 / 7 / 6 / 4 |

All 967 rams in the four sets, by killer length and the step of its move that hit her: L2 step 1 in 85% (202 of 238); L3
step 2 or later in 80% (237 of 296); L4 step 3 or later in 83% (107 of 129); L5-7 step 4 or later in 84% (161 of 191);
L8-15 step 5 or later in 65% (73 of 113). At the start of the kill round the killer was more than 3 tiles away in 46%.
So killers use their whole reach, ceil(L/4) free steps plus L-2 paid ones, and a pearl on the way adds one.
Fed queens: at length 20+ at r300, dead by r400 in 6% (larp, 32), 8% (dev, 37), 18% (us, 17); from r400: 12%, 20%, 34%.

## 3. Feeding
Length of living queens, median (n alive):

| | r200 | r250 | r300 | r350 | r400 | r450 | r499 | reaches 8 after r30 (median round, q1-q3) | reaches 20 |
|---|---|---|---|---|---|---|---|---|---|
| aAah | 3 | 3 | 3 | 3 | 4 | 3 | 3 (54) | 71/191 (r171), at the unit cap, then shed | 15 |
| larp | 3 | 3 | 16 | 31 | 38 | 46 | 30 (55) | 95/190 (r261, 200-278) | 75 (r300) |
| dev test 1 | 3 | 7 | 9 | 9 | 11 | 13 | 11 (103) | 147/275 (r228, 159-262) | 84 (r285) |
| us | 3 | 3 | 3 | 4 | 5 | 4 | 4 (130) | 136/554 (r155) | 79 (r311) |

- Queens that peak at 20+: larp grows from a median r254 at **0.264 per round** to a peak of 57; dev from r212 at **0.239** to
  42.5; ours 0.16. Both shed afterwards by splitting at length 10+ (larp 8.8 length a game, dev 6.2), so end lengths in r500
  games are 27 and 14.5. Small re-splits (4 into 2+2) stop at a median r126 (larp), r129 (dev), r125 (aAah), r104 (us).
- The queen's pearls per game by source, r200-299 / r300-399 / r400-499, natural | own corpses: larp 2.3 | 9.4, 3.0 | 20.1,
  4.6 | 15.8; dev 2.6 | 9.2, 2.3 | 7.1, 2.7 | 8.9; aAah 2.8 | 1.3, 3.1 | 1.6, 2.6 | 1.8; us 1.2 | 1.2, 2.4 | 7.8, 2.0 | 4.6.

**Who feeds her.** Own non-queen units that die by their own doing within 3 steps of her head, from r200, per game:

| | aAah | larp | dev test 1 | us |
|---|---|---|---|---|
| deaths a game (and at 4-8 steps) | 2.6 (7.1) | **14.4** (7.8) | **10.7** (4.0) | 3.4 (7.7) |
| how | reverse into own neck, 100% | no action sent, 97% | no action sent, 99% | reverse into own neck, 100% |
| feeder length 2 / 3 / 4-7 / 8+ | 70 / 23 / 5 / 2% | 38 / 42 / 12 / 7% | 59 / 33 / 6 / 2% | 56 / 34 / 8 / 2% |
| distance at death 1 / 2 / 3 | 28 / 33 / 39% | 8 / 38 / 54% | 12 / 30 / 59% | 4 / 24 / 71% |
| pearls a game; queen eats; other own units | 3.8; 32%; 68% | 31.0; 51%; 46% | 16.5; **70%**; 28% | 5.5; 45%; 49% |
| rounds until eaten; feeder's age (median) | 1.8; 28 | 5.6; 30 | 3.2; 28 | 7.5; 19 |

Feeders are 28-30 rounds old, so they walk to her; they aren't children split off next to her. aAah's deaths near the
queen are its ordinary small-unit deaths, not a feed.

**Distance is the whole trick.** Queen's share of pearls from own-doing deaths within 8 steps (r200+), by the feeder's
distance from her head, and where each team's feeder pearls fall:

| distance | larp: queen's share (share of 9,354 pearls) | dev: (of 6,703) | us: (of 9,779) |
|---|---|---|---|
| 1 | 65% (5%) | 85% (8%) | 71% (1%) |
| 2 | 60% (23%) | 73% (20%) | 52% (8%) |
| 3 | 43% (35%) | 64% (39%) | 41% (22%) |
| 4 | 32% (13%) | 37% (9%) | 31% (**32%**) |
| 5 | 31% (8%) | 30% (7%) | 22% (**25%**) |
| 6-8 | 15% (16%) | 8% (17%) | 1% (12%) |
| all | 41% | 53% | 29% |

- Short feeders work better because a corpse drops a pearl on every second segment: within 3 steps the queen gets 67 / 76 /
  52% (larp / dev / us) of a length-2 feeder's pearls, 55 / 70 / 46% of a length-3's, 42 / 55 / 31% of a length 4+.
- **The other units near her don't hold back.** A unit within 4 steps of its queen with one of those pearls on a neighbouring
  tile eats it in 86% (dev), 79% (aAah) and 63% (larp) of turns after r250; ours in 29%. We already have the restraint they
  lack and still get less, because the pearl lies 4-5 steps from our queen and 7.5 rounds pass before anyone eats it. Their
  queen takes an adjacent feed pearl in 92% of turns (ours 77%); ours also skips adjacent natural pearls (eats 59%, 33% at
  length 2-3) where dev's small queen eats 95%.

## 4. The enemy queen
Share of a team's heads within 10 walking steps of the enemy queen's start tile at r100-199 / r200-299, next to the share of
the map that area covers (what an even spread would give), and the first round one of its heads is within 5 steps of it.

| map (area share) | aAah | larp | dev test 1 | us | first head within 5 steps: aAah / larp / dev / us |
|---|---|---|---|---|---|
| Thermopylae (4.3%) | 5 / 6% | 7 / 8% | 4 / 6% | 1 / 2% | 15/15 r91 / 15/15 r98 / 13/13 r135 / **17/23 r315** |
| Around UNSW (2.6%) | 1 / 1% | 1 / 1% | 1 / 1% | 0 / 0% | 13/13 r91 / 12/13 r128 / 18/18 r88 / **10/29 r219** |
| Australia (5.2%) | 4 / 5% | 3 / 5% | 4 / 6% | 0 / 0% | 12/12 r93 / 12/12 r113 / 28/28 r92 / **23/47 r243** |
| Autarky (12.3%) | 3 / 3% | 4 / 6% | (2 games) | 0 / 1% | 10/11 r74 / 9/12 r157 / 2/2 / 8/23 r197 |
| Islands (9.7%) | 7 / 7% | 6 / 7% | 1 / 1% | 6 / 5% | 12/12 r8 / 11/11 r36 / 23/23 r181 / 44/46 r63 |
| all maps | 3 / 2% | 2 / 2% | 2 / 2% | 1 / 1% | 154/191 r87 / 133/190 r121 / 209/275 r134 / 305/554 r160 |

- **Not on purpose.** Their share near the enemy start is at or below the even-spread figure on every map (a little above
  on Thermopylae). They're there because they're everywhere; our units aren't on the 64x64 maps and Autarky. Their own
  opponents reach the top teams' start in 71/191 (aAah) and 80/190 (larp) games.
- **When and how enemy queens die against them.** aAah's opponents: dead in 163/191, round quartiles 110 / 156 / 233, 126
  rammed (killer L2 37, L3 31, L4-7 44, L8+ 14; 70 needed a paid step), 8 more walked into a head; she was a median 15 steps
  from her start. larp's: 143/190, 96 / 162 / 291, 115 rammed (L2-3 77), 72 paid. dev test 1 against us: 206/275, 87 / 150 / 315.

## 5. End states
Cells = games (the team's wins). "Both alive" lists longer / equal / shorter queen.

| team | games, W-L | theirs alive, opponent's dead | both alive | both dead | theirs dead, opponent's alive |
|---|---|---|---|---|---|
| aAah, all | 191, 140-51 | 91 (91) | 15 (6): 0 / 6 / 9 | 72 (43) | 13 (0) |
| aAah, 56 unselected focus-map games | 49-7 | 37 (37) | 2 (0) | 16 (12) | 1 (0) |
| larp, all | 190, 139-51 | 72 (72) | 26 (15): 8 / 7 / 11 | 71 (52) | 21 (0) |
| larp, 56 unselected focus-map games | 48-8 | 24 (24) | 8 (5) | 21 (19) | 3 (0) |
| dev test 1 | 275, 194-81 | 80 (80) | 37 (29): 19 / 13 / 5 | 126 (85) | 32 (0) |
| us | 554, 207-347 | 68 (68) | 82 (31): 17 / 38 / 27 | 253 (108) | **151 (0)** |

Nobody has ever won from "our queen dead, theirs alive" in 968 games. On the seven maps the queen is alive at r200 for
aAah in 64/81, larp 68/87, dev 87/106, us 127/224; their opponents' in 36/81, 53/87, 42/106 (us), ours' 178/224.
Per map (aAah | larp | dev | us), "theirs alive, other dead" + "both dead" + "theirs dead, other alive", rest both alive:
Thermopylae 12+2+1 | 9+2+4 | 10+1+0 | 1+3+16; Autarky 5+5+1 | 5+6+0 | 2+0+0 | 2+7+13; Around UNSW 6+6+1 | 5+6+2 | 12+6+0 |
0+12+16; Australia 3+9+0 | 5+7+0 | 16+12+0 | 1+24+22; Maze 7+2+0 | 6+2+1 | - | 1+5+7; Slithery 8+4+0 | 5+3+0 | 5+1+3 | 3+5+17;
Islands 11+1+0 | 5+6+0 | 5+18+0 | 0+31+15.

## 6. The seven maps
Steps = from her start at r50 / r100 / r200 / r300. "Heads" = enemy heads entering 4 steps per 100 queen rounds from r100.
Block coordinates are for the queen whose start tile is the lexicographically smaller one; mirror for the other side.

| map (size, queens apart) | aAah | larp | dev test 1 | us |
|---|---|---|---|---|
| Thermopylae (64x64, 53) | 13-2. Out to 12-15 steps, back within 5 of start from r150 (60% of rounds). L2, unfed. Alive r200 12/14, rammed 3. | 11-4. Roams 15 / 27 / 28 / 16. Fed in 6/15 from r282, L27 at r400. Alive r200 11/14, rammed 6 (r192). | 12-1. **Never leaves the start block**: 96% of r50-149 within 5 steps in 13/13 games. 0.1 heads. L6 at r300, 12 at the end. Alive r500 11/12. | 3-20. Hide block (6,14), 19 steps out, room 45. 2.3 heads. Rammed 19/23 (r252). L2 all game. |
| Autarky (54x18, 54) | 8-3. 17 / 17 / 7 / 5. L2-3. Alive r200 7/9, rammed 5 (r104). Opponent's queen dead in 10/11 (r182). | 9-3. 17.5 / 23.5 / 7 / 10; 86% within 10 at r150-249. Alive r200 5/10, rammed 6 (r132). | 2 games. | 3-20. Start block (8,2), 61% of rounds. Alive r200 15/22, rammed 20/23 (r218). Our heads reach their start in 8/23. |
| Around UNSW (64x64, 62) | 9-4. Roams 17 / 24 / 23 / 21, 679 tiles in 11 games, no parking. L3-5. Alive r200 9/13, rammed 6 (r147). | 11-2. 11 / 12 / 10.5 / 17; most-used block (18,48), room 54. Fed early: 8 at r176 in 10/13, L28.5 at r400. Alive r200 10/13, rammed 7 (r336). | 18-0. Roams 15 / 20 / 19 / 23. L3-4. Alive r200 15/18, r500 10/16, rammed 3. 0.7 heads. | 4-25. **Parked at (10,45)** in 28/29 (room 34, 2 exits). 1.5 heads. Rammed 27/29 (r172). Alive r200 11/29. |
| Australia (64x64, 40) | 12-0 (9 with both queens dead). 23 / 30 / 35 / 27 out. Alive r200 6/12, rammed 8 (r116). 2.3 heads. | 11-1. 13 / 12 / 14 / 15; block (19,24), room 51. Fed in 6/12 from r268, L47 at r400. Alive r200 9/12, rammed 7 (r229). 2.0 heads. | 26-2. 17 / 25 / 27 / 32 out. L3-4. Alive r200 19/28, rammed 12 (r142). 1.9 heads. | 10-37. Hide block (31,7), room 39. **5.8 heads**. Rammed 41/47 (r134). Alive r200 10/47. |
| Maze (48x24, 46) | 7-4. 8 / 6 / 8.5 / 8; 12 own heads within 8; 0.1 heads. L2-4. Alive r500 8/10. Both losses with her alive: shorter queen. | 9-5. 4.5 / 6.5 / 5.5 / 6.5. Fed in 14/14: 8 at r263, 20 at r293, 46.5 at r400, 59.5 at the end. 101 feeder pearls a game. Alive r500 10/13. | none | 4-11. 5 / 4.5 / 6 / 4.5. Fed: 51 at r400, 91 at the end. 0.7 heads. **Rammed 9/15 (r375) while long**; alive r500 3/15. |
| Slithery Fight (63x27, 80) | 11-2. Block (2,24), 38% of rounds. L2-5.5. Alive r500 9/11, rammed 3. | 12-2. Roams 12 / 27 / 9 / 15. Fed in 13/14: 8 at r260, 54 at r400, 84 at the end. 87 feeder pearls, 52% hers. Alive r500 10/13. | 19-3. Block (2,24) for half of r50-249 in 18/22. Fed in 18/22: 8 at r237, 43.5 at r400, 58 at the end. 63 feeder pearls, 71% hers. Alive r500 18/22. | 6-38. Block (2,24), 65%. L7-10. 19 feeder pearls, 33% hers; 6.5 at the end. Alive r500 22/44, rammed 18 (r413). **Both alive in 19, shorter in 17.** |
| Islands (56x40, 23) | 12-0. 12 / 16 / 6 / 9.5. Alive r200 9/9. Opponent's queen dead in 12/12 (median r112). 2.8 heads. | 10-1. Home: 79% within 10; block (12,7), room 50. Fed in 7/11 from r257, L46 at r400. Alive r200 6/10, rammed 5 (r101). 1.8 heads. | 18-5. L9.5 by r100 (her only early long queen). 4 / 10.5 / 20 / 13.5. Alive r200 19/23, r500 5/23, rammed 16 (r363). | 11-35. Block (10,13), room 30, 3 exits. **5.6 heads**. Rammed 33/46 (r195). Alive r200 19/45, r500 0/43. |

What each row says for us:
- **Thermopylae**: our far block draws 23 times the traffic dev's queen sees on her start tile. Part of that is us: none of
  our heads comes near her until r315. aAah's queen also sits there from r150 (room 52, alive at r200 in 12/14), but its
  opponents reach that tile in only 4 of 15 games, so no sample shows the block holding against a team that arrives by r135.
- **Around UNSW, Australia, Islands**: no top team parks. larp stays within 15 steps of start (82%, 72%, 97% of r150-249) on
  open tiles; our three blocks have rooms 34, 39 and 30, and on Australia and Islands sit on a route (5.6-5.8 heads).
- **Slithery Fight**: same block as dev and aAah, and our queen lives to r200 in 42/44. The games are lost on length.
- **Maze**: feeding already works; the long queen is rammed late, 9 times in 15 against larp's 3 in 14.
- **Autarky**: queens die for everyone (top teams alive at r200 in 12/19). They win by killing the other queen; we don't arrive.

## 7. Rules to implement, by expected value
1. **Feeders die at 1-2 steps, not 4-5.** *Condition:* round 220 or later (dev starts at r212, larp at r254); I'm a
   non-queen unit of length 2 or 3 (at 4+ split first); my queen's head is within 2 walking steps; no enemy head in my view.
   *Action:* die there. *Queen:* an own-corpse pearl within 3 steps outranks every other target, natural pearls included.
   Don't add restraint for bystanders, ours already skip 71% of those pearls. *Evidence:* section 3 distance table: 43-85%
   of pearls reach the queen from 1-3 steps (dev 64-85%), 22-37% from 4-5, and 57% of ours fall at 4-5 (dev 15%, larp 21%).
   *Worth:* Slithery Fight alone has 17 of 44 games lost as "both alive, ours shorter"; fed queens grow 0.24-0.26 a round.
2. **Lunge radius for the queen.** *Condition:* an enemy head of length L in her 7x7 view. *Action:* never end her move
   within R = ceil(L/4) + L - 2 walking steps of it (L2: 1, L3: 2, L4: 3, L5: 5, L6: 6, L7: 7), plus 1 if a pearl lies on
   its path; among the moves that pass, take the one whose tile has the most tiles within 5 steps. *Evidence:* 967 rams:
   80-84% of kills by L3, L4 and L5-7 units come on step 2+, 3+ and 4+; 46% start more than 3 tiles away; our small queen
   has a head at distance 1-2 in 23% of threatened turns (theirs 5-12%) and dies in 30% of approaches (theirs 9-12%).
   km14 added lunge reach as a threat for our units: check that the queen uses this radius and the pearl bonus.
3. **Never box her.** *Condition:* choosing the queen's move, or any allied move next to her. *Action:* the queen rejects
   a tile that leaves her fewer than 2 free neighbours when another legal tile exists; allies treat the four tiles around
   her head as walls unless rule 1 applies. *Evidence:* 89 of our queen's 404 deaths are her own move, 64 of them with zero
   free neighbours: ally body 29, own neck 35, enemy head 24. The three teams together: 2 ally bodies and 6 enemy heads in
   335 deaths. Boxed deaths happen to them too (15-23 each), so this buys the 53 that are ours alone.
4. **Open home zone instead of a pocket** (known maps; test per map before shipping). *Condition:* queen of length 4 or
   less from r30; `room5(tile)` precomputed. *Action:* wait only on tiles with room5 of 41+ and 4 exits, inside a leash of
   15 walking steps from her start, and change block after every approach; with a head in view and room5 under 41, move
   toward larger room5. First candidates: Around UNSW around (18,48), Australia around (19,24), Islands around (12,7),
   Thermopylae the start block (15,9). *Evidence:* room table in section 2 (11-14% dead per approach in 41+ rooms against
   19-35% below, for the top three and for everyone else); larp's numbers on those maps in section 6. *Against it:* our
   own queen dies less per round in her 26-40 rooms (0.25) than in the open (0.61-0.68), so this only pays once rules 2
   and 3 cut the per-approach deaths. The local hide tests against km6 (`t34_hide`, `t35_hide2`, see `gen_qhide.py`) chose far
   corners on Hive, Devil, Around UNSW, Queen Of Spades and Whale Song; on the server that Around UNSW block lost her in 27/29.
5. **Send two to four units to the enemy queen's start** (unverified: no top team does it deliberately). *Condition:*
   known map, or known symmetry so that her start is the mirror of ours; r60-250; enemy queen not known dead; I'm a
   length-2/3 unit with id mod 16 == 0. *Action:* walk to her start tile, sweep the tiles within 10 steps, lunge when she's
   in reach. *Evidence:* she's within 10 steps of her start for 40% (aAah), 60% (larp), 52% (dev) of r150-249, and 99% for
   dev on Thermopylae, 65-80% for all three on Slithery, 79-97% on Maze; our heads get there in 50/99 games on the 64x64
   maps at r219-315 (theirs 138/139 at r88-135). "Theirs alive, ours dead" is 151 of our 554 games with 0 wins; "both dead"
   is 253 with 108.

Not a rule: a guard ring (nobody has one, and own heads within 8 steps don't predict survival consistently), a queen hunt in
the top teams' sense (there is none), and a longer queen before r200 (length 4-7 at r100 dies no less than 2-3).

## 8. Not determined
- Whether aAah or larp changed builds after 12 Oct 3:45 PM EDT. Only 14 of their games (ours, 13 Oct) are newer.
- Cause and effect in the room table: queens may sit in open ground because their team already controls it.
- Everything about dev test 1 is against our builds only; its Thermopylae queen meets 0.1 heads because we never come.
- How feeders find the queen (they're 28-30 rounds old and die 2-3 steps from her; sonar use wasn't decoded).
- Why dev test 1's queen died to "no action" 20 times (8 on Athena at length 6-17) and why its fed queen sheds length.
- Per-map cells rest on 11 to 15 games for aAah and larp; W-L in the older 112 + 122 games is biased toward losses.
- Nothing here was built or run locally, and nothing was uploaded or challenged.

## 9. Rerun (from `/Users/devsingh/Developer/UNSW_Battlecode`; 2 worker processes; cache in `work/top_oct13/queen/cache/`)
```
python3 work/top_oct13/queen/fetch_extra.py           # done: 112 picks in extra.json; prints them and stops (--more adds games)
python3 work/top_oct13/queen/run.py aaah larp dev us   # qsim.analyze per game, about 10 min for 968 games
python3 work/top_oct13/queen/report.py where,pattern,guard,events,react,qdeath,growth,splits,feeders,qeat,opp,hunt,fate,recipe [aaah|larp|dev|us] [--map "Islands"]
python3 work/top_oct13/queen/extra.py all              # hazards: flight, mobility, home, company, length
python3 work/top_oct13/queen/geo.py                    # room size against deaths per approach (section 2)
python3 work/top_oct13/queen/misc.py                   # feed share by distance, lunge steps, feeding start per map
python3 work/top_oct13/queen/dwell.py                  # busiest 5x5 blocks per map;  nearstart.py: time near start;  area.py: section 4 baseline
```
Printed tables from this run are in `work/top_oct13/queen/out/`.
