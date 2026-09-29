# Unseen-map plan (synthesis of 6 research tracks)

Written 2026-09-28. The Sprint submission freeze is **2026-09-30 18:00 UTC**, about 40 hours away. Live version: `variants/v24`.

Detail for each item is in the track write-ups in `notes/unseen/`:
- `unknown-portals.md`
- `runtime-map-features.md`
- `pearl-inference.md`
- `endgame-king.md`
- `failure-mining.md`
- `external-knowledge.md`

I checked the code locations below against `bot/main.cpp` (2581 lines).

---

## 1. Three cross-cutting insights

### 1.1 On an unknown map, most of v24's best machinery is switched off

Each tuned feature depends on a fact that only map knowledge supplies:

| Feature | What turns it off on an unknown map | Where |
|---|---|---|
| King and feeding | `RP.kingDeclare=0`. Nobody passes length 5 before r450, so no beacon goes out and nobody feeds. 23 of 46 local round-limit team-games ended with the longest dragon at 7 or less. | — |
| All portal guards (WARN, MEMO, ECHO_GUARD, BODY_PEN, NEWBORN_NECK_GUARD) | They key off `portalExit[]`, which is empty. | `observeEdges` sets `nxt=-1` for every unknown portal, main.cpp:554 |
| Hot-tile logic (DFS eats, PUMP_TIP, `rate()=1`) | Every gate tests `gmin==gmax==1`, which is never true. | main.cpp:1118, 2325 |
| Pocket pumping | `POCKET_UNK_NEEDS_HOT=1` makes it depend on hot tiles, so it is dead too. | — |

So the cheapest unseen-map gains come from turning existing, already-tested code back on using signals we can observe at runtime:
- a quiet map or a full team (for the king);
- countdown==1 runs (for hot tiles);
- clean knock echoes (for portals).

Inventing new behaviour comes second.

### 1.2 Self-play on blind maps cannot see our two biggest unseen-map losses

`unseen_eval` plays blind against blind, so both sides lack a king and both treat portals as kelp.

Real opponents do both:
- **Portals.** Blind v24 against map-aware v24 on Default lost 0/2, with 6-13 eats against 81-91 in r0-99 and elimination at about r210. Blind against blind on the same map is a coin flip decided by side.
- **King.** Top-10 kings on Portals, Trauma and QoS are 31-42 long. Blind v24 reaches 4-7.

Every rejected LEARN_PORTALS or UNK_SIZE_PARAMS result was measured in a setting that cannot reward the idea. Map/seed pairs that end identically before r300 add 0.5 noise on top of that.

**Before judging items Q2 and Q4, the main agent must add an asymmetric set.** Call it `blindvk`: the candidate is built with `-DNO_KNOWN_MAPS=1`, and it plays map-aware v24 on Default, QoS, Portals, Schooltime and Trauma. Judge it on eats in r0-300, survival round and r500 longest length, not on win rate. Also add a named `gated` set:
- lesson islands_a/b and vault_a/b/c;
- gen g2026_23/28/32;
- genhold g2027_13/16.

This is a change to `tools/unseen_eval.py` only. It is the main agent's job, because tracks may not edit `tools/`.

### 1.3 Knowledge dies with each process, so rules must be recomputable per dragon

70-90% of our dragons are split children with empty memory. That is why:
- per-dragon portal knowledge is 0.24-2.7 pairs, against a team union of 10/12;
- our late king reach is 59-61%, against 75-89% for the top teams.

Good designs follow from this:
- Prefer rules every dragon can derive alone: the round, `units`/`UNIT_LIMIT`, its own 7x7 view, its own knock echo.
- If something must be shared, use a standing broadcast (KING_NET), not a one-off message.
- Never write learned facts into `w.nxt`, which routes idle wanderers. LEARN_PORTALS failed exactly that way, over-crossing 3.4x.

---

## 2. Ranked implementation queue

Rank = (expected unseen gain x confidence) / effort, adjusted for the freeze.
- Q1-Q4 are the Sprint candidates.
- Q5-Q8 are for Qualifiers (10 Oct) unless time remains.
- Every flag defaults to 0 in `params.hpp`.
- Everything marked "!w.known" leaves ladder play byte-identical. Confirm that with 1 ladder seed; it must come back at exactly 0.50.

### Q1. `CAP_RESERVE` (test first with zero code: `-DSPLIT_MAX_UNITS=60`)

**Spec.** Keep R=4 team slots free for rescue splits:
- Growth splits (including LATE_SPLIT) stop at `unitLimit-R`.
- ESCAPE_SPLIT and the pocket pump stop at `unitLimit-R/2`.
- The trapped reverse split and KING_ESCAPE's split may still use every slot.

**Why.** 88% of our trapped L>=5 deaths before r400 happen at 63-64 units: 329/374, or 3159 length, in 16 unseen games. In 95% of them the tail had an exit, so a reverse split would have saved the rear. Schooltime ladder games have the same pattern: 305/338 of those deaths were at the cap. Nothing cap-related appears in the journal. This applies on known maps as well.

**Code** (main.cpp):
- growth split, line 2334: `units < w.unitLimit` becomes `units < w.unitLimit - CAP_RESERVE`;
- ESCAPE_SPLIT, line 1156;
- pocket gate, line 1870;
- optionally the keepLen peel, line 2309;
- leave lines 2481 and 2139 unchanged.

**Value / risk / effort.** High on maps that reach the cap (open, maze and islands lessons, big gen maps, Schooltime) and zero elsewhere. Low risk: about 6% fewer foragers while at the cap. Effort: zero code now, then about 10 lines.

**Test.**
1. Mechanism check with `fm_trapped.py` on 3 single games (lesson open_a and maze_a, blind Schooltime). Pass if trapped at-cap L>=5 deaths drop by at least 70%.
2. `unseen_eval 'variants/v24:-DSPLIT_MAX_UNITS=60' --sets gen,blind,lesson,ladder`, and also try 58.
3. If positive, implement the full flag and run a Schooltime server mini-batch of 10 games.

### Q2. `UNK_KING` + `FEED_QUEUE` (merges UNK_KING_BASE, UNK_EARLY_KING and endgame UNK_KING)

**Spec.** When `!w.known` and there are no candidates, apply this once in a new `applyUnknownParams()` at the UNK_SIZE_PARAMS hook (main.cpp:761):
- `kingDeclare=1`
- `kingSeedRound=UNK_KING_SEED` (250)
- `feedStart=UNK_KING_FEED` (300)

Then, each turn:
- Drop the seed to `max(110, round)` once `units >= unitLimit-2` (the saturation trigger, bit 2).
- Optionally drop it to 170 after 50+ turns with no enemy head within walking distance 4 (the quiet trigger, bit 1). Ship bit 2 first; bit 1 is optional.

Replace the fixed feed reserve with a schedule that every dragon computes the same way: `feedReserveNow() = max(3, 14 - (clamp(round,300,490)-300)*11/190)`. This goes in the V2 branch of `shouldFeed()`, main.cpp:1732.

FEED_QUEUE (V2 feeding block at about line 2259-2295):
- a feeder holds for up to 6 rounds while a pearl lies within 2 of the king's head, in front or beside;
- only the ally closest to the king feeds, with ties going to the lower id;
- no feed deaths more than 3 tiles from the king.

`FOOD_RESERVE=2` zeroes pearls within Manhattan distance 2 of a fresh king for subordinates, in `pearlValue()`.

**Why.** Blind Portals, Trauma and QoS end with a longest dragon of 4-7 against top-10 kings of 31-42. Each such game is a certain tiebreak loss against any team that builds a king. Unthrottled king-on already failed: g12 collapsed from 38 to 6 units and was eliminated; g28's king was rammed at r498. The reserve schedule and the queue are what make it survivable. UNK_SIZE_PARAMS was neutral because it fired on the wrong maps (N>=1000) and fed with reserve 4. This merged flag fixes both. The rival proposal (UNK_KING_BASE: seed 350 at all sizes) is the conservative fallback arm.

**Value / risk / effort.** The highest tournament value in this plan. Medium risk: swarm collapse or king rams if the throttle is wrong. Effort: about 60 lines. Bit 1's quiet test adds a BFS for enemy heads within 4, about 20 more lines.

**Test.**
1. `unseen_eval "bot:-DUNK_KING=1 -DFEED_QUEUE=1 -DFOOD_RESERVE=2" --sets gen,blind,lesson` against v24. Pass if at least 0.50 and elimination losses after r300 do not rise.
2. `localking.py` on saved replays. Target: the share of round-limit team-games with longest <=7 at r500 falls from about 0.5 to under 0.15. Check units at r420.
3. Blindvk on the 5 ranked maps. The opponent builds a king, so this is the real test.
4. Arms: seed 250 vs 350, and FEED_RES_HI 10/14/18. Run at most 2 arms before the freeze.
5. Holdout once on the final combination.

FEED_QUEUE alone is also on-map, since KING_V2 is active on 8/10 ranked maps. If the unseen result is positive, run a ladder pool and a 10-game server mini-batch on Schooltime/Slithery.

### Q3. `TURN_ORDER_TIES`

**Spec.** A tile reached at our step s against another head at distance k is ours whenever s <= k, whatever the IDs. Two changes:
- `pearlValue()`, main.cpp:1006: `od==s` stops applying 0.55. It keeps 0.85 only when the tying head is an enemy (needs an `otherEnemy[]` array from `computeOtherDist`).
- `bfsFrom()`, main.cpp:1030: the Voronoi test becomes `du <= otherDist[u]`.

**Why.** The engine moves heads sequentially: a lower-ID head has already moved this round, and a higher-ID head moves after us. So ties are won, and two allies never both see themselves as first. Top teams contest 24% of eats against our 19%. Unlike EAT_SPRINT, this costs no length.

**Value / risk / effort.** Small and global, +1-3%. Low risk: more head-ons among small dragons, but `threatAt` still applies. About 15 lines.

**Test.** A pool against v24 on gen, blind and lesson (at least 120 games), plus a ladder regression, because it also changes known maps. Also check the contested-eat share. Retest with PEARL_ROUTE, which reads `pearlValue`.

### Q4. `UNK_EXPLORE` (knock-before-crossing; folds in UNK_EXPLORE_NOSPLIT, and replaces PORTAL_ATLAS and UNK_SCOUT)

**Spec** (only when `!w.known`):
1. A dragon ending a single-step turn on an unknown portal mouth casts a solo knock ray through it. It uses the WARN payload in `emitSonar()`, next to the PORTAL_WARN block at line 1650, and never opposite its facing direction.
2. `readMessages()` records whether the knock came back clean: all rays returned and no dragon echo.
3. Crossing that edge becomes a candidate in `decide()` only when all of these hold:
   - a clean knock came back from this tile last turn;
   - L < 10;
   - no threat at the head for L >= 6;
   - the edge is past its 8-round cooldown;
   - the desire gate is open. The gate opens when the walk-region is closed (BFS over `nxt`, capped at 600 tiles, finds no never-seen tile) and hunger is at least 3. It also opens when hunger is at least 25 and no visible pearl is within 6.

   The candidate goes after the direction loop and before `tryKingEscape`, next to the UNK_PORTAL_ESCAPE code at line 2503.
4. The link is learned on arrival, in `updateTrail()`. It goes into a separate `learnDest[]`, **never `w.nxt`**, and `computePortalExits()` adds mouths plus `learnDest` exits so the existing guards wake up.
5. Add a small mouth lure of 0.4 in `pearlValue` while the gate is open.
6. NOSPLIT: `threatened |= round - lastPortalRound < myLen` on unknown maps, so no child is born straddling a portal.

**Why this is not LEARN_PORTALS again:**
- It learns by crossing, so it reaches sealed regions that are never visible. On Trauma, g32 and islands_a, 0-33% of far ends are ever seen.
- Learned links never enter the BFS topology, so there is no idle over-crossing.
- Each crossing needs a fresh clean knock (0.6% fatal in notes/17) and a reason to cross, so the crossing budget is capped by construction.

Stake: 35.5% of the pearl rate on the 9 ranked portal maps sits behind portals (Trauma 99%, QoS 73%). On lesson islands and vaults the figure is 75-97%.

**Value / risk / effort.**
- Value: very high on gated maps; gen/genhold roughly neutral.
- Risk: medium-high. Door jams, dead-end exits (the Portals map), an enemy behind the door, and an explore score that has never been calibrated.
- Effort: about 150-200 lines across 8 functions, the largest item here.

**Test.**
1. Mechanism check with BOTDBG, one game each on blind Trauma, Default, Portals, QoS and lesson islands_a/vault_a. Pass if crossing fatality is at most 3% and dragons leave the Trauma start room by about r40.
2. The `gated` set, blind against blind.
3. Blindvk; this is the key check.
4. Regression on gen, blind, lesson and holdout: must be at least 0.50.
5. Ladder: 1 seed, which must be identical.

Ship for the Sprint only if steps 1-4 all pass by about T-12h. Otherwise it goes to Qualifiers.

### Q5. `HOT_LEARN` (level 1 only)

**Spec.** In `analyse()`'s visible-tile loop (after `w.spawnAt[t]=round+in.tin[i]`, line 814):
- 3 consecutive observed rounds with countdown 1 sets `gmin=gmax=1`;
- a later countdown above 1 undoes it.

This wakes up surviveDepth hot eats (line 1118), `rate()=1` and, through `POCKET_UNK_NEEDS_HOT`, POCKET_PUMP on unseen maps. PUMP_TIP_SPLIT stays off; it was rejected at 0.50.

**Why.** (1,1) tiles produce 44% of pearls on the dev-made ranked maps: Devil 92%, Dilemma 98%, Trauma 90%. Detection is precise; a (1,5) tile shows three 1s in a row only about 1.3% of the time. Our own generator under-represents hot tiles (6/40 gen maps), so a neutral gen score is expected.

**Value / risk / effort.** Medium value, concentrated on dev-style maps. Low risk because of the unlearn rule. About 30 lines. First confirm with one BOTDBG game that engine 1.2.2 still sends countdowns to bots.

**Test.** unseen_eval on gen, blind and lesson; read the blind Devil/Dilemma/Autarky/Trauma rows and lesson pockets/fountain. Metrics: eats per game and POCKET debug entries.

### Q6. `KING_NET` (`KING_NET_AGE=6`), only together with Q2

**Spec.** In `readMessages()`' king loop (about lines 1543-1592):
- every dragon that knows a fresh king re-broadcasts it every turn;
- accept news up to 6 rounds old;
- the hop count saturates at 3 instead of stopping the relay;
- the original round travels with the message.

**Why.** At r430/r470, only 59-61% of our L2-3 dragons hear any of our rays, against 75-89% for the top teams. Our leftover L2-7 length at r500 is 25.3 against 8.8. A dragon that never hears the king never feeds.

**Value / risk / effort.** Medium, only on top of Q2 and known-map KING_V2. Risk: more rays pollute echo counts. Probe turns already skip relays; confirm PORTAL_PROBE_SOLO still holds. About 10 lines.

**Test.** Ladder pool plus the unseen sets with Q2 on. `reach.py` target: at least 0.8 of L2-3 dragons hit at r430.

### Q7. `UNK_SMALL_RAMGUARD`

**Spec.** On unseen boards with N <= 750, set `RP.ramGuard=2` (local odds only, no `units<8` gate) inside `applyUnknownParams()`. This is the same mechanism RAM_GUARD_LOCAL uses for Devil and Dilemma at main.cpp:110.

**Why.** On the small ranked maps, guard=1 did worst: Devil and Trophy 0.25, against 0.58-0.70 with the local guard. Medium maps prefer guard=1. The flag fires on 29/40 gen maps.

**Value / risk / effort.** Small but broad. Low risk. 3 lines.

**Test.** Bundle it into the Q2 batch as an extra arm. Read only the rows with N <= 750.

### Q8. `REPLY_SEARCH` (Qualifiers)

**Spec.** For L>=8 only, right after `surviveDepth` in the `decide()` loop (about line 2379):
- let each enemy head within L1 3 make each non-suicidal 1-step reply;
- block the reply tile and re-run `surviveDepth` with a 6000-node cap;
- apply a soft penalty of 120 * shortfall / 10.

**Why.** Kings die 0.57 per game against 0.22 for the top teams. In 65 of 111 big-dragon rams, every move was already threatened, so looking 1 ply earlier addresses exactly that. It matters more once Q2 creates kings on unseen maps.

**Value / risk / effort.** Medium. Risk: king over-caution, the historic failure of blanket penalties. About 50 lines, plus making `nodeCap` a member.

**Test.** `deaths.py` for L>=8 on lesson maze and fountain_b. Then a pool on gen, blind and lesson (at least 120 games). Accept at 0.53 or better.

### Zero-code sweeps to slot into idle CPU (not queue items)

- `-DUNK_PRIOR=0.005` and `0.0025`. The flat prior is 2-5x too high after r100. Only the high side, 0.04, was tested; it lost. Rerun after PEARL_ROUTE lands.
- `-DSMALL_THREAT_PEN=8` and `6`, as a control for the PROB_THREAT idea.

---

## 3. What NOT to do

- **Do not re-run** LEARN_PORTALS (with or without UNK_BLIND_PEN or PORTAL_BLIND_PENALTY), INFER_SYM, PEARL_DISTRUST, UNK_PRIOR above 0.01, EAT_SPRINT, PORTAL_ALLY_COST, SMALL_SPRINT_THREAT, KING_V2_MERGE_ROUND, or plain UNK_SIZE_PARAMS.
  - Q2 and Q4 are the "new angle" versions. They cover different maps, add throttling, and keep learned links out of `nxt`.
- **Do not write learned portal links into `w.nxt`**, under any flag.
- **Deferred until Q4 proves out:** PORTAL_ATLAS gossip, UNK_LINK_MIRROR, UNK_EXPLORE_RETURN, UNK_LINK_SHARE, UNK_SCOUT, SPLIT_HANDOFF.
  - They only multiply the value of portal and hot knowledge, and each adds sonar traffic that competes with king, warn and probe rays.
- **Deferred to Qualifiers or later:** FOOD_GOAL, GAP_SAMPLES, UNK_CROWD_DEADEND, TRAP_ENEMY, DOOR_AREA, PROB_THREAT, FEED_REACH, KING_LAST_STAND.
  - These have low confidence or small effect.
  - LAST_STAND and FEED_REACH are worth a look only after Q2 is live.
- **Do not trust blind-vs-blind scores** for anything involving kings or portals (insight 1.2). Report early-identical pairs separately.
- **Do not tune on the holdout.** Run it once per final combination.
- **Do not stack untested flags into the Sprint build.** Freeze at about T-6h (2026-09-30 12:00 UTC) with only flags that passed both the regression sets and their mechanism check.
- **No NN, MCTS or deep minimax, and no KING_COIL.**

---

## 4. Interaction with Codex's PEARL_ROUTE (`codex-battlecode/notes/pearl-route.md`)

**Status.**
- It is built on v15 and is **not ported to `bot/`**: `grep PEARL_ROUTE` finds nothing.
- Screening against v15 scored 0.694 on gen and 0.65 on ranked.
- Confirmation and holdout were still pending.
- The port is small: a header, 3 knobs, and 2 lines at the end of `bfsFrom`.

**Recommendation.** Codex ports it onto v24 behind the flag in parallel, then runs its holdout against v24, not v15. This could be the largest single generic gain, and it is independent of Q1, Q2, Q6 and Q7.

It interacts with everything that edits `pearlValue` or `rate()`:

| Item | Interaction with PEARL_ROUTE |
|---|---|
| Q3 | Tie values feed the route sum. |
| Q4 | The mouth lure becomes route-attractive, so cap the lure at 0.4 or skip it when the route is on. |
| Q5 | `rate()=1` hot tiles give strong route pulls; this is intended. |
| UNK_PRIOR sweep | With the route on, an all-unseen path is worth about 2.25 pearls. That is more than a visible pearl 2 steps away, so prior calibration matters more. Rerun the sweep with the route on. |

When PEARL_ROUTE lands in `bot/`, re-verify each accepted Q-flag with `-DPEARL_ROUTE=1` on both sides (the gen and blind sets, 1 seed) before shipping the combination.

---

## 5. Suggested schedule (about 40 hours)

| When | Main agent (local CPU, one batch at a time) | Codex / server |
|---|---|---|
| T+0-4h | Add `blindvk` and `gated` to `unseen_eval.py`, run the baseline, run the Q1 zero-code test | Port PEARL_ROUTE onto v24 |
| T+4-14h | Implement Q2 + Q7 + Q3 and batch them; add Q6 if Q2 passes | PEARL_ROUTE confirm and holdout against v24 |
| T+14-26h | Implement Q4 and run its mechanism check; implement Q5 | Server mini-batch (10-20 games) on the best local combination |
| T+26-34h | Combination with the route; holdout once | Server A/B |
| T+34h (2026-09-30 12:00) | **Freeze.** Submit the best passing combination | — |
