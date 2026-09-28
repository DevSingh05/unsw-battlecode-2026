# Queen Of Spades (ranked map id 7): map-specific plan

28 Sep 2026. Research and local prototype only. `bot/` has not been changed.
- Tested module: `notes/maps/queen_of_spades_proto.hpp`, a drop-in replacement for `bot/maps/queen_of_spades.hpp`. Its defaults are the best tested settings.
- Analysis scripts: `notes/tools/qos/*.py`. They write pickles to the session scratchpad path in `S=`; edit that path before rerunning.

## 1. The map

25x35 with xy symmetry: B's tile is `(24-x, 34-y)`. Every tile is walkable; the blank tiles in `showmap` just never spawn pearls.

**Starts.**
- A: (5,11) facing S (id 0) and (2,9) facing N (id 2).
- B: (19,23) (id 1) and (22,25) (id 3).

**Food.** There are 32 "spade" tiles with gap [1,50] (mean 25.5), 410 tiles with gap [1,1000], and 433 that never spawn. Each spade room gives about 0.63 pearls a round. The whole open field gives about 0.8 a round, split between both teams. **The spade room is about 60% of a team's food.**

**The rooms are sealed by kelp. The only way in is one portal edge.**
- Bottom room: x6-11, y31-33. Reached from the edge (3,3)|(4,3), next to A's start.
- Top room: x13-18, y1-3. Reached from (20,31)|(21,31), next to B's start.
- The rooms are symmetric. Below, everything is in A's frame; the top room is the same with the rotation applied.

| move | lands on | next move is forced |
|---|---|---|
| (4,3) W → | (8,33) facing W | N to (8,32) |
| (3,3) E → | (9,33) facing E | N to (9,32) |
| (8,33) E → | (4,3) | N, E or S are free |
| (9,33) W → | (3,3) facing W | N to (3,2) |

- Inside the room there is a 2x6 block: rows 31-32, x6-11.
- Pockets one tile deep: (6,33) and (11,33) are spade tiles; (7,33) and (10,33) are entered from row 34 and never spawn.
- **Vision does not pass through the portal.** A dragon at (4,3) cannot see (8,32). A dragon inside cannot see (4,3) or (3,2).
- The map has 16 pocket tiles in total, each one deep: (4,20), (5,31), (6,33), (7,33), (10,33), (11,33), (12,3), (12,12), (12,22), (12,31), (13,1), (14,1), (17,1), (18,1), (19,3), (20,14).

## 2. Our real games (v7, ch5, ch6, ch8: 36 games, 19-17)

- 11 of the 17 losses were eliminations, at r147-455. The other 6 were lost on length at r500, with kings of 3-21 against 12-30.
- **Losses are decided by r100 on unit count.** At r100 we had about 5 units against their 12 (at r150: 4 against 16).

In losses, rounds 0-100, per game:

| | us | them |
|---|---|---|
| deaths in our own room | **15.6** (37 length) | 6.2 |
| spawn eats in own room | 26.9 | 18.1 |
| spawn eats in the open field | **3.3** | 14.6 |

- We eat plenty. The pearls come back as corpses of our own dragons: 17.8 corpse eats in the room.
- Almost all our HitSelf and ally-body deaths before r200 happen in the rooms and at the door.
- 92% of the dying dragons had 0 free neighbours, and every one of them was length 2-3.

**Death map, r0-150, deaths per game.** Us = losses and wins, top = top-25 winners, 21 games from `notes/replays/permap` and `notes/replays/kings`.

| tile | us | top winners |
|---|---|---|
| (8,33), the IN landing | **7.4-7.9** | 2.1 |
| (9,33) | 3.2-3.9 | 0.8 |
| (3,3) and (4,3), outside the door | ~3.8 | 0.7 |
| pockets (6,33) and (11,33) | 5.2 | 4.7 (same as ours, so not the problem) |
| corners (6,31) and (11,31) | 3.5 | 1.8 |

**Why the door kills us.** From `qos_doordeath.py`, all 36 games, per game:
1. **Blind entry into an occupied landing: ~6.** A dragon comes in (4,3)W→(8,33) or (3,3)E→(9,33). It is forced N, and (8,32) or (9,32) holds an ally body or head.
2. **Head-on crossing at the door: ~3.** An insider leaves (8,32)S→(8,33)→E and meets an ally waiting at (4,3), often an ally head about to enter.
3. **Split children born on a door tile: ~3, all at age 0.** Their neck is across the portal. The child can't see the neck, so `trail` has only the head and moving back through the portal looks free. We counted 110 such deaths in 36 games (`qos_doordeath.py` tail).
   - This is a general bug and probably also hits Schooltime and Portals.
   - Children born on door tiles: we have 8.2 a game and 67% die within 3 rounds; top winners have 3.3 and 24% die.

**Traffic.** Door crossings in r0-150, per game:

| | entries | exits |
|---|---|---|
| us | **19** | 16 |
| top winners | **6.7** | 8.9 |

Our room is a net sink of units. Top winners' room is a net source: children born inside walk out.

**Opening.** Top winners send only the (2,9) starter into the room (it arrives about r9-14). In 14 of 21 games the (5,11) starter forages the open field. Ours sends both starters in, in 10 of 12 games.

## 3. How strong teams play it

- Winners' units at r50-100 are 12-31 (kings index). Their room residents are length 2-3 and split at 4.
- They keep 2-3 heads in the room: 0, 1, 2 or 3 heads 22%, 14%, 36% and 25% of the time. We have 9%, 14%, 34% and 33%, plus 9% with 4 heads.
- They also die in pockets about as often as we do. The pockets are not what separates us.
- They win on fewer door deaths, fewer entries and more open-field foraging.
- Kings on QoS only matter in the rare r500 games. There, winners grow a king from about r275-330 to 17-34 by r500.

## 4. Proposed behaviours (all in `notes/maps/queen_of_spades_proto.hpp`)

All coordinates are in A's frame; the code applies them to both rooms with `qosR(r,x,y)`.

**Q3, one-way doors and clear landing lanes (the core fix).** Implemented as `queenofspadesScore`:
- -150 for (8,32)→S→(8,33). That would mean leaving through the IN door, onto whoever is at (4,3).
- -150 for (3,2)→S→(3,3). That would mean entering through the OUT door.
- -30 for an insider stepping onto (8,32), the IN landing.
- -30 for anyone except the dragon just out of (3,3) stepping onto (3,2), the OUT landing.
- So traffic runs IN via (4,3)W→(8,33)→(8,32) and OUT via (9,32)→(9,33)W→(3,3)→(3,2).

**Q3b, entry spacing (`QOS_SPACING=4`, `QOS_SPACE_PEN=80`).**
- The override records the last round it saw another of our segments on (4,3).
- For 4 rounds after that, stepping onto (4,3) or taking the W step into the room costs -80.
- This stops a second dragon tail-chasing a first one into a blind landing. That was the case left over after Q3.

**Q4a, entry quota (`QOS_GATE=1`, `QOS_GATE_MOD=3`, pen 60).**
- The entry step (4,3)W costs -60 unless `id%3==0` or `units<=3`.
- That brings entries down to about 5 per 150 rounds, the top teams' level. The other dragons forage the open field.

**Q1, portal-neck guard (`QOS_NECK=1`).**
- -1000 for a move through our head's portal when `myLen>=2` and `trail.size()<2`. If the neck isn't visible, it is across that portal.
- Neutral in self-play (0.51) but logically right. It should go into `main.cpp` for all maps.
- Q2, no split while any of our segments is on a door tile (done by bumping `threatAt[myHead]`), was slightly negative: the reference beat it 0.59. **It is off.**

Rejected or neutral:
- Opener (the (5,11) starter stays out until r60): 0.55 against the reference.
- Spacing 3: 0.45. Spacing 6: 0.62 against spacing 4 without the gate, but 0.465 once the gate is on.
- Lane penalty 80 instead of 30: 0.50.
- Gate `id%2`: 0.64 against the spacing-4 candidate, where `id%3` scored 0.79.
- Against the spacing-4 + gate reference: gate `%4` 0.54, gate penalty 150 0.50, both neutral.

### Local results
Pool runs, QoS only, both sides.

| candidate | opponent pool | score | 95% interval |
|---|---|---|---|
| current bot (baseline) | v8, v10h | 49/100 | 0.39-0.59 |
| Q1+Q2+Q3 | v8, v10h | 77/100 | 0.68-0.84 |
| + spacing 4 | v8, v10h | 96/100 | |
| + gate | v8, v10h | 99/100 | |
| **final (Q1+Q3+Q3b+Q4a, Q2 off)** | v8, v10h, current bot | **117/120 = 0.975** | 0.93-0.99 |
| saved proto file | current bot | 46/50 | |
| Q2 alone, doors two-way | v8, v10h | 43/100 | |
| gate but no one-way | v8, v10h | 80/100 | |

- Head-to-head against the spacing-4 candidate: + gate 0.79 [0.70-0.86].
- Metrics against the current bot (12 games, `qos_cmpbots.py`):
  - door deaths per game 3.8 against 33.8;
  - room deaths before r150: 11.8 against 26.9;
  - units at r100: 10.4 against 4.5; at r200: 21.4 against 5.7;
  - entries 4.7 and exits 11.2 before r150, so the room now produces units.

**Caveat.** The whole pool shares our old door behaviour. The ladder is the real test: challenges on QoS against the teams we lost to (DIET CODE, Codehammer 40K, Hakimi, uhhhhhhhh, NeungzAI, Deer Park, usagi, Settlers of Battlecode, QgQ). The module only runs when the map is recognised as "Queen Of Spades". "QoS But She Ages" (id 8) has the same walls and could reuse it.

## 5. Next ideas (not tested)
- Late king for the r500 games: the QoS KING_V2 row is seed 330, split stop 420, feed 400. Winners have a king of about 17-34 by r500.
- Resident "farmer" on the 12-tile ring (6..11,31) + (11..6,32), splitting when its tail is on (9,32) so the child exits through (9,33) straight away.
- Move Q1 into `main.cpp` and measure it on Schooltime and Portals.
