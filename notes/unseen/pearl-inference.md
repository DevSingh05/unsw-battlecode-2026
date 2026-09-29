# Pearl and timer knowledge on unseen maps (track: pearl-inference)

28 Sep 2026. Read-only study, no games run. Scripts: `notes/unseen/tools/pearl_stats.py` (static map
statistics) and `notes/unseen/tools/pearl_smooth_sim.py` (offline move-ranking check). Run both from the
project root: `python3 notes/unseen/tools/pearl_stats.py [--per-map]`,
`python3 notes/unseen/tools/pearl_smooth_sim.py gen 40`.

## 0. TL;DR

- **The bot is not blind to timers.** Every visible tile's line is `x y hasPearl pearlIn`, where `pearlIn` is the
  live countdown (engine `protocol.cc:122`, `pearlIn = mSpawnsPearls ? mNextPearl : -1`). The replay-side hiding in
  engine 1.2 does not touch bot input, and our parser already reads it (`in.tin`). For any tile the dragon has
  seen, the bot knows (a) whether it is barren (-1), and (b) the exact round of its next spawn (`spawnAt`). So
  on a seen tile, "timer learning" is already solved. What is left is:
  1. **Tiles never seen** use a flat prior of `0.5*min(1, 0.01*since)`.
  2. **The spawn rate after the known spawn** falls back to UNK_PRIOR. This only matters if someone eats the pearl.
  3. **Hot tiles (gap (1,1)) are invisible to all the machinery gated on `gmin==gmax==1`** on an unknown map:
     DFS_EATS in `surviveDepth`, the hot-only escape split, PUMP_TIP_SPLIT `holdTile`, and `rate()`.
  4. **Anything more than about 12 steps away is worth nothing** (PEARL_GAMMA 0.82: 0.82^12 = 0.09). A
     fountain a dragon saw earlier, or one an ally knows about, never pulls it back.
  5. **Split children start with empty memory**, and on unknown maps that means empty map knowledge.
- **Hot tiles are where the devs put the pearls.** On the 10 ranked (dev-made) maps, (1,1) tiles give on
  average **44%** of all pearl production. By map: Devil 92%, Dilemma 98%, Trauma 90%, Autarky 77%, Slithery
  52%, Portals 31%. On the generated maps the figure is 8% (gen) and 22% (genhold, heavy tail), and on the
  lesson maps 18%. The Sprint and Qualifier maps are dev-made, so hot-tile handling on an unknown map is the
  largest pearl lever I found.
- **Hot tiles are usually not in view at the start.** Devil: 0 of 18 visible at r0, nearest is 9 walking steps
  away. Trauma: 0 of 12, at 51+ steps without portals. Fountain lessons: 0 visible, 10-14 steps. Pockets: 0,
  6-15 steps. Someone has to find them, and at the moment nobody else hears about it when they do.
- **The flat unseen prior is too high after r~60** and does not depend on the map:

  | round | bot `0.5*min(1,.01r)` | true P(pearl present on never-seen tile), gen | genhold | lesson | ranked |
  |---|---|---|---|---|---|
  | 25 | 0.125 | 0.16 | 0.25 | 0.15 | 0.06 |
  | 50 | 0.25 | 0.20 | 0.27 | 0.22 | 0.08 |
  | 100 | 0.50 | 0.27 | 0.29 | 0.37 | 0.10 |
  | 200 | 0.50 | 0.38 | 0.35 | 0.57 | 0.15 |
  | 300 | 0.50 | 0.42 | 0.38 | 0.61 | 0.18 |

  (The true figure assumes nothing eats the pearl, so real values are lower still.) On ranked-style maps the
  prior is 3-5x too high from r100 on, because 60-80% of tiles are barren there (median spawner share 0.20).
- **Spatial smoothing of the unseen prior barely changes which way the dragon moves.** Neighbour tiles share
  spawner status 94% of the time (k=1) and 86% at k=8 on gen maps. They share the exact [min,max] range 92-96%
  of the time. Even so, an offline re-ranking of the four first moves by unseen-tile value moved agreement
  with the truth-best move only from 71.7% to 78.7% (gen) and 60.5% to 64.4% (ranked). Captured value went from
  0.970 to 0.981 of best. The BFS mass behind the four neighbours covers almost the same tiles, so the prior
  mostly sets **how much** unseen space is worth compared with visible food, area and threats, and hardly
  **which** unseen space. This fits LEARN_GAPS and INFER_SYM coming out neutral. The lever is the level of the
  prior and hot or fountain knowledge, not finer per-tile inference.

## 1. What the generator and the engine do (ground truth)

**Engine** (`reference/unswbc/engine/src/pearls.cc`):
- `InitPearlCountdowns` draws each tile's first countdown from U[min,max]. The first pearl appears when that
  runs out, so a never-seen tile has P(first spawn by r) = clamp((r-min+1)/(max-min+1)). The tables above use this.
- `PearlTick`: countdown minus 1. At 0 the tile tries to spawn (only if it has no pearl and no living segment),
  then redraws **whether or not the spawn happened**. A pearl stays until eaten. The mirror tile shares the
  countdown only when the map has a SYMMETRY line (16 of 80 gen/genhold maps lack one; all 10 ranked and all
  24 lesson maps have it). Occupancy is never shared.
- A (1,1) tile always shows `pearlIn == 1` after the tick. A (1,G) tile shows 1 a fraction 2/(G+1) of the
  time. Three rounds in a row of 1 on a (1,5) tile has probability about 1/3 * 0.2 * 0.2 = 1.3%, and four in a
  row about 0.3%. So "K consecutive observed rounds with countdown 1" identifies hot tiles quickly and precisely.
- Reading a countdown the round after it resets gives an **exact gap sample**. It resets when `tin_now >
  tin_prev - 1` for consecutive observations. The current `gapSeen` (max of tin+1) keeps only an upper envelope.

**Generator** (`reference/loong/harness/mapgen.py` `assign_spawn_ranges`, see notes/13 §2.7):
- There are four layouts: spread (x3), starving, centre and fields. Spread takes one base range for the whole
  map plus barren clusters grown from seeds, 60% of maps add hotspot blocks (1-3 square, {(1,1),(1,50),(5,30),
  (20,50),(1,100)}), and 25% add late blocks. Every choice is mirrored, including on SYMMETRY-less maps, so
  spawner geometry is always symmetric even when countdowns are not.
- As a result ranges are strongly block-correlated (the 92-96% same-range figure above).

**Ranked maps** (dev-made, the best proxy for Sprint and Qualifier maps):

| map | spawner share | pearls/round (no blocking) | top classes by production |
|---|---|---|---|
| devil | 0.34 | 19.6 | (1,1) x18 92% |
| schooltime | 0.14 | 7.6 | (1,20) x26 33%, (20,80) 32% |
| portals | 0.20 | 25.5 | (1,10) x96 69%, (1,1) x8 31% |
| default | 1.00 | 1.6 | slow spread, no fast tiles |
| queen_of_spades | 0.51 | 2.1 | (1,50) x32 61% |
| trophy | 1.00 | 2.4 | (1,1000) 48%, (5,30) 26% |
| autarky | 0.19 | 10.4 | (1,1) x8 77%, (1,5) 13% |
| dilemma | 0.17 | 12.3 | (1,1) x12 98% |
| slithery_fight | 0.20 | 60.0 | (1,1) x31 52%, (1,5) 31% |
| trauma | 0.12 | 13.3 | (1,1) x12 90% |

Set averages from `pearl_stats.py` (avg / median):

| set | spawner share | fast10 share (mean gap<=10) | top 5% of tiles' share | production in r0 view | within 10 steps of own heads | own half |
|---|---|---|---|---|---|---|
| gen | .56/.55 | .24/.00 | .34/.19 | .24/.20 | .62/.66 | .46 |
| genhold | .43/.33 | .30/.00 | .35/.20 | .19/.13 | .54/.49 | .47 |
| lesson | .71/.94 | .31/.32 | .47/.46 | .13/.04 | .38/.31 | .48 |
| ranked | .39/.20 | .57/.91 | .70/.73 | .19/.12 | .48/.42 | .48 |

In short, the loong generator makes spread-food maps, while the devs make fountain maps. In a typical ranked
map 5% of the tiles produce 70% of the pearls.

## 2. What the bot does today on an unknown map (bot/main.cpp, v24)

- `analyse()` (about l.797-818): per visible tile, a countdown of -1 gives `gmax=0` (barren, exact). Otherwise
  it sets `spawnAt = round+tin` and `gapSeen = max(gapSeen, tin+1)`. `w.mirror()` returns -1 when `sym<0` (the
  unknown-map default, INFER_SYM=0), so nothing is mirrored.
- `pearlValue()` (l.972): visible gives exact. Remembered pearl gives 0.96^age. Known spawn passed and not
  re-seen gives 0.75*0.97^age. Otherwise `0.5*min(1, since*rate)` with `rate = UNK_PRIOR = 0.01` (LEARN_GAPS off).
- `surviveDepth` `eats()` (l.1115), `escapes()`/`hotEaten` (l.1128-1156), `PUMP_TIP_SPLIT` holdTile (l.2325):
  all test `gmax==1 && gmin==1`. **On unknown maps gmin/gmax are never 1, so none of these fire for learned
  tiles.** `pocketWorthPumping` alone uses `gapSeen<=POCKET_FAST_GAP` (POCKET_OBSERVED=1), so the pump can
  trigger, but the survival DFS it relies on still assumes the hot tile is empty after the first eat.
- The move score is `10 * bfsFrom pearls` (gamma 0.82, BFS cut at 60) plus area, survival, threat and
  `mapScore` (empty on unknown maps). Nothing points at a far target.

Why earlier attempts were neutral or negative (my reading):
- **LEARN_GAPS (0.50):** it changes `rate()` only for tiles already seen whose known spawn has passed and not
  been re-seen. That is a narrow slice, and the gamma horizon cuts it further. It does not touch the hot-tile
  gates.
- **UNK_PRIOR=0.04 (0.375):** it quadruples an unseen-area term that section 0 shows is already 2-5x too high.
  Dragons wander into empty space. **Lowering it has never been tested.**
- **PEARL_DISTRUST (0.41-0.45):** it throws away correct built-in data on known maps. Not relevant here.
- **INFER_SYM (0.52 vs 0.544):** it mirrors walls, and mirrored pearl knowledge is on the enemy side,
  beyond the gamma horizon.
- **EAT_SPRINT:** a combat and eating tactic, not modelling.

## 3. Interaction with Codex's PEARL_ROUTE (do not duplicate; it is being ported)

PEARL_ROUTE scores `0.15*region + 2*gamma*route[start]`, where `route` is the best single outward path through
`pearlValue`. Under the flat prior, an all-unseen path collects about `p * sum 0.82^d ~ 4.5p`, which is **2.25
pearls at p=0.5** (any round >= 100). A visible pearl two steps away is worth 0.67. So under PEARL_ROUTE the
over-high unseen prior competes directly with real food. The calibration in P3 below should be tested **with**
PEARL_ROUTE on, and probably matters more there than on v24. Both P1 and P2 feed through `pearlValue`/`rate()`,
so they compose with the route pass unchanged.

## 4. Proposals (ranked by my estimate of value per unit risk)

### P1. HOT_LEARN: learn hot (1,1) and fast tiles from observed countdowns on unknown maps
- **Why:** 44% of ranked production comes from (1,1) tiles. Every hot-tile mechanism in the bot is gated on
  `gmin==gmax==1`, which is never true on an unknown map. Evidence arrives within 3-4 rounds of standing near
  the tile, and the false-positive rate is small (section 1).
- **Where:** `Bot::analyse()`, in the per-visible-tile loop after `w.spawnAt[t] = round + in.tin[i];`, plus new
  vectors in `World` (`hotRun`, `lastTin`, `lastTinRound`, `gapSampleMax`, `gapSamples`).
- **Sketch:**
```cpp
// params.hpp
#ifndef HOT_LEARN
#define HOT_LEARN 0          // 1: learn (1,1) tiles; 2: also learn fast (1,G<=HOT_LEARN_FAST) from exact samples
#endif
#ifndef HOT_LEARN_RUN
#define HOT_LEARN_RUN 3      // consecutive observed rounds showing countdown 1
#endif
#ifndef HOT_LEARN_FAST
#define HOT_LEARN_FAST 10
#endif
// World: std::vector<short> hotRun, lastTin, gapMax, gapN; std::vector<int> lastTinRound; std::vector<char> learned;
// analyse(), in the else-branch (tile spawns), only when !w.known:
if (HOT_LEARN && !w.known) {
    if (w.hotRun.size() != (size_t)w.N) { /* assign all: hotRun 0, lastTin -1, lastTinRound -9, gapMax 0, gapN 0, learned 0 */ }
    int tin = in.tin[i];
    bool consec = w.lastTinRound[t] == round - 1;
    // exact gap sample: the countdown reset since last round
    if (consec && tin > w.lastTin[t] - 1) { w.gapMax[t] = std::max<int>(w.gapMax[t], tin); w.gapN[t]++; }
    w.hotRun[t] = (tin == 1) ? (consec ? w.hotRun[t] + 1 : 1) : 0;
    w.lastTin[t] = tin; w.lastTinRound[t] = round;
    if (w.hotRun[t] >= HOT_LEARN_RUN && w.gmax[t] < 0) { w.gmin[t] = w.gmax[t] = 1; w.learned[t] = 1; }
    else if (tin > 1 && w.learned[t] == 1) { w.gmin[t] = w.gmax[t] = -1; w.learned[t] = 0; }   // was a false positive
    if (HOT_LEARN >= 2 && w.gmax[t] < 0 && w.gapN[t] >= 2 && w.gapMax[t] <= HOT_LEARN_FAST) {
        w.gmin[t] = 1; w.gmax[t] = w.gapMax[t] + w.gapMax[t] / w.gapN[t];   // unbiased-ish max estimate
        w.learned[t] = 2;
    }
    // if (tin > w.gmax[t] && w.learned[t] == 2) { w.gmax[t] = tin; }  // widen, never narrow below evidence
}
```
  Note: `rate()` returns `2/(gmin+gmax)` once gmax>0, so learned tiles get 1.0 for hot tiles and about 2/(G+1)
  for fast ones. The `gmax[t]==1` checks in `surviveDepth` (eats, hotEaten), `PUMP_TIP_SPLIT` and
  `pocketWorthPumping` (via `gmax<=POCKET_FAST_GAP`) then work on unknown maps with no other change. Keep
  `learned[]` so filterByCountdowns/PEARL_DISTRUST logic never treats learned data as built-in.
- **Expected effect:** positive on blind Devil, Dilemma, Autarky, Trauma, Slithery and on lesson
  pockets/fountain/brawl; inactive (exactly 0.50) on maps without fast tiles; ladder unchanged (known maps skip
  it). Main channels: pumping and tip-splitting on unknown pocket maps, and DFS accepting routes that loop
  back through a hot tile.
- **Risks:** a false hot label makes the DFS optimistic (it assumes a pearl that is not there). This is
  mitigated by the unlearn-on-`tin>1` rule and RUN=3 (use 4 if paranoid). HOT_LEARN=2 changes `rate()` on
  more tiles and could pull dragons back and forth between fast tiles (the old LEARN_GAPS risk). Test level 1
  first.
- **Test plan:** `unseen_eval.py "bot:-DHOT_LEARN=1" --base variants/v24 --sets gen,blind,lesson`. Look first
  at blind Devil, Dilemma, Autarky, Trauma, Slithery and at lesson pockets_a/b, fountain_a/b/c and brawl_b.
  Metrics: win rate, eats per game, pump entries (POCKET debug), self-hits. Then HOT_LEARN=2 against
  HOT_LEARN=1. Holdout only once, at the end.

### P2. FOOD_GOAL: long-range pull toward remembered or beaconed fast-spawner clusters
- **Why:** gamma 0.82 makes anything past about 12 steps worthless, but 5% of tiles hold 70% of production on
  dev maps. Those fountains sit 9-20 steps from spawn (Devil, fountain_*, pockets_*, vault_*) and are
  rarely in the r0 view. A dragon that walks away from a fountain forgets it, and allies never learn of it.
  The known-map modules do this job on ranked maps; nothing does it on unseen maps.
- **Where:** a new `foodTargets` list in `Bot`, filled from `learned`/`gapSeen<=HOT_LEARN_FAST` tiles (needs
  P1's detection) and, at level 2, from a sonar FOOD message decoded in `readMessages()`. The direction loop in
  the main move function (about l.2362: `bfsFrom(t, pearls, area, areaCap)` fills `bfsDist` from each
  candidate `t`) reads `bfsDist[goal]` after each call.
- **Sketch:**
```cpp
#ifndef FOOD_GOAL
#define FOOD_GOAL 0        // 1: own memory, 2: + sonar FOOD beacons
#endif
#ifndef FOOD_GOAL_W
#define FOOD_GOAL_W 3.0    // score per step of progress (10 = one pearl)
#endif
#ifndef FOOD_GOAL_LOCAL
#define FOOD_GOAL_LOCAL 2.0 // only when best local 10*pearls is below this
#endif
// before the direction loop:
int goal = -1;
if (FOOD_GOAL && !w.known && myLen <= 6 && !iAmKing() && round < RP.splitStopRound) {
    // nearest (plain wrapDist) food target not seen in the last 3 rounds with >=2 other heads within 3
    goal = pickFoodTarget();
}
double goalD[4]; int minGoal = INF;
// inside the loop, right after bfsFrom(t, pearls, area, areaCap):
goalD[d] = goal >= 0 ? bfsDist[goal] : INF;  minGoal = std::min(minGoal, (int)goalD[d]);
// after the loop, before picking best (restructure: collect score[d] first, then add):
if (goal >= 0 && bestLocalPearlScore < FOOD_GOAL_LOCAL && minGoal < INF)
    for (d) if (goalD[d] == minGoal) score[d] += FOOD_GOAL_W;
// Level 2 message (only when the ray slot is free: no king/relay/warn this turn in that direction):
// [4-bit tag FOOD][12-bit tile][9-bit round][4-bit class][rest: 21-bit checksum, as in encodeKing]
// Sent at most every 8 rounds by a dragon within 2 of a learned hot tile, on 1-2 free directions.
```
  The bonus is a tie-breaker in size (0.3 pearl per turn). It must never beat survival (-150) or threat
  penalties. Because it only applies when local food is poor, fountain crowding caps itself: once a dragon
  can see the fountain, local food is high and the pull switches off.
- **Expected effect:** faster discovery and re-use of fountains on dev-style unseen maps, and more dragons
  pumping a pocket bank. It should be neutral on spread-food gen maps, where local food is rarely below the
  threshold.
- **Risks:** crowding and friendly head-ons at fountains (loong blog: 382 friendly head-ons vs 78 enemy),
  walking into enemy-held pockets (notes/14: opponents usually hold them already), and extra portal crossings.
  Sonar beacons can be intercepted, since enemy bodies absorb rays, and they cost ray slots after r250 (king
  relay has priority). Start at level 1 with no sonar.
- **Test plan:** FOOD_GOAL=1 on top of HOT_LEARN=1 against HOT_LEARN=1 alone, on lesson (fountain, pockets,
  vault, islands) plus blind Devil, Autarky, Dilemma and Trauma. Watch friendly head-on deaths (tools/friendly.py)
  and portal deaths. Then level 2 against level 1.

### P3. UNK_PRIOR calibration (cheap sweep first, then a map-adaptive prior)
- **Why:** the flat prior is 2x (gen) to 5x (ranked) above the true chance that a never-seen tile holds a pearl
  after r~60 (table in section 0). UNK_PRIOR=0.04 made it worse (0.375), and the lower side is untested. Under
  PEARL_ROUTE an unseen path is worth about 2.25 pearls, more than a visible pearl.
- **Where:** `World::rate()` and the unseen branch of `Bot::pearlValue()` (l.990-996), plus running counters in
  `analyse()`: `seenTiles`, `seenSpawners`.
- **Sketch:**
```cpp
#ifndef UNK_ADAPT
#define UNK_ADAPT 0
#endif
#ifndef UNK_CAP
#define UNK_CAP 0.5         // current cap on unseen value
#endif
// step 0 (no code): sweep -DUNK_PRIOR=0.005 and -DUNK_PRIOR=0.0025, and -DUNK_CAP=0.3 once the cap is a param.
// unseen branch:
double cap = UNK_CAP;
if (UNK_ADAPT && !w.known) {
    // empirical-Bayes share of spawners among tiles this dragon has seen (Beta(2,2) prior)
    double f = (w.seenSpawners + 2.0) / (w.seenTiles + 4.0);
    cap = UNK_CAP * std::min(1.0, f / 0.55);   // 0.55 = gen-map mean spawner share
}
v = cap * std::min(1.0, std::max(0, since) * r);
```
  Count only first sightings (`lastSeen[t] < 0` before this turn), so a dragon standing still does not
  inflate the counts.
- **Expected effect:** less drifting into barren space on starving or fountain maps. On P2 maps this lowers the
  unseen term, which gives the fountain pull more room. Unknown sign on spread-food gen maps, because the
  unseen term also acts as the de facto exploration drive. That is why the sweep comes first.
- **Risks:** too low leaves dragons idling in known-empty space. Split children start with f = 0.5 and quickly
  pick up the local share, which is fine.
- **Test plan:** first `UNK_PRIOR=0.005` and `0.0025` against v24 on gen, blind and lesson. If either is
  >= 0.52 pooled, try UNK_ADAPT=1 at the best value. Repeat the winner with PEARL_ROUTE=1 on both sides once
  Codex's port lands.

### P4. SPLIT_HANDOFF: pass hot and fountain knowledge from parent to child at the split
- **Why:** on an unknown map every split child starts with zero memory, and we split at 4 constantly, so most
  dragons are young. The engine makes a handoff almost free. After `SPLIT k` the child's body is the reversed
  rear (`actions.cc:Split`), so its tail touches the parent's new tail. A parent sonar **opposite its facing
  starts at its tail** (`sonar.cc`) and continues along the direction body[-2] to tail. When the tail is
  straight, the first tile it reaches is the child's tail, so the child receives it. The child also acts later
  in the **same round**, and its inbox is written at the start of its turn, so it reads the message on its
  first turn.
- **Where:** the split branch of the main move function (where `SPLIT k` is emitted) and the sonar-emission block
  (about l.1660-1690), plus the child-side decoder in `readMessages()`.
- **Sketch:** the parent recomputes its post-split body and checks that `plainStep(tail, dir(body[-2] to tail))`
  is the child's tail tile (else skip, or pick a head ray that hits the child). It sends
  `[tag HAND][tile A 12][tile B 12][class 2+2][checksum 20]`: the two best learned hot or fast tiles or
  fountain targets (from P1/P2), with symmetry and portal id pairs as later extensions. The child adds them to
  `learned`/`foodTargets` with `gmin=gmax` set as in P1. This must not overwrite the opposite-facing ray the
  bot already uses for king relay or warn: skip the handoff when that slot is taken.
- **Expected effect:** small by itself. It extends P1 and P2 to every newborn. Worth building only if P1 or
  P2 shows a gain.
- **Risks:** a bent tail makes the ray miss and hit something else. That is harmless apart from the leak and
  the checksum rejects it. It also adds code complexity.
- **Test plan:** after P1 and P2, SPLIT_HANDOFF=1 against the P1+P2 baseline on lesson pockets/fountain and
  blind Devil/Autarky. Check with BOTDBG that children log a received handoff on turn 1.

### P5. GAP_SAMPLES: replace LEARN_GAPS' estimator with exact reset samples, pooled over a block
- **Why:** consecutive observations give exact gap samples (section 1), and neighbouring tiles share the exact
  range 92-96% of the time. Pooling a 3x3 block's samples gives a good `max` estimate within a few rounds.
  LEARN_GAPS used the per-tile `max(tin+1)` envelope with a 0.75 fudge. It was neutral, most likely because
  of the narrow slice it touches (section 2), not the estimator.
- **Where:** `World::rate()` for `gmax<0`, `gapSeen` bookkeeping in `analyse()`.
- **Sketch:** `rate(t) = 2/(1 + Ghat)`, where `Ghat = max over the 3x3 block of gapMax * (n+1)/n` (n = pooled
  sample count, need n >= 3). Otherwise use UNK_PRIOR. It shares the data structures with P1.
- **Expected effect:** small. It helps re-visit timing only for tiles whose known spawn has passed, been eaten
  out of view, and lie within the gamma horizon.
- **Risks:** low. It is the same failure mode as LEARN_GAPS (neutral).
- **Test plan:** only piggy-back on P1 (HOT_LEARN=2 with pooling on/off), on gen and lesson.

### Considered and not proposed
- **Spatial smoothing of spawner status for unseen tiles:** the offline check gains only 1 point of captured
  direction value (section 0). It is the cheapest idea but has the lowest ceiling. Revisit only if P3 shows the
  unseen term matters a lot.
- **Symmetry-lite mirroring of countdowns or hot tiles:** mirror tiles are mostly on the enemy half (own-half
  share is about 0.47 everywhere), beyond the gamma horizon, and countdowns are unshared on 20% of loong-style
  maps. It only pays near the axis (fountain_b/c, Dilemma-style centre banks), and P2's memory covers those
  once they are seen. It has the same failure profile as INFER_SYM.
- **Sharing all observed spawners by sonar:** 4 u64 per turn cannot carry a map, and most observations are
  local anyway. P2 level 2 shares only the high-value fact (a fountain here).

## 5. Caveats
- Production figures assume no blocking. A tile that holds an uneaten pearl wastes its spawns, so true
  harvestable food on spread-food maps is lower, while on hot tiles every eaten pearl is replaced one round later.
- The offline simulation idealises the window: the whole 7x7 class is known and portals count as plain edges.
  It is a ranking-signal check, not a win-rate predictor.
- I did not verify on engine 1.2.2 that bot input still carries live countdowns. The C++ helper's
  `pearl_time`, our `filterByCountdowns` and POCKET_OBSERVED all rely on it. One BOTDBG game would confirm
  it: grep for countdown values in a dragon's view dump.
