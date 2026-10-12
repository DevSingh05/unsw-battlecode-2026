# forgot to mention (FTM, id 264) on the 31-map pool, 10-12 Oct

Written Mon 12 Oct, 3:45-4:45 PM EDT (all times EDT). Read-only: public game listing, public replays, one leaderboard call. No uploads,
challenges, local games, Discord or browser. Scripts and data: `work/top3_oct12/ftm/` (section 7). Builds on
DEEP_FTM_OCT8.md and TOP4_SYNTHESIS_OCT8.md and covers only what is new. Rounds are r0-r499.

## 0. Short version
- **No sign of a new build since 8 Oct** (section 2). #2 at 2539. Ranked since the pool change 854-349 (71%): new maps
  378-162 (70%), old maps 476-187 (72%).
- **They keep two unit slots free for long dragons; we fill them with L4 foragers.** In r150-400 we are at 63 units in
  48% of rounds, FTM in 3%. Our longest dragon dies boxed 3.3 times a game, theirs 0.3 (section 3.5).
- **Their queen is L2 from round 1, home by r150 and fed from r204.** When she is the final king (26 of 84 round-limit
  games) FTM wins 23. Our queen is 28 steps from spawn at r150 and alive at r500 in 41 of 425 games; hers in 49 of 117.
- **Atlantis 36-2 ranked:** queen at spawn, 54 units at r100 against 10, opponent eliminated at r195-208. Nothing to
  copy on Trolley Problem (8-23 and 14-18 ranked; we beat them there) and nothing new in queen hunting.

## 1. Data
- Listing: 3,560 completed FTM games, 10 Oct 5:34 AM to 12 Oct 3:40 PM EDT; 1,203 ranked, 2,357 unranked (890-1467).
- Sample: **126 ranked replays** (79 W, 47 L), 3-6 per map on all 31 maps, 69 on the 14 new maps, picked by outcome
  (1-2 losses per map, wins against the strongest opponents first, 18 extra wins against teams rated 2100-2350).
  Opponents: larp 31, WHQ 14, aAah 11, Cutlery 10, us 10 (every game), horse 9, SSS 9, others 32.
- Comparison, same script: **our 455 ranked qf1 games** of 10-12 Oct (14 new maps and Around UNSW; "ours" below; no
  km1/km2 games), and the 137 FTM games against us of 6-8 Oct.

## 2. What changed since 8 Oct: nothing we can measure
- Openings: the queen's first 8 actions repeat a 6-8 Oct opening on 14 of 18 map-sides that have games in both periods.
- Queen: L3 or less on 94% of her turns in r10-199 then, 95% now on old maps, 94% on new maps; first L10 at r248 / 236 / 256.
- Fighting, old maps: steps of the killing move 1/2/3/4/5+ were 50/38/8/2/2%, now 54/33/9/2/2% (new maps 45/32/15/4/3%).
- Splits: non-queen 4>2 was 70%, now 68%. Ranked win rate per 6 hours stays between 67% and 76%.
- Two maps moved: Maelstrom 21-5 before 11 Oct 10:24 PM EDT and 3-9 after (22 units at r100 against 62), Caution 19-11 and 3-9.

## 3. What they do
### 3.1 Per map (medians; "steps" = walking distance of the queen from her spawn; F/O = FTM / its opponent)
| map | ranked W-L | n | queen steps r100 / r200 | queen alive r500 (her L) | first L10 (games) | units r50, r100 F/O | first round at 60+ units | longest r300 / r500 | ours (qf1): queen steps r100, alive; units r100, first 60+; longest r300 / r500 |
|---|---|---|---|---|---|---|---|---|---|
| Athena | 38-16 | 4 | 3 / 4 | 1/4 (45) | 252 (2) | 42/50, 61/62 | 71 | 44 / 66 | 15, 0/31; 63, 73; 27 / 57 |
| Atlantis | 36-2 | 6 | 2 / 1 | 4/6 (2-4, not fed) | 285 (1) | 17/12, 54/10 | 81 (4 of 6) | 12 / 17 | 38, 4/30; 7, never; 4 / 14 |
| Caution | 22-20 | 4 | 10 / - | 0/4 | - | 2/2, 6/5 | never | 3 / 10 | 12, 12/36; 4, never; 4 / 8 |
| Detention | 29-9 | 6 | 1 / 1 | 6/6 (3, sealed room) | - | 24/24, 62/60 | 84 | 42 / 90 | 1, 30/30; 32, 154; 21 / 50 |
| Ezam | 21-18 | 4 | 8 / 6 | 2/4 (131, 7) | 218 (3) | 18/16, 46/30 | 117 (3 of 4) | 48 / 57 | 5, 10/20; 32, 156; 10 / 55 |
| Hive | 29-9 | 4 | 17 / 1 | 0/4 | 242 (1) | 30/59, 47/62 | 114 (3 of 4) | 14 / 56 | 14, 0/23; 63, 53; 20 / 52 |
| Maelstrom | 24-14 | 4 | 10 / 6 | 1/4 (53) | 374 (1) | 14/53, 22/62 | 325 (3 of 4) | 4 / 53 | 14, 1/31; 26, 219; 12 / 42 |
| Metro | 29-5 | 4 | 3 / 8 | 0/4 | 216 (1) | 32/22, 61/50 | 77 | 31 / 96 | 11, 0/42; 41, 122; 20 / 56 |
| Ouroboros | 41-5 | 4 | 18 / 1 | 0/4 | 344 (1) | 47/34, 61/52 | 55 (3 of 4) | 36 / 87 | 18, 0/26; 51, 111; 29 / 56 |
| Thermopylae | 32-11 | 6 | 1 / 1 | 4/6 (46, 42, 22, 17) | 314 (4) | 18/17, 22/23 | 159 (1 of 6) | 10 / 42 | 48, 10/33; 25, 240; 5 / 28 |
| Troll Australia | 29-5 | 6 | 28 / 4 | 2/6 (52, 6) | 331 (2) | 22/18, 58/50 | 98 (5 of 6) | 45 / 58 | 15, 0/31; 24, 178; 12 / 42 |
| Trolley Problem | 8-23 | 5 | 44 / 39 | 3/5 (45, 42, 41) | 225 (3) | 5/4, 17/18 | 225 (2 of 5) | 14 / 41 | 62, 2/27; 18, 166; 6 / 42 |
| Trolley Problem (Buffed) | 14-18 | 6 | 44 / 38 | 2/6 (36, 5) | 234 (3) | 5/5, 24/15 | 182 (3 of 6) | 10 / 28 | 50, 0/30; 18, 165; 6 / 36 |
| Whale Song | 26-7 | 6 | 30 / 11 | 3/6 (80, 71, 61) | 266 (4) | 12/12, 39/42 | 129 | 25 / 60 | 22, 1/33; 35, 147; 14 / 50 |
| Around UNSW | 22-16 | 6 | 7 / 4 | 2/6 (52, 46) | 257 (4) | 32/40, 52/60 | 126 | 26 / 44 | 22, 1/32; 57, 98; 13 / 49 |
| Slithery Fight | 42-8 | 6 | 14 / 5 | 4/6 (117, 94, 75, 68) | 242 (5) | 53/49, 61/62 | 60 | 27 / 80 | no replays |

"First round at 60+ units" is the median over the games that got there (all unless noted). All 69 new-map games: units at
r25 / r50 / r100 / r200 / r300 = 8 / 18 / 43 / 61 / 59 (opponents 7 / 16 / 39 / 60 / 60), total length 100 / 197 at r100 / r300 (92 / 209).

### 3.2 Queen
- **Split.** On every map where she starts at L4 or more she splits in round 0 (98 of 98 games), is L2 from round 1 and
  splits 2 off whenever she reaches L4 (359 splits 4>2). Ours: no round-0 split in 425 games outside Detention; L5 at r100.
- **Where.** Outside sealed rooms: median 12 steps from spawn at r25-100 (beyond 20 steps in a third of games), 8 at
  r125, **5 at r150-200** (63% within 8 steps at r150). Ours (70 games): 17 at r100, 28 at r150, 23 at r200.
  Alive at r200: FTM 70 of 117, ours 24 of 70. She used a portal in 8 of 126 games (Caution 4, Stripes 3, Ezam 1).
- **Feed.** First round at L6: r204-211 in 20 of 50 games, median r218, a median 6 steps from spawn. Of 73 queens alive
  at r260, 50 were fed; the other 23: sealed rooms 9, Atlantis 4, small maps 9, one other. She eats about 12 own-team
  pearls per 100 rounds from r200, 2,055 of her 2,521 from units that died by passing no action.
- **End.** Alive at r500 outside sealed rooms: 49 of 117 (L10+ 33, L30+ 29), opponents 34; against teams rated above
  2350, 25 of 82 (opponents 28). Ours 41 of 425 (L10+ 18). She is her team's longest in 32 of the 58 games she survives.
- **Deaths** (68): 60 rammed by an enemy head, 5 boxed (all r100-199), 3 head-ons she moved into, none into her own or
  an ally's body. Ours (384): 299 rammed (218 of them at L5-6), 48 own body, 30 ally body, 7 other.

### 3.3 How their games are decided (126 games; wins / losses, then new maps and old maps)
- Elimination 24 / 18 (new 7 / 9, old 17 / 9); median last round 198 in wins, 206 in losses.
- Longer queen 28 / 9: theirs alive and the opponent's dead 17 / 0 (new 12, old 5); theirs dead and the opponent's alive
  0 / 6 (new 4, old 2); both alive 11 / 3 (new 4 / 0, old 7 / 3).
- Longest dragon, with both queens dead or both L3 in sealed rooms, 26 / 19 (new 17 / 15, old 9 / 4). Total length 1 / 1.
- Our 252 qf1 losses: longest dragon 127, our queen dead and theirs alive 94, elimination 24, other 7.

### 3.4 Splits, losses and kings
- **Split sizes** (non-queens, 417 splits a game): 4>2 68%, 5>3 8%, 5>2 5%, 6>4 4%, 6>2 3%, 7>2 3%, 7>5 2%. In 91 splits
  a game the child takes all but 2: a turn-around, where the stub at the boxed head dies and the bulk leaves by the tail.
- **Length lost per 100 rounds, new maps:** own body 0.3, ally body 3.6, no action 168, head-ons 116. A boxed or feeding
  FTM unit passes no action and ours moves into a body, so only the sum compares: per game on six capped maps FTM 1,204,
  ours 1,427 (18 games each). The difference is which dragons die (3.5), not how much.
- **Longest dragon** (84 round-limit games) at r200 / r300 / r400 / r500: 6 / 26 / 37 / 54 (opponents 12 / 20 / 32 / 48).
- **Final king.** The queen in 26 games: L10 at r222, L20 at r272, 21 / 40 / 50 / 56 at r300 / r400 / r450 / r500. Another
  dragon in 58 (32 won): its line starts at r289, is L10 at r358 and 2 / 14 / 32 / 52. Ours (392 games): starts r254, L10 at
  r332, 3 / 20 / 30 / 45. On average 64% of what their final king eats is own-team corpses.

### 3.5 At the unit cap (r150-400; Athena, Detention, Trolley Problem, Around UNSW, Ouroboros, Troll Australia, Metro, Hive)
| | FTM | ours (qf1) |
|---|---|---|
| share of rounds at 60 / 61 / 62 / 63 units (24 games each) | 15% / 38% / 18% / 3% | 2% / 5% / 18% / 48% |
| splits made with 62+ units alive (12 games each, six of the maps) | 255, 216 of them by L10+ parents | 2,679, 105 of them by L10+ parents |
| splits by L10+ parents with 60+ units alive, per game | 68 | 8.8 |
| L10+ dragons dying by own body, ally body or no action, per game | 5.5 (74 length) | 15.4 (265 length); 300 of 369 with 62+ units alive |
| the same for L20+ | 0.5 (18 length) | 3.7 (109 length) |
| the dying dragon was the team's longest, per game | 0.3 | 3.3 |

FTM's L4 foragers stop splitting at 61-62 units (their 4>2 splits by units alive before: 1,132 at 60, 371 at 61, 15 at
62), so a boxed long dragon always has a slot for its turn-around split. Ours split up to 63, the non-queen limit.

### 3.6 Enemy-queen kills
- An FTM unit rams the opponent's queen in 71 of 126 games (56%): median r166, quartiles r117-319; 9 before r100, 33 in
  r100-199, 9 in r200-299, 20 from r300 (victim L10+ in 10 of those). She was a median 17 steps from her own spawn.
- Killer: median L3 at impact (L2 18, L3 32, L4 6, L5-8 9, L9+ 6); the killing move has 4 or more steps in 27 of 70.
- **No dedicated hunters:** 3.7% of FTM units are within 6 tiles of the enemy queen in r10-100 (their opponents 4.2%,
  ours 3.1%). We ram the opponent's queen in 52% of games (median r226) with the same lunges (4+ steps in 50%).

### 3.7 Map notes
- **Atlantis.** Queen L2 at spawn, never through a portal, not fed; 15-23 units through portals by r100. In the four
  wins the opponents (rated 2136-2484) had 4-15 units at r100. Both losses: their own economy (5 and 18 units).
- **Trolley Problem, both.** Their worst maps: eats are about 600 or about 2,600-3,200 a game. Queen fed from r204-243.
- **Thermopylae.** The queen stays on two tiles next to her spawn at L2 for 200 rounds (6 of 6 games) and is fed from
  r242-270. Units and eats equal ours (22 v 25 units at r100, 482 v 532 eats).
- **Detention.** The longest dragon decides (5 of 6; once 104 v 104 and total length). All 16 of our losses are the same.
- **Whale Song.** Queen roams (30 steps at r100), comes back and is fed at r207-264. **Slithery Fight.** She sheds from
  L25 to L3 by r25 and is fed from r210-232. **Around UNSW.** Fed at r219-298, killed late at L24 and L53 by horse and larp.
- **Troll Australia.** 58 units at r100 (ours 24). Both losses are to larp (longest 203 and 215).

### 3.8 The ten games against us (11 Oct, our build qf1): FTM 7, us 3
- Their wins. Longest dragon: Australia 61 v 10, Detention 77 v 39, Ouroboros 87 v 30 (units at r100 52 v 27, 62 v 20,
  61 v 22). Queen: Troll Australia, theirs alive at L52, ours rammed r269; Portals, both alive, 81 v 51. Elimination:
  Autarky r371 (our queen rammed r76 at L6), Caution r211.
- Our wins: Schooltime longest 58 v 54, Caution elimination r145, Trolley Problem longest 57 v 23 (eats 3,290 v 593).

## 4. How this differs from our bot
- **Unit slots.** `w.unitLimit` is 64 minus `QBOX_RESERVE` (1) for non-queens. The growth split (main.cpp about line
  6360) and the trapped turn-around split (about line 7230) both test `units < w.unitLimit`; `SPLIT_MAX_UNITS` is 64.
- **Queen.** `QG_MIN` 5 keeps her at L4-6, there is no home rule on unseen maps, and the king seed is r250 and the feed
  r300 (`UNK_KING_SEED`, `UNK_KING_FEED`) against their r204. `QUAL_QHOME`, `QHOME_UNK`, `QHOME_CROWN` exist and are off.
- **Already the same:** split size 4>2, king turn-around splits (3.1 per final-king line, theirs 4.8), lunges at queens.

## 5. Candidate changes, by expected value
1. **Leave two slots for long dragons: `SPLIT_MAX_UNITS=61`.**
   - Evidence: table 3.5. Longest-dragon games are half of our results (147 wins, 127 losses).
   - Maps: all where we reach 60 units (Athena, Hive, Metro, Ouroboros, Detention, Around UNSW, Whale Song, Troll Australia).
   - Reuse: the define gates only the growth split. The split paths near lines 6194 and 6331 test only `units < w.unitLimit`.
   - Check: unranked series on Athena, Detention, Hive, Metro, Ouroboros (qf1 77-75 there, 59 of 75 losses by longest).
     `bigdeaths.py` and `caphist.py` on the new replays: L10+ boxed deaths from 15 to about 6 a game, rounds at 63 units
     under 5%, longest at r400 and r500 up.
2. **Queen home by r150, crowned and fed from r200.**
   - Evidence: 3.2. We lose 19 of 51 queens between r100 and r150 (FTM 13 of 96) and do not feed her before r300.
   - Maps and our losses by "our queen dead, theirs alive": Whale Song 16 of 22, Around UNSW 15 of 21, Trolley Problem
     12 of 17, Buffed 10 of 18, Thermopylae 8 of 14, Ezam 6 of 10, Troll Australia 4 of 20; Slithery not measured.
   - Reuse: `QUAL_QHOME` / `QHOME_UNK` with `QHOME_CROWN`, seed and feed at 200 (`QUAL_QPARK_SEED/FEED` or `UNK_KING_*`).
     FTM's numbers for the settings: no leash before r100, full by r125-150, radius 8.
   - Risk: QPARK_UNK and QK_BIG lost on the server earlier. This differs by letting her forage first.
   - Check: unranked on Whale Song, Thermopylae, Around UNSW, Slithery: queen alive at r200 and r500, her steps from
     spawn at r150 (`qhome.py`), her length at r300 and r500.
3. **Known map on the capped Qualifier maps, together with 1:** `QUAL_KNOWN` bits Athena, Detention, Hive, Metro,
   Ouroboros (0x1A9). Known doubled our eats locally but lost it again at the cap. On four of the five (not Hive) FTM
   reaches 60 units at r55-84 and holds 31-44 longest at r300 (ours 20-29). Check: the same series, known on against off.
4. **Thermopylae: queen stays at spawn from round 0.** Evidence: 3.7; FTM 32-11, ours 19-14 with the queen 48 steps away
   and 8 of 14 losses to a dead queen. `QUAL_QPARK` bit 9 needs the map known, and known lost 1-3 locally on economy, so
   try `QHOME_UNK` with a small radius first. Check: unranked on Thermopylae only.
5. **Atlantis: finish by elimination.** FTM's four sample wins end at r195-208. First count how km2's Atlantis wins end;
   if they wait for r500 with an L4 queen, gate `LH_FINISH` or `EQ_HUNT` on Atlantis.
- Not candidates: the L2 queen floor (tested 8 Oct, no gain), queen hunting, anything from their Trolley Problem play.

## 6. Not determined
- Whether a new build was uploaded (their submissions are not visible), and whether any play on the new maps is
  map-specific code: the Thermopylae and Atlantis parks could be either.
- Why their queen survives more: her size, her position and the team around her cannot be separated from replays.
- Why Maelstrom and Caution turned against them on 12 Oct, and why their Trolley Problem economy has two modes.
- Whether `SPLIT_MAX_UNITS=61` saves our long dragons; they may still fail the tail-exit test. km1/km2 are not in the
  comparison set, and per-map FTM samples are 3-6 games.
- One slip: I removed a Python cache file of my own script (`__pycache__/select*.pyc`) instead of archiving it.

## 7. Rerun (from `/Users/devsingh/Developer/UNSW_Battlecode`)
```
python3 work/top3_oct12/ftm/crawl.py && python3 work/top3_oct12/ftm/pick.py    # listing.json; sample.json + up to 125 replays
python3 work/top3_oct12/ftm/mk_samples.py && python3 work/top3_oct12/ftm/analyze.py   # rows.json; then `analyze.py old`, `analyze.py ours`
python3 work/top3_oct12/ftm/tables.py         # 3.1 and 3.3; report.py prints every section; lunge.py for section 2
python3 work/top3_oct12/ftm/caphist.py        # 3.5, with capsplits.py, bigdeaths.py and allybody.py
python3 work/top3_oct12/ftm/qhome.py          # 3.2 (`qhome.py ours 5` for ours); timeline.py <gameId> <A|B> for one game
```
