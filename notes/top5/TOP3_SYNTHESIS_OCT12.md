# Top 3 on the 31-map pool: what they share and what we take (12 Oct 2026)

Three replay studies, each 112 to 126 ranked games since 10 Oct on all 31 maps, with the scripts next to the data:
- larp stock zi balls (#1): `notes/top5/LARP_OCT12.md`, `work/top3_oct12/larp/`
- forgot to mention (#2): `notes/top5/FTM_OCT12.md`, `work/top3_oct12/ftm/`
- aAah (#3, Qualifier winner): `notes/top5/AAAH_OCT12.md`, `work/top3_oct12/aaah/`

All "us" numbers are our qf1 build (before km1). Per-map rows in the three notes rest on 3 to 6 games.
Caveat from the aAah study: `notes/tools/replay_sim.py` counts every starting dragon 1 too long until its first split,
so early lengths and "first split at L" in our older notes are 1 too high (a "start length 5" queen starts at 4).

## What all three do

| | larp | FTM | aAah | us (qf1) |
|---|---|---|---|---|
| ranked record since 10 Oct | 1005-345 | 854-349 | 805-261 | |
| against us | 17-3 | 7-3 | 22-3 | |
| queen split 4 -> 2+2 in round 0 (starts of 4+) | 75 of 84 | 98 of 98 | 80 of 85 | 30 of 455 |
| queen length to about r200 | 2-3 | 2 | 2-3 | 5 at r100 |
| queen distance from spawn | 10-15 | 12, then 5 from r150 | home side, no portals | 17 at r100, 28 at r150 |
| queen fed | from r250, median 20 by r400 | from about r204, 29 of 117 end at 30+ | never | only on Portals / Maze |
| queen alive at r500 | 56 of 122 | 49 of 117 | 32 of 64 | about 1 in 10 |
| units at r100 (big maps) | 43 | 54 on Atlantis | 50 | 30 |
| wins by elimination | 38 of 79 | | 38 of 75 | |
| looks for the enemy queen | no | no | no | no |

1. **The queen is a length-2 unit near home from round 0.** She keeps splitting at 4, so she also produces workers.
   She is rammed about half as often as ours (an enemy head is in her view in 10% of her rounds, in ours 26%).
2. **Mass first.** Fifty units by r100, also on maps nobody had seen (aAah's Qualifier numbers equal their ladder
   numbers). In aAah's 25 games against us: 5.5 portal crossings before r50 against our 0.9, and 44% of the tiles
   visited by r100 against our 15%.
3. **Nobody hunts queens.** The enemy queen dies to ordinary small units in 55 to 60% of games (median r141 to r158,
   killer length 2-4, often a paid lunge). Our queen dies that way because she is long, far from home and seen often.

## Where they differ, and what it costs them

- **larp builds kings by local suicide from exactly r250**: a small unit with a longer ally in view dies where it
  stands (121 a game). King line at r300/r400/end 17/57/97 on ten big maps; ours 4/25/55 from similar totals.
- **FTM keeps two unit slots free.** They sit at 60-61 units, we at 63 in 48% of rounds. Our length-10+ dragons die
  boxed 15 times a game (theirs 5.5) and our longest dies that way 3.3 times a game (theirs 0.3), because the
  turn-around split needs a free slot.
- **aAah has no king and no queen plan.** With both queens dead at r500 they win only 14 of 32, and in 12 of the 18
  losses they held 62+ units. All four of their "longer queen" losses outside sealed rooms are to a long safe queen.
- **Sealed-room maps (Detention, Schooltime):** both queens sit at L3; the longest dragon decides. larp's queen dies
  when the team is at 64 units and she must split; aAah's pays a step and ends L2 against L3.

## What we take, in order

| # | change | flag | state on 12 Oct |
|---|---|---|---|
| 1 | Queen stays near home | `QUAL_QHOME`, `QHOME_OLD`, `QHOME_UNK` | live in km3/km4 on Whale Song, Troll Australia, Around UNSW and unseen big maps |
| 2 | Queen cut to 2 in round 0, re-split at 4 until r250 | `QHOME_SMALL=250` | built; local test running |
| 3 | Feed the home queen from the king seed round | `QHOME_CROWN` | built; local leash+crown vs leash: Troll Australia 5-1, Whale Song 2-4 (fed queens rammed at L43-61) |
| 4 | Two free unit slots | `SPLIT_MAX_UNITS=61` | local vs km4, 40 games: 19-21, but total length at r300 up 15 to 60% (Hive 464 vs 282); the extra mass does not reach the king yet |
| 5 | Local feeding from r250 | `LOCAL_FEED=250` | built; one smoke game was bad (27 vs 109 on Maelstrom); needs a proper run together with 4 |
| 6 | Earlier crown and feed (200 / 250) | `NEWMAP_KING_SEED/FEED` | local vs km4, 32 games: 12-20, kings shorter at the end on Athena and Metro; not shipped |
| 7 | Detention and Schooltime as a longest-dragon race | `QUAL_KNOWN` bit 3 + crowd | not started |

Rejected by the data: copying a queen hunt (none of the three has one), and aAah's "no king" (it loses them the
both-queens-dead games).
