# aAah (id 454) turn by turn: their decision rules vs ours (8 Oct, DEEP_AAAH)

**Status: done (15:35 EDT 8 Oct).** The analysis was paused at 12:45 and resumed at 14:50. The prototype unseen check is
in section 5: **GOV50 pooled .491 and .531 on two seed bases, .511 combined. Neutral, do not ship.** Nothing in bot/ or
variants/ was changed, nothing was submitted, and there were no challenges.

This builds on TOP4_AAAH_OCT8.md and does not redo it. Data:
- the 88 replays in `replays/top4_aaah/`;
- a full per-action trace of every dragon on both sides: pre-state (pearls by BFS and the BFS-optimal first steps,
  enemy and ally heads, exits) and outcome (steps, free/paid, eats per step, kills, death, split k);
- the turn-by-turn narratives of 12 games (queen + 4 mid-size units, r0-120 and r250-270).

"US" = our b4 code (games classified 19891 in which_submission.json: 36 open, 21 narrow). "open" = AUNSW, Australia,
Islands, Slithery, QoS, weakhold, Default, Maze, Schooltime, Portals. Unless marked, aAah numbers use all their games.

Caveat up front: aAah very likely has map knowledge on the ranked maps. On Australia (1274149) an L3 walks 10 rounds
straight to the portal vault from r6, before anything in it could be seen. So their known-map play is not all generic.
Only the rules below that hold on every map class should be expected on unseen maps. Our "US" numbers are known-map
b4 too. I profiled our blind play separately (section 4).

## 1. Their policy as rules (counts)

**R1. Splitting: a unit-count governor, k = L-2, and an escape when boxed.**
- **Head boxed** (no free neighbour): split 97-100% of turns at every length and unit count
  (open: 15,462 turns, 99%). The bulk (k = L-2) leaves from the tail, and the 2-stub left at the head dies
  (parent dead within 5 rounds in 46% of L5+ splits, mostly HitSelf).
- **Below ~50 units**, a non-queen L>=4 splits in 40-55% of turns.
  - After eating at L4: 64-66% (open, exits >= 1).
  - Without eating: 15-29%.
  - So it is not an instant split: units often reach L5-6 even early.
- **At 50-55 units** the hazard is 5-13%. **At 56-63 units it is 1-5%** (open: 392k of 421k L4+ turns are at 56+ units).
  Above ~50 units the surplus goes into length.
- **Split sizes** (open, 28,860 splits): child = L-2, parent keeps 2, in 77% (narrow 93%). Top (L,k): (4,2) 9431,
  (5,3) 3799, (6,4) 1821, (7,5) 1345. The child (old tail, reversed) carries the bulk away.
- **Big units with few units on the map unpack each turn.** Example: Australia, an L10 at 15-18 units splits
  k=2, 2, 4 on consecutive turns.
- **Viability.** 4% of L4 children are born with 0 exits; ours: 19%. Their child is dead within 5 rounds in 15% of
  cases; ours in 32% (8% of ours HitOtherBody, theirs 0%).

**R2. Steps: all free steps when moving on, rarely paid.**
- **All free steps (s = F)** (open, all games):
  - L5-7: 71% of moves (ours 43%);
  - L8-12: 63% (ours 37%);
  - with no pearl in view: 72% / 63% (ours 38% / 31%).
  - Steps per turn: L5-7 1.73 (ours 1.43), L8-12 2.14 (ours 1.77), L13+ 2.84.
  - Example: AUNSW 1364970 id99 L8 at 57-61 units roams 2 tiles a turn for 50 rounds without splitting.
- **Paid moves:** 1-2% of moves.
  - About 15-23% of them are kills (all mutual).
  - The rest are 2-step escapes or approaches by L3-4 units, plus "eat then sprint": an L2 whose first step eats can pay
    the second step.

**R3. Pearl choice: greedy nearest visible pearl, mildly coordinated.**
- First step on a BFS-shortest path to the nearest visible pearl:
  - when they are the closest head: 88% (L2-3) / 88% (L4+); ours 79% / 72%;
  - when an ally head is closer: 69% / 77% (they mostly leave it);
  - when an enemy head is closer: 78% / 83% (they contest it).
- Ate this turn when the pearl is "theirs": L4+ 73% (ours 56%).

**R4. Exploring with nothing in view.**
- Straight on 46-52% (random 34%).
- Toward out-of-view pearls within BFS 12: 58% (random 51%).
- **No ally repulsion:** the first step maximises ally distance 55% (random 50%); ours 62%.
- Away from own spawn: no bias.
- Their spread comes from more units and faster mid-size movement, not from a dispersion rule:
  - coverage: heads visit 42% of map tiles by r100 (ours vs them 21%, our blind self-play 30%);
  - allies within 3 per unit, r<150: 0.88 (ours 1.64).
- In lane mazes this fails. On TD 1364969 their two L2s wander in the home box with no pearl in BFS 12 until r80.

**R5. Threats.**
- **Flee:** they move away from heads within 4 at about the same rates as we do (L2-3: 50-88% away). Both bots flee.
- **Split-escape:** mid-size units next to an enemy head split. L5-7 at distance 1: 39%; L8-12: 17%; L13+: 20%.
- **Kills:**
  - per game (open): theirs 40, ours 43;
  - 59% of their kills use paid steps, 34% of ours;
  - **836 of their 2427 open kills take 3-5 steps; ours: 2 of 1542.** That is the kamikaze lunge.
  - Victims include 145 L8+ units and 30 queens.

**R6. Queen.**
- **r0:** the L4 starting queen splits k=2 at r0 in 35 of 61 open games.
- **r<100, split hazard per turn:** L4 30%, L5 25%, L7 20%. Ours: about 1%, and 81% at L7 (keep >= 3, grow to 7, split 2).
- **r100+:** 2-5% per turn. Median length 3 all game; 12.9 eats per game (ours 9.4).
- **Where:**
  - own half 74% of turns;
  - nearest enemy head 8.4-10.1 tiles;
  - 2.7-4.1 allies within 6, rising late (ours: similar, 3.7-3.8).
- **Alive** (open, vs us): r100 82% / r200 64%. Ours 69% / 44%.
- Queen rules look similar on paper. Her survival comes mostly from their mass lead, not from a different rule.

**R7. Portals.**
- L2-3 units cross 21 portals per 1000 steps (ours 8-9). L4 cross 9, L8-12 cross 2.6.
- 45-58% of crossings happen with an enemy head within 4 (fleeing through). Only 8-9% have a pearl in view.

**R8. Late game.**
- Units sit at 58-64. Growth goes into length: longest 20-45 by r400.
- Deliberate backward suicides by L2-3 units: 5.8 per game in r100-299 and 10.5 at r300+ (ours 7.7 and 22.4).

## 2. Our rules side by side (b4 code)
| rule | b4 | aAah |
|---|---|---|
| growth split | any non-queen L>=4, k=SPLIT_CHILD=2. Unthreatened, below 64 units, no viability check. Hazard after eating at L4: 93-96%. Still 43% at 60-63 units | k=L-2. Below ~50 units: ~65% after eating, 15-29% otherwise. At 56+ units: 1-5%. Boxed: 99% |
| pearl value | BFS sum of gamma^d (0.82) × value, ×0.25 if another head is closer, plus PEARL_ROUTE on unknown maps | greedy: nearest visible pearl they are closest to (88%) |
| free steps | FREE_STEPS beam only for L>=5. Needs +0.5 over the 1-step. FS_VIS vetoes endpoints next to unseen tiles, so 3-step straight runs mostly fail | all F free steps in 63-72% of mid-size moves |
| crowding | CROWD_PENALTY 0 on unknown maps (3.0 on QoS/Portals/Trauma/Schooltime/Australia) | no repulsion rule either |
| threat | flee; tryRam at distance 1-2 only; no paid lunges beyond 2 | flee; split-escape; 3-5 step paid lunges |
| early queen | keeps >= 3 before QS_FROM=100; splits at L7 | splits at L4-7 with a 20-30%/turn hazard; L2-3 |

## 3. The differences that matter on open maps (b4 games, per game)
1. **Crowding deaths (the biggest term of the r100 gap).** By r100 we lose 54 units (about 123 length) and they
   lose 31 (about 71). Breakdown:
   - HitSelf: ours 35, theirs 24;
   - HitOtherBody: ours 12.5, theirs 0.9;
   - boxed (0-exit) deaths by r150: ours 83, theirs 45;
   - allies within 3 per unit: ours 1.64, theirs 0.88;
   - stillborn children (0 exits at birth): ours 19%, theirs 4%.

   The r0-99 net change in length is +59 for us and +138 for them. Deaths account for ~52 of that 79 gap, eats for ~26
   (182 vs 208). Caution: the direct fix (SPLIT_DEFER, SPLIT_VIABLE) already lost (s1: r100 length ratio 1.82 → 1.20).
   They avoid crowding by *where* units are (spread, more coverage), not by blocking splits.
2. **The unit governor and the mid-size phase.** From ~50 units they stop voluntary splits, so every unit grows. Mid-size
   units take all free steps (L5-7 71% vs our 43%) and harvest the whole map:
   - eats in r100-199: theirs 329, ours 234;
   - units: theirs 43, ours 26;
   - total length at r200 in our losses: theirs 173, ours 32.
3. **Greed plus lunges.** They head for their own nearest pearl 88% of the time (ours 72-79%). 34% of their kills come
   from 3-5 step paid lunges, which we cannot do or see.

## 4. Our play on unknown maps (local, b4 vs b4 blind, 7 open maps, seed 971500)
- Units per team: r50-99 about 27, r100-199 about 40.
- Allies within 3: 1.22.
- Coverage by r100: 30%.
- In own half: 80% at r0-49, 72% at r50-99.
- Stillborn children: 17%. Child dead within 5 rounds: 29%.

The crowding and stillborn pattern is the same as on known maps, and blind we stay even more at home.

## 5. Prototype (built, not evaluated)
- `work/top4b/aaah/bot/` = copy of bot/ (QF1 state, md5 e33fe07b…) plus two flags. Both default off and act only when
  `w.neverKnown()`.
  - `UNK_GOV=N`: the non-queen growth split is allowed only while units < N, or when the head is boxed. A boxed L>=5
    unit splits k=L-2 if its tail has an exit.
  - `UNK_GOV_FSM=m`: on such maps, a free multi-step path only has to beat the 1-step by m (default FS_MARGIN 0.5).
- **Smoke test** (blind, GOV50 as A vs b4, seed 971500): Islands W, Slithery W, AUNSW L, Australia L, all decided at
  r500.
  - Traced: the rule works as written. Units hold at 50-52 (boxed splits push it to 60-65 on Slithery and AUNSW).
  - L5+ units at r200: 9-14 (b4 3-9). Total length at r200-300 is ahead on 3 of 4 maps (e.g. AUNSW r300 276 vs 237).
  - **Both losses were on the longest-dragon tiebreak**: AUNSW 50 vs 87, Australia 51 vs 56. Spreading mass over
    mid-size units starves b4's single fed king.
  - aAah wins by elimination and queen tiebreak, not by longest, so this half of their design does not transfer to our
    win conditions by itself.
- **Unseen check** (`python3 tools/unseen_eval.py "work/top4b/aaah/bot:-DUNK_GOV=50" --base variants/b4 --seeds 1 --jobs 4
  --sets real,realhold,blind17`, run from the project root):

| seed-base | real | realhold | blind17 | pooled |
|---|---|---|---|---|
| 971000 | 38.0/80 = .475 | 40.0/80 = .500 | 34.0/68 = .500 | 112.0/228 = **.491** |
| 976000 | 44.0/80 = .550 | 43.0/80 = .537 | 34.0/68 = .500 | 121.0/228 = **.531** |
| both | 82/160 = .512 | 83/160 = .519 | 68/136 = .500 | 233/456 = **.511** |

  - Every 95% interval covers .5 (e.g. 971000 real [.369, .583]). The two seed bases disagree by .04, which is noise
    at n=228.
  - **Verdict: neutral against b4; not a ship candidate.**
  - UNK_GOV_FSM was skipped, per the rule "only if GOV50 >= .53 on both". The opponent is b4, not aAah, so this only
    tests for regressions; it cannot show the gain against aAah's mass race.
  - MIDSIZE ms1, a related idea, lost on the server (-5.8 pp).
- **If anyone revisits it:** pair it with a king-feeding rule, so the longest-dragon tiebreak is not given up. The
  governor alone only moves mass from the king into mid-size units.

## 6. Mass accounting (corrected; b4 games, open, per game)
| | eats r0-99 | length lost in deaths r0-99 | paid-step cost r0-99 | eats r100-199 | lost r100-199 | total r100 | total r200 |
|---|---|---|---|---|---|---|---|
| US (b4) | 181.8 | 138.7 (own move 122.2, rammed 16.5) | 2.4 | 234.1 | 235.7 | 64.2 | 61.9 |
| aAah | 208.2 | 89.0 (own move 71.6, rammed 17.5) | 13.3 | 328.6 | 202.7 | 121.0 | 191.6 |

- By r100 the gap is about 57 length: deaths about -50 for us, eats about +26 for them, paid steps -11 for them.
- From r100-199 we gain nothing (-2); they gain about +97 gross, +68 after paid steps.
- The run.py label bug (vs-top games counted as ours) is fixed: local games are now detected by `meta['src']`.
  `out_econ_mass_fixed.txt` replaces `out_mass.txt`.

## Files (all in `work/top4b/aaah/`)
- deep.py: tracer (deep/ = v1, deep2/ adds ally positions).
- agg.py and run.py: analyses (split split2 move econ threat queen pearl disp explore terr child box misc mass).
- narr.py, plus narr/<gid>.txt (12 games).
- timeline.py.
- local_games.py, deep_local.py, local/ (blind replays and traces).
- out_*.txt: the outputs.
