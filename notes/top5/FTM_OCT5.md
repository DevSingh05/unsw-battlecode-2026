# forgot to mention (FTM, id 264): current play vs b3, 2026-10-05

Status: **PAUSED a second time, at about 01:20 UTC 6 Oct (21:20 EDT 5 Oct)**, on the user's request. Done: steps 1-2,
the harness fidelity check, and harness runs of PM_POR_EARLY and the five staged fixes on the FTM games (results
below). Not done: `show --debug` traces at the cited points, and the step-4 prototype (Portals queen box). Nothing in bot/
or variants/ was touched, nothing was submitted, no challenges, no Discord or browser. All my processes are stopped.
(My replay script `ftm5/chains.py` lacked a `__main__` guard, so it kept spawning processes; I killed its orphans,
pids 43826/43827. Add the guard before running it again.)

## Session 2 results (harness, sandbox, scratch `ftm5/v/<label>/<game>.json`)
- **Fidelity:** with the exact server zips (`--sub b3` / `--sub cm1`), all 61 games vs FTM rebuild IDENTICAL and
  **628,814 / 628,814 turns match**. bot/ with every flag off (cm1 rows with CROWD_MAPS=3) also matches 100% on all 61,
  so any change a flag makes below comes from that flag.
- **PM_POR_EARLY=1 (Portals, 7 games):** every game changes 361-449 turns, starting at r210-214. Most changes fall in
  r225-300 (non-queen moves and splits become feed moves), and wins change as much as losses (1160797 361,
  1164511 439). So it is a policy change, not a point fix. The harness confirms the mechanism (feeding starts about
  65 rounds earlier) but cannot score the outcome. The local test on 4 Oct (OWN_RANKED_OCT4.md R7) showed the
  blocker: the queen fed early gets boxed and sheds to death. **Not shippable alone.**
- **New verified mechanism on Portals: the queen box-and-shed chain (QBOX_K2).** Seen in 3 of 5 Portals losses vs FTM:
  - 1182688: L40 → 2 over r407-425.
  - 1151983: L41 → dead at r409. Their queen ended at L8, so with our queen intact this game is a likely **win**.
  - 1151507: L39 → 31 over r433-437.

  Geometry from the replays (`ftm5/box.py GAME SIDE ROUND`):
  - 1182688 r405-406: from (19,1) she steps W to (18,1). Its only open side leads N to (18,0). There N and W are kelp,
    S is her neck, and E is a portal into her own segment 7 at (13,13).
  - 1151983: at r385 she steps S into (22,13). Its only open side is the portal E to (9,1), the far side of the map.
    She then walks (9,0) → (8,0) → (8,1) and is boxed at r390.

  In both she has to take a portal step, which the park scores dead (`qparkScore`, PM_QP_PEN). It is the only move
  left, because the step before it entered a cell whose only non-portal exit was a dead end.

  Then `tryMove`'s trapped branch (main.cpp ~6963, `QBOX_K2 && amQueen() && bestD < 0` → `SPLIT 2`) sheds 2 per
  turn. Every child is stillborn (exits=0) and frees only the 2 rear tiles. Her head neighbour stays blocked until
  her length drops below that segment's index (7 in 1182688), so she loses about 33 length in 17 turns.
  *Not yet traced with `show --debug`* (the pause came first). Points to trace: 1182688 dragon q r404-407,
  1151983 q r384-390, 1151507 q r432-433.
- **PM_TD_PULL=2 (TD, 5 of 6 losses; 1160796 failed on a build-dir race, rerun it):** in all 5, the same opening
  decisions flip. Our non-queen (dragon 3) goes **S → W toward the centre at r0, 1, 2 and 12-18** (r3 S → N). Later,
  turns at r30-62 flip too (1182687 r37-41, r59-62). That is 14-24 changed turns per game; the queen never changes. The opening is deterministic, so these are the
  same 9-10 decisions in every TD game. There are no TD wins vs FTM to check "unchanged" against; UNDERSTANDING's
  check had 21/21 wins changing toward the centre. This is the cause in all 6 TD eliminations (FTM's non-queen reaches
  the centre at r45-50; ours at r55-60 by the top route).
- **QG_RAM=8 (Maze, 7 games):** 1133622 changes 22 turns at r325-398, 1160800 10, 1138664/1164998/1176048 1-3,
  1176685/1182690 0. Our queen's killer is an L3-5 FTM head in 4 of 6 losses: 1133622 r399 by L5 id 774,
  1160800 r392 L3, 1164998 r339 L3, 1182690 r466 L3. In 1133622 our L2 id 766 was at distance 1 from killer 774 at
  r347 and changes its move (E → N). Whether that is a ram is not traced. 1176685 is a pre-crown ally-box HitSelf
  at r299, and 1138664 is a pure queen race (92 v 20). The win 1176048 changes 3 turns.
- **QVAULT=3 (big open, 12 games):** the queen's vault-entry move flips in every Australia loss that has one:
  1133621 r34 W→E, 1164507 r36 S→E, 1165000 r62 EN→W. Slithery 1160798 also flips (r24 W→E, then r26 SPLIT 2
  instead of N). The one changed win is 1138229 r44 S→E; the queen died in that vault in the win as well.
  AUNSW/Islands are unchanged in all 6. 1151982 is unchanged (its r27 death has a different cause). **QVAULT=1**
  changes only Slithery 1160798.
- **QKILL_KING + QKK_FREE (all 61):** 1 changed turn (1176046 r416). Against FTM it almost never fires: their queen
  is either dead early (L2-4) or parked out of reach.

## Ranked fixes vs FTM (harness evidence as of the pause)
1. **PM_TD_PULL=2** (staged, `dgu/stage/PM_TD_PULL`). 5/5 TD losses flip at the same opening decisions; the queen is
   untouched. TD is 6/6 eliminations vs FTM. Scope: TD only. Risk: low (one map; the queen still random-walks out).
2. **QVAULT=3** (staged). 3/3 Australia vault entries and 1/1 Slithery entry flip, 1 win changes at the same kind of
   move, 6/6 AUNSW/Islands unchanged. Risk: the 4 Oct smoke had one Australia-A loss (see UNDERSTANDING).
3. **Portals box fix (to build): replace the K2 shed chain with one split of k = L - i**, where i is the index of
   her own segment next to the head. The child's tail is then exactly on that tile, so the tile frees next round:
   the queen keeps i segments and the rest stays on our team as an ally instead of 17 stillborn L2s. A second part
   is still unspecified: an entry guard against a cell whose only non-portal exit is a dead end. Expected: 3/5
   Portals losses change at the box turn; 1151983 is a likely flip to a win. Also a prerequisite for PM_POR_EARLY.
   Not prototyped yet.
4. **QG_RAM=8**: changes 2 of 4 Maze ram-death losses before the death. Not traced, low confidence.
5. **PM_POR_EARLY**: only after fix 3, and judged on the server (the harness cannot score it).
6. QKK_FREE: neutral vs FTM (1 turn in 61 games). Its case rests on other opponents.

## Next steps when resumed (supersede the list at the end of this note)
1. `show --debug` on the box points above. Get the score breakdown at the entry step, the code path in
   `qparkScore` / `tryMove`, and confirm the K2 branch.
2. Prototype fix 3 in `ftm5/bot/` (copy of bot/, flag default 0). Then verify all 61 games: the 3 box turns must flip,
   and every other turn must match. Expect 0 changes elsewhere, because the branch fires only when the queen has no legal move.
3. Rerun tdp on 1160796, then do the small-map eliminations (step 4 of the task).

## Data (all local, reusable)
- Scratch folder: `/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/ftm5/`
  - `games_264.json`: every FTM game from 22:08 UTC 4 Oct to 23:20 UTC 5 Oct (4556 listed). `g24.json` = completed
    games from 22:10, each tagged with our build (from `subs.json`, our upload times).
  - `team264.json`: FTM's team record and its 628-point rating history.
  - `sample.json`: the 85 games downloaded to **`replays/ftm_oct5/`**. That is all 51 vs b3, 10 of 20 vs cm1, and 8 each
    vs SSS, Vibing++ and dev test 1, spread over four time bins.
  - `rows.pkl`: per-game rows (an_top1.analyse) for the 85 new games plus the 99 Oct-3 baseline games
    (replays/top2: 68 FTM vs us (v44/v55/v60) and 31 vs VIB/SSS).
  - Scripts: `crawl.py`, `build.py`, `pick.py`, `dl.py`, `run_an.py`, `agg.py` (old-vs-new profile), `list.py`
    (per-game table), `qtrace.py MAP` (both queens every 25 rounds), `mass.py MAPS` (queen vs rest mass),
    `feed.py` / `feed2.py MAPS LO HI` (feed-death mass, distance to the queen, share of dropped pearls the queen eats).
  - `list_all.txt`: harness input, 61 lines (`id our_side build map W/L`). b3 is 19 W / 32 L, cm1 4 W / 6 L.
- The listing's `elo` field is the team's *current* rating, not its rating at game time. Don't use it for expectations.

## Did FTM upload a new build? Yes, by behaviour (the replays carry no bot names)
- Rating: about 2270-2300 for most of 4 Oct. Steps of 50-93 points within minutes start at 17:20-18:40 UTC 4 Oct
  (2321 → 2374 → 2412 → 2447). Swings like that come from a fresh upload's extra sigma or from switching the active
  submission. Other steps: 10:26 UTC 5 Oct (+44), 14:35 UTC 5 Oct (-93 then back). Peak 2485 at 13:13 UTC 5 Oct, 2399 at 23:35.
  FTM probably toggles between builds.
- Behaviour changed between the Oct-3 sample and the new sample (FTM vs us):
  | metric | Oct 3 (n 68) | Oct 5 (n 61) |
  |---|---|---|
  | FTM queen reaches L20+: Portals | 0/6 | **7/8** |
  | same, Maze | 3/5 | **8/8** |
  | same, Trauma | 4/4 | 6/6 |
  | same, Autarky | 1/5 | 3/4 |
  | queen is the longest at the end | 12% | 26% |
  | FTM queen length at r300 (median) | 0 | 10 |
  | FTM moves by an L5+ queen | 2852 | 5144 |
  | Tower Defense at r75, FTM units / mass | 2-4 / 5-8 | **9-11 / 23-28** |
- Unchanged: the queen splits at r0-1 (48% of games), the queen stays L2-4 on most maps, 1-2 step kills (90%),
  feeding by NoValidAction suicides (168/game), about 60 head-on kills per game.
- Where the rating came from: 920 ranked games in the window, **190 of them vs us (FTM 123-67)**, the largest single
  source. Our ranked loop kept matching FTM with test builds: h1 30, k2 20, s1 25, l1 15, ms1 20, cm1 20, b3 50.
  vs VIB, FTM was 11-19 ranked.

## What FTM does now (profile)
- **Queen on king maps (new):** on Portals the queen goes to the x 0-3 strip next to its spawn at r25-50 and stays
  there as an L3 until about r200. Feeding starts around **r225-275** (L7 at r250, L13-19 at r275-300, L30+ by r350,
  L58-73 at r500). Almost all of its mass ends in the queen (end total 62-86, of which the queen is 60-73).
  Maze: crowned from about r250, L40-60 at r275-300, L88-94 at r500.
- **Tower Defense opening (new):** the non-queen (id 2) leaves at r30 along the south route (5,14) → (12,11) → (13,9)
  and is in the centre field at r45-50. Ours reaches the centre's north edge (18,1)-(20,0) at r55-60, about 10 rounds
  later. The first 36 rounds are identical in every game, so the race is deterministic. FTM ate 29-31 pearls by r80
  (12 in the centre) vs our 13-27. The FTM queen stays L2-3 at home and is alive in 6/6.
- **Small maps:** these are still elimination games. vs b3: Stripes 1-5 (our wins), Default 2-3, PD 2-1, Devil 2-2,
  Trophy 2-1 (cm1 included), QoS 0-2, TD 6-0, Autarky 3-0.
- **Feeding efficiency:** this is *not* the difference. On Portals r250-500 both sides lose about 450-600 mass in
  feed suicides (median L2). The share of dropped pearls the queen eats is 0.17 for us and 0.20 for FTM. Feed deaths
  within 2 tiles of the queen: 3% for us, 13% for FTM.

## Our losses vs FTM (b3 + cm1, 38 losses), grouped (not yet verified in the harness)
1. **Portals queen race, 5 losses** (1151507, 1151983, 1182688, 1182917, 1133619). Total mass is even at r300
   (us 74-80, FTM 84-101). FTM's queen is already L10-20 at r300; ours is L3 because `KING_V2 v2("Portals",250,360,300)`
   gives feedStart=300. Our feed then burns the rest in r300-350 (rest 71 → 31, queen only 3 → 16). The queen
   reaches L30 about r375-400 against FTM's r325-350, and ends at 19-54 vs 60-73. In both Portals wins (1160797,
   1164511) FTM's queen died (r303, r206), and the feed pattern was the same.
   *Lever:* `PM_POR_EARLY` already exists in bot/ (seed 210 / feed 235 / split-stop 310, default 0). It failed one
   local test on 4 Oct ("fed-early queen boxed, sheds to death") and was never server-tested. New angle: FTM's
   timing (feed from about r225) is now the reference, and it beats our r300 crown 5-0 when both queens live.
2. **Tower Defense, 6 eliminations** (1160796, 1164999, 1176049, 1176684, 1182687, 1183195). This is the centre race
   above, then our L5-6 queen is rammed at r68-131. It matches UNDERSTANDING's TD cause. The staged `PM_TD_PULL=2`
   (scratch dgu/stage/PM_TD_PULL) should be run on these 6 games first.
3. **Maze, 6 losses** (1133622, 1138664, 1160800, 1164998, 1176685, 1182690). Our crowned queen is rammed at
   r392-466 or HitSelf at r299, and FTM's queen is now crowned too (L88-94). Run the staged `QG_RAM` on them.
4. **Big open, early queen self-death, 5 losses**: Australia 1164507 / 1165000 / 1133621 (HitOtherBody self at
   r45-66, the portal vault), 1151982 (r27); AUNSW 1176046 (r76); Slithery 1160798 (HitSelf r30). Run the staged
   `QVAULT` / `QVAULT1` on them.
5. **Small-map eliminations, about 12**: Trophy 1151504 / 1138226, PD 1165002 / 1176050, Devil 1176682 / 1138667,
   Stripes 1176047, Autarky 1182919 / 1183194, Default 1165001; plus queen tiebreaks Autarky 1151984 and
   Default 1160799. Not studied yet.
6. Others: Trauma 1164510 (queen race 44 v 42), Islands 1182691, AUNSW 1183197.
- Wins vs FTM: Stripes 5/6 even though our queen always dies at r13 (HitSelf, the vault pump design), Default 3,
  QoS 2, Devil 2, Portals 2 (their queen died), Maze 1176048 (their queen died at r498), AUNSW 1176683, Islands 1183196,
  Trauma 1182920 (our queen 53 v 45). Not yet studied for "what we did right".

## Next steps when resumed (in order)
1. Baseline harness: `VPJ=3 python3 <dgu>/builder/vp.py ftm_b3 bot <ftm5>/list_all.txt`. vp.py takes columns
   `id side sub map`, and cm1 rows need `-D CROWD_MAPS=3`, which vp.py adds. Better: run with `--sub b3` / `--sub cm1`
   so the zip is exact. Confirm 100% match.
2. Portals (cause 1): for the 5 losses and 2 wins, `show GAME --dragon <feeder> --round 235..300 --debug` on our
   non-queen units near the queen. Then `verify` with `-D PM_POR_EARLY=1`. Count how many r235-300 decisions become
   feed moves in losses, and whether wins change only after r210. Decision points to cite: the r250 / r275 / r300
   turns of 2-3 feeders per game. Then look into why the fed-early queen "boxed" locally (qparkScore vs coil): FTM's
   parked queen is fed in an open strip.
3. TD (cause 2): `verify` with the PM_TD_PULL stage on the 6 TD losses. Cite the r30-45 non-queen turns
   (id 3 / the second starter) that go N/E along the top instead of toward the centre.
4. Maze / big-open (causes 3-4): rerun the QG_RAM and QVAULT stages on the new games and count flips at the cited rounds.
5. Prototype in `<ftm5>/bot/` (copy of bot/) only if a new flag is needed. For Portals, try PM_POR_EARLY with KS 225 /
   FS 250 and a feeder distance gate, then re-run the harness. Finally, fill in "verified causes" and "ranked fixes"
   (flips / unchanged counts, scope, risk) here.
