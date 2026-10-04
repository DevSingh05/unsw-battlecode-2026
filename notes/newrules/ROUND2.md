# ROUND 2 synthesis: why we lose and what to fix next

Written 4 Oct ~02:50 UTC (3 Oct 22:50 EDT). Six analysts studied v61 and v69 server games; this page merges their results. Nothing in `bot/` or `variants/` was changed and nothing was submitted.

Scratch data and scripts for every lens: `/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r2/{top5loss,shouldwin,mazedevil,maps3,qtrace,stats}/`

## Overview

**Do first: take v69 down and re-upload identical `variants/v61`.** v69 (QEARLY_PEN) is 24-42 after 66 games, and the opponent-and-map-adjusted estimate is -12 to -20 pp against v61 (93-99% probability it is worse). The rank drop to about #12 at 2053 belongs to v69's own submission rating; v61's stored rating is 2187, which would be about #5. v69 also switches off the Stripes vault dive that separates our good Stripes builds (2086-2170) from our bad ones (1635-1977).

**What the six lenses agree on:**

- **We lose on the queen, not on fights.** Combat length lost, corpse pearls and queen rams are even against the top 5. In r500 games against the top 5 our queen was alive in 4 of 54 and theirs in 26.
- **Most of our queen deaths are self-inflicted.** 103 of 250 audited losses contain a shed chain (she is boxed, sheds 2 per turn, dies at L2-3). In 56 of those she would have won the queen tiebreak just by keeping her length. Against the top 5 she kills herself 32 times in 93 games; they do it 3 times.
- **The shed chains have four overlapping causes:** an ally body or head boxes her (47 of 103), an economy split with one open step (45), a pocket that fits her before eating but not after (35), and a false "exit blocked" reading on portal exits (25, a real bug, reproduced locally).
- **We do not finish a lone enemy queen.** 14 of 53 losses to non-top-10 teams and 8 of 30 Devil losses end with us holding 45-255 length against a queen of L2-16. Our hunters are L2-3 (reach 1-2), and a king refuses a certain queen kill because the king gate in `tryRam` returns before the queen-kill call.
- **We waste length on stillborn splits.** 14% of our splits create a child that dies within a round (top 5: 4.8%), about 21 length by r100 on a total of about 58.
- **Every A/B so far was underpowered and PAE is biased by opponent mix.** v49, v60 and v64 are firm losses; v55 over v44 is likely real (+5 pp); v61 over v55 is unproven (+1 pp).

**One constraint on ranking.** The Qualifier (10 Oct) is on unseen maps, and the freeze is Fri 9 Oct 06:00 UTC (2:00 AM EDT). All-maps fixes help both the ladder and the Qualifier; map-specific fixes only help ladder seeding. The stats lens budget is 9-12 server decisions in total, so all-maps fixes go first.

**Lesson from v69 that applies to every queen-safety flag below.** v69 cut early self-inflicted queen deaths (19 of 70 to 0 of 23 against the top 5) and still lost: she was then rammed (19 of 23) and r100 total length fell from 58.5 to 50.3. Each queen flag therefore needs two guard stats alongside its target stat: r100 total length must not fall, and on Stripes the W-vault eats by r50 must stay at 15 or more.

**Where the lenses disagree:**

- **QNOPOCKET.** The should-win lens wants it on globally (it does fire under QS_FROM=100). The Stripes and queen-trace lenses show that stopping the queen's r13 vault dive on Stripes loses games (0 of 4 locally, and every server build without the dive collapsed there). Resolution: enable it only with a Stripes exemption (proposal 4).
- **Early queen on Devil.** A home-box queen wins tiebreaks but weakens the centre fight (prototype won the army in 8 of 32 local games). Kept as the last proposal, Devil only.

## Key findings per lens

### Top-5 losses (100 games of v61/v69 vs forgot to mention, Vibing++, SSS, Sponge, horse; 40-60)
- Loss endings: 24 their queen alive and ours dead (we had more total length in 10), 20 eliminations, 16 longest-dragon.
- Retention is the gap: self-inflicted deaths by r100 cost us 80 length against 41 for them. We eat more fresh pearls by r100 (96 v 81) and hold the same length (58 v 60).
- Stillborn splits: 48.9 children per game die within a round of being split (top 5: 11.4). Slithery Fight 304 v 48, Around UNSW 131 v 19, Australia 116 v 10. Cause: `SPLIT_NEEDS_EXIT 0` (params.hpp:141) and `SPLIT_VIABLE 0` (:832), so the growth split at main.cpp:5187 never checks the child has a free tile.
- Long lunges: our L>=8 dragons were rammed head-on 101 times, 63 from 3 or more steps; in 51 the lunge was longer than our threat model's reach (`KING_THREAT_REACH 4`, `THREAT_TAIL_UNKNOWN 2`). Three king rams after r490 flipped games we led (984270, 986287, 1007193).
- No protect-the-lead mode: 5 losses were ahead on the deciding tiebreak after r450.
- Map notes: Devil 0-3 and Trophy 1-4 (queen rammed by r40 in 6 of 7); Schooltime layout B 0-5 (we eat 0-3 top-strip pearls by r200, they eat 29-46; `SCH_B_KEEP` exists and is 0); Around UNSW 5 longest-dragon losses with more total length.

### Should-win losses (53 losses to non-top-10 teams)
- Endings: 22 queen-dead at r500, 20 eliminated, 7 longest lost, 4 queen shorter. In 23 of the 33 r500 losses we had more total mass.
- Lone-queen survivors, 14 of 53: Devil 985964 (141 v 2), 1006614 (145 v 2), 1005726 (138 v 2, 582 sighting turns and 0 killable because the seers were L2).
- King refuses the kill, 2 confirmed: Tower Defense 985968 (141 v 14, 21 turns with a free 3-5 step path) and 1007417. Cause: main.cpp:3966 `if (!ENABLE_RAM || units < 2 || (feedPhase() && iAmKing())) return false;` sits before the queen-kill call.
- Ally-plugged corridor shed chains, 15 of 53: Devil 1007413 (we led the tiebreak, she died r467), Maze 985232 (L28 queen and L59 king deadlock, their queen dead since r45).
- Eliminations by fast splitters on lane maps, 20 of 53: trades are even, but they eat 2-4x the spawn pearls in r21-60. No verified fix.
- QNOPOCKET does fire under QS_FROM=100 (local Stripes check); the "never fires" line in LOSS_AUDIT2 is out of date.

### Maze and Devil
- Maze (6 wins in 38): economy stalls from r100 (total 63/91/97 at r100/200/300 against 74/153/158 for teams that beat us). About 62 of our units die boxed in the home field by r200 (winners 18-23). Maze gets no crowd penalty because `applyMapParams` returns early for sprint maps (main.cpp:92). A prototype crowd penalty lifted r200 total from about 95 to about 147 but broke king formation in 4 of 8 games unless switched off at the king seed round.
- Maze queen: dead in 35 of 38, 28 at the field doorway or in the maze. Winners keep her deep in the field and crown her (alive in 22 of 32, longest in 17).
- Devil (7 wins in 37): 22 eliminations from a centre snowball decided by r20-40 (no verified fix), and 8 r500 losses to a lone home-box queen while we held 92-174 length. `LATE_HUNT=1` raised the local home-queen kill rate from 5 of 9 to 7 of 9.

### Portals, Stripes, Trophy
- Portals: our queen is dead at r500 in 49 of 50 games, 43 by HitSelf in a portal vault, 41 by r100. Top teams park her at L3 in her own half for 300-400 rounds and then crown her (+29 to +35 length). In 21 of 27 queen-dead losses our non-queen king was already longer than their final queen.
- Stripes: rating tracks whether the queen dives the far vault at r13 and seeds the second farm. v55/v61/v64/v65 do; v44/v49/v60/v69 do not. No build of ours takes the free centre loop that top queens reach by r9-13 (loop pearls by r50: 11.5 for them, 1.3 for us in losses).
- Trophy: the split floors hold our queen at L5-7 (first split r27 against r10), so we have 3 units at r30 against 6.5.
- Caveat for all tooling: dragon id 0 is not always team A in server replays. Derive the queen from `g['team'][0]`.

### Queen trace (349 audit replays, code-level, with a local debug build)
- **Bug:** with `PORTAL_ECHO_GUARD=2` (main.cpp ~1855-1888) a portal exit is marked as an ally head when the probe ray reports a head anywhere along the ray. `evalDir` then treats the exit as illegal, QBOX_K2 sheds her to L3, and the all-lethal fallback (~5873-5893) ranks the phantom tile below kelp and her own body, so she steps into her neck. 18 deaths with a truly free exit (15 on Portals); a local patch took that death mode from 5 of 12 to 0 of 12.
- One-open-step splits: 61 of 339 such splits (18%) led to a shed-chain death within 8 rounds, against 2.6% with two open steps and 1% with three. `qsrBlock()` only checks a flood of 16 tiles and no ally head within 2.
- Growth: `eo.dead = qGuard() && area < need` with `need = myLen + 3` (main.cpp:5448) does not count the pearls she will eat inside the pocket. Tower Defense 985968: L4 enters an 8-tile pocket with 5 pearls and is boxed by her own body at L8.
- Ally enclosure: `QAK_PEN 150` is a soft penalty on ally head end-tiles only; ally bodies cost nothing. Prisoners Dilemma 984268: lost 47 v 2 to an L2 queen.
- Each patch alone barely moved local deaths; the phantom-exit fix plus the split rule together moved Portals deaths before r100 from 7 of 8 to 4 of 8.

### Stats (4,160 server games)
- PAE is biased: against 2300+ teams we score 0.30-0.47 where Elo expects 0.20-0.22, so a window with more strong opponents gets a higher PAE for free. Share of 2100+ opponents ranged from 17% (v49) to 61-74% (v69).
- Every test was 3-6x underpowered: detecting 5 pp needs about 845 games per arm; we used 160-490. Identical code differs by 4-9 pp between windows.
- Proxies carry signal in far fewer games: queen dead by r100 gives P(win) 0.54 against 0.75 alive; length ratio at r100 above 1.25 gives 0.81, below 0.8 gives 0.31.
- Throughput is about 95 games per hour, about 10,000 games before the settle period.

## Ranked proposals

Every flag goes into `bot/` with default 0. Line numbers are approximate. Gains are rough estimates from the loss shares; none is measured.

### 1. HUNT_FINISH: kill the lone enemy queen (all maps)
- **Flags:** `LATE_HUNT=1` (built, variants/v68), new `QKILL_KING=1`, new `LH_FINISH=1`.
- **Change:**
  - `QKILL_KING`: in `tryRam()` (main.cpp:3960-3968) call `tryQueenKill()` before the `feedPhase() && iAmKing()` return for every non-queen unit. Optional limit: a true king of L>=20 skips it only when our queen is known alive and longer than theirs.
  - `LH_FINISH`: turn the hunt on (`lhOn()`, main.cpp:2235) also when enemy units seen or relayed over the last 30 rounds are 3 or fewer and their queen is L<=4, whatever our own queen's state.
  - Hunter reach: while the hunt is on, units inside the pull radius do not split below L6 and the pull prefers L>=5 units. Check the hunt BFS routes through portals.
- **Evidence:** 14 of 53 should-win losses, 2 confirmed king refusals (both would have been outright elimination wins), 8 of 30 Devil losses, and about 21% of all audited losses per STATUS. Local: home-queen kills 5 of 9 to 7 of 9 with LATE_HUNT alone.
- **Expected gain:** +2 to +4 pp, mostly against non-top-10 teams.
- **Risk:** low for `QKILL_KING` (only fires on a visible certain kill). `LH_FINISH` could pull units off food in a game that is not actually won; the 3-unit, L<=4 gate keeps that narrow. EQ_HUNT (always-on) was rejected locally; this stays gated.
- **Target stat:** r500 losses with their queen alive and 3 or fewer enemy units, per 100 games against non-top-10.

### 2. QFIX_PORTAL: phantom portal-exit bug plus no split with one open step (all maps)
- **Flags:** `QFIX_ECHO=1`, `QFIX_RANK=1`, `QFIX_VSPLIT=1` (sketched in scratch `qtrace/botfix/main.cpp`).
- **Change:**
  - `QFIX_ECHO`: for the queen, in the portal echo guard (main.cpp ~1855-1888) drop the `bodies>0 && shortPath` rule and limit the `heads>0` rule to heads within `PORTAL_ECHO_RANGE` of the exit. Real WARN messages stay walls. At L<=4 an echo-only block is a penalty, not a wall.
  - `QFIX_RANK`: in the `bestD<0` fallback (~5873-5893) rank an unseen tile with `occId==(1<<20)` above kelp and above own body for the queen.
  - `QFIX_VSPLIT`: in `qsrBlock()` (~4597) return true when the queen has fewer than 2 open plain visible steps from her head.
- **Evidence:** 25 of 250 losses involve a false block (16 died with the exit free); 45 of 250 have a one-open-step split in the fatal chain. Reproduced with a debug build.
- **Expected gain:** +1 to +2 pp overall, most of it on Portals, Australia and Around UNSW.
- **Risk:** low; it is a bug fix. Locally she still died later in vaults on Portals, so this alone will not fix Portals (see proposal 7). Stripes play was unchanged by the split rule locally.
- **Target stat:** queen deaths next to a free portal exit (should reach 0) and queen alive at r100.

### 3. QBOX_ALLY: allies must not seal the queen (all maps)
- **Flags:** `QAK_HARD=1`, then `QPLUG_LOOK=1`.
- **Change:**
  - `QAK_HARD` (cheap first test): in the QALLY_KEEP block (main.cpp ~5357-5400, ~5598-5605) make the penalty a hard veto when any other legal move exists, use `QAK_DIST 3` for allies of L>=8, and count the ally's post-move body tiles on her exit tiles, not only the head end tile.
  - `QPLUG_LOOK` (queen side): before stepping into a tile with exactly one onward exit, follow the 1-wide corridor up to 4 tiles; if it reaches a non-self body tile whose clear time exceeds her arrival time, mark the step dead when another surviving step exists.
  - A king that sees the queen with 1 or fewer free neighbours stops king-swap splits on her exit and moves off it.
- **Evidence:** 47 of 103 shed-chain losses have a non-child ally among the blockers; 15 of 53 should-win losses. Late direct flips: Maze 985232, Prisoners Dilemma 984268 (47 v 2), Devil 1007413, weakhold 972452. Of 35 late shed-chain losses, 19 flip if she keeps her length.
- **Expected gain:** +1.5 to +3 pp.
- **Risk:** medium. A hard veto can stall allies in tight maps or feed gridlock (Maze). `QPLUG_LOOK` is narrower than QEXIT_LOOK (server loss), which penalised every low-exit tile; keep it to body plugs only.
- **Target stat:** queen shed chains with an ally neighbour per game; r100 and r300 total length unchanged.

### 4. QDEAD_GROW: growth-aware dead-end test, with QNOPOCKET outside Stripes (all maps except Stripes)
- **Flags:** `QDEAD_GROW=1`, `QNOPOCKET=1` with new `QNP_SKIP_STRIPES=1`, optional `QLATE_NOPOCKET=440`.
- **Change:**
  - `QDEAD_GROW`: at main.cpp:5445-5448, for the queen use `need = myLen + 3 + (pearls and every-round pearl tiles inside the flood from t)`. Keep the existing "veto only when an open alternative exists" rule.
  - In the veto at ~5815, when the dead step has no way back within `myLen` turns, let a threatened open step beat it unless that threat is a certain 1-step ram. Get a debug trace of the 984268 geometry first (Prisoners Dilemma, queen at (14,4), r487); the precedence cause is a hypothesis.
  - `QNOPOCKET=1` (params.hpp:1436) everywhere except Stripes; on Stripes the r13 vault dive stays.
  - `QLATE_NOPOCKET`: from r440, if our queen is alive and at least as long as the last known enemy queen, pocket pearls are worth 0 to her.
- **Evidence:** 35 of 103 shed-chain losses are growth boxes; 25 of 250 losses are static pockets (Maze 980979 and 984645, both lost while far ahead on mass); 12 of 24 top-5 queen-dead losses are self-inflicted.
- **Expected gain:** +1 to +2 pp.
- **Risk:** medium. This is the family where v60 and v69 lost by starving the early queen. The Stripes exemption is mandatory. Watch r100 total length.
- **Target stat:** queen deaths with three kelp neighbours or boxed by own coil; Stripes W-vault eats by r50 at 15 or more.

### 5. SPLIT_SAFE: stop stillborn children (all maps)
- **Flag:** `SPLIT_SAFE=1`.
- **Change:**
  - Voluntary case: in the growth split at main.cpp:5187, skip the split this turn when `tailHasExit(2)` is false, and keep moving and eating (do not hold; idling is what sank `SPLIT_VIABLE` locally).
  - Forced case: extend the queen's eat-into-a-box veto (QBOX_EAT_PEN, ~5425) to every unit: penalise a pearl step that leaves no free neighbour next turn unless `splitSideArea(true, 2, 3)` passes.
  - Leave the pocket-factory branch (~5170) alone so the Stripes and Portals vault farms keep working.
- **Evidence:** 48.9 stillborn children per game against 11.4 for the top 5; 21 length by r100 on a total of about 58. Heaviest on maps holding 26 of the 60 top-5 losses. On Maze, 62 units per game die boxed in the home field by r200.
- **Expected gain:** uncertain, +1 to +3 pp if the length is retained; the r100 length ratio is a strong win predictor (0.31 below 0.8, 0.81 above 1.25).
- **Risk:** medium. `SPLIT_NEEDS_EXIT` and `SPLIT_VIABLE` both lost locally under the old rules (never on the server). Fewer splits can mean fewer heads early.
- **Target stat:** stillborn children per game and r100 total length; unit count at r50 must not fall.

### 6. KING_GUARD: wider defensive threat reach and a protect-the-lead endgame (all maps)
- **Flags:** param step `THREAT_TAIL_UNKNOWN 4` and `KING_THREAT_REACH 6`; then `ENDGAME_GUARD=470`.
- **Change:**
  - Param step: params.hpp:565 and :67.
  - Code step (main.cpp ~3158-3215, ~5520): for L>=8 and for the queen use `K(Lv) = ceil(Lv/4) + Lv - 2` with an unseen tail assumed Lv>=5. For a king of L>=20 or the queen, a threatened tile is a veto when an unthreatened step exists.
  - `ENDGAME_GUARD`: from r470, for our longest dragon and a live queen, pearls are worth 0 unless the step is unthreatened; use free steps to stay further than `K(enemy)+1` from every visible enemy head; no queen splits; no king-swap splits after r430 unless there is no legal move.
- **Evidence:** 51 of 101 head-on rams on our L>=8 dragons out-ranged our model; king rammed at r>=440 12 times against 5; 5 thrown leads after r450; late king swaps cost 3 should-win games (985234 lost 52 v 53 with 368 v 114 total).
- **Expected gain:** +1 to +2 pp, concentrated against the top 5.
- **Risk:** medium. A wider reach makes long units timid and can cost economy mid-game. Local self-play cannot judge it because our bot never lunges; spar against variants/v64. QKREACH and QWARN (queen only) were rejected locally; LUNGE34 was offence and is not being retried.
- **Target stat:** head-on rams suffered by L>=8 from 3 or more steps; king rams at r>=440.

### 7. PM_QPARK: park the queen and crown her on Portals and Maze (map-specific)
- **Flags:** `PM_QPARK=1` (Portals, Maze), per-map `RP.queenKing`, `PM_MAZE_CR=3..8`.
- **Change:**
  - Portals (`bot/maps/portals.hpp`): from r0 to the king seed round the queen never crosses a portal edge and takes no POR_PULL or pocket dives (add an `amQueen()` exclusion in `pfDiveOK`, main.cpp:3627, for this map); she circles a 2x2 block in her own half and falls back to normal evasion when an enemy head is in reach. From `PM_POR_KS` (330) enable `QUEEN_KING` through a per-map RuntimeParams field. The existing fallback (non-queens crown if she is not heard) stays.
  - Maze (new `bot/maps/maze.hpp`): until the seed round, heavily penalise queen tiles with frame x>=9 and block queen pump-splits; from the seed round enable `QUEEN_KING` for Maze. In the sprint branch of `applyMapParams` (main.cpp:92) set `RP.crowd = PM_MAZE_CR` and apply it only while `round < RP.kingSeedRound`.
- **Evidence:** Portals: 21 of 37 losses flip if a parked queen had received our king's feed. Maze: 8 of 16 queen-dead losses flip the same way, and the crowd penalty lifted r200 total from about 95 to about 147 locally. v65 (QK_BIG) failed on these maps because the queen was dead before the feed (9 of 10 on Portals, 9 of 13 on Maze); in the 2 Maze games where she lived to be fed we won.
- **Expected gain:** +1.5 to +2.5 pp on the ladder (2 maps of 17, both currently among our worst). Nothing for the Qualifier.
- **Risk:** medium. QK_BIG lost on the server (-6.4 pp, though the adjusted re-score against adjacent v61 is only -2.4). The new part is the park, which must keep her alive to the seed round. The crowd penalty breaks king formation if left on after the seed round.
- **Target stat:** queen alive at the seed round (target near 100% on Portals) and queen length at r500 (target 30 or more); Maze home-field deaths by r200.

### 8. DEVIL_HOMEQ: home-box queen plus home-box sweep on Devil (map-specific)
- **Flags:** `DEVIL_QSPLIT0=1`, `DEVIL_QHOME=1` (prototype in scratch `mazedevil/bot_dq/`), new `DEVIL_SWEEP=1`.
- **Change:**
  - Queen splits 4 into 2+2 on turn 0; the L2 queen stays in the home box (frame x<=4) and eats once or twice on the own-side fast tiles at (5,0)/(5,15) so she is L3 or longer.
  - `DEVIL_SWEEP` in `devilScore` (`bot/maps/devil.hpp`): when `round >= 100`, `units >= 16` and the enemy queen is not known dead, non-queen units with `id % 4 == 0` get a pull to the enemy home box through the door at rows 7-9.
- **Evidence:** our queen is dead by r60 in 31 of 37 Devil games; 8 of 30 losses are r500 tiebreaks to a home-box queen; the prototype won 4 of 9 lost-army games on the tiebreak. Devil is our second-worst map (13 of the 53 should-win losses).
- **Expected gain:** up to +1 pp on the ladder. Nothing for the Qualifier.
- **Risk:** high. The prototype won the army fight in only 8 of 32 local games, and 22 of 30 Devil losses are eliminations that this does not address. EARLY_QSPLIT was rejected locally. Only about 15 Devil games arrive per 2-3 hour window, so the server signal will be weak. Proposal 1 already covers the sweep's main target; run this only if a slot is free.
- **Target stat:** Devil queen alive at r60; Devil r500 queen-dead losses.

### Left out of the top 8 (backlog, in order)
- **Stripes exemption for any early-queen penalty** (zero cost; folded into proposal 4's rule).
- **Stripes centre loop** (new `bot/maps/stripes.hpp`): the queen laps the 8-tile loop from r9 and her first child takes the W vault. Removes the dependence on the queen dying; small code, 1 map.
- **Trophy queen split floor** (`RP.queenKeep`): the queen splits at L4 like a normal unit while units are 8 or fewer. 14 of 250 losses.
- **`SCH_B_KEEP` on** for Schooltime layout B (param, mask 3 then 15). 0-5 on that layout.
- **v70 `SPRINT_KING_PM`** for Around UNSW (seed 190 / feed 230), together with proposal 6.
- **Tiebreak-aware feed** (feed the queen when both queens live and theirs is longer; no king swaps when both are dead). Large code.
- **Lane-map rush eliminations** (20 of 53 should-win losses, 22 of 30 Devil losses): no verified fix; mechanism experiments only.

## A/B protocol (from the stats lens)

1. **Baseline.** Keep one pooled v61 baseline and grow it with interleaved blocks. Read our real standing only from v61's stored rating (2187). Never use server rating or rank as A/B evidence: at 2-3 hours the rating difference between two builds has an SD of about 40-45 Elo.
2. **Scoring.** Replace PAE with the adjusted logistic model: win ~ build + opponent fixed effect (ridge, opponents with 12 or more games) + map fixed effect + ranked + autoscrim. Report the build contrast in pp with P(better). `stats/a2.py` in the scratch dir is a working version; it belongs in `tools/ab_server.py` as a new mode.
3. **Interleave.** Alternate baseline and candidate in 45-60 minute blocks by re-activating stored submissions, about one baseline block per two candidate blocks. Freeze the challenge loop's opponent list during a test so both arms meet the same teams.
4. **Opponents and maps.** A fixed panel of 10-12 teams rated about 1950-2270 (Vibing++, forgot to mention, Sponge, horse, WeHaveQuizzes, Computers, free trip to sydney pls, bread first search, Settlers, Team SKKU, Sabotage-d). Unranked 5-map series rotating evenly through all 17 maps. While a candidate is live the loop launches unranked challenges only; ranked challenges run only while the build we intend to keep is active.
5. **Stage 1, mechanism gate (100-150 candidate games, about 1.5 hours).** Download the replays and compute the proposal's target stat plus queen alive at r100, length ratio at r100, elimination rate and queen dead at r500. Continue only if the target stat moves at least 10 pp the right way and the log length ratio at r100 is not down by more than 0.1. Any queen flag must also pass the Stripes check (W-vault eats by r50 at 15 or more).
6. **Stage 2, win rate (adjusted estimate).**
   - At 250 candidate games: drop if below -1 pp.
   - At 500: drop if below +1 pp.
   - At 850: adopt if +2.5 pp or more.
7. **Budget.** About 250 games (2.6 hours) per early reject and 850 (9 hours) per full confirmation, so 9-12 decisions before the freeze. Queue no more than 12 candidates.
8. **Bundling.** With that budget, proposals 2, 3 and 4 can run as one "queen survival" candidate if each flag's own target stat is checked in stage 1; the queen-trace lens found the fixes only showed an effect in combination. Proposal 1 is independent and can run first because LATE_HUNT is already built.
9. **Final build.** Activate it at least 12-15 hours before the freeze (Fri 9 Oct 06:00 UTC / 2:00 AM EDT) so it has 600 or more ranked games. No new code in the last 12 hours. The Qualifier build still needs the `tools/unseen_eval.py --sets real,realhold,blind17` check, and only the all-maps proposals (1-6) carry over to unseen maps.
