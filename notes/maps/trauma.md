# Trauma (ranked map id 15): map-specific plan

Data used:
- **Our games:** 35 real games. v7 ladder 16, ch1 5, ch2 5, ch3 1, ch5 5, ch8 3. The current generation (v7, ch5, ch8) is 24 games, record **17-7**.
- **Top-team games:** 24 in `notes/replays/permap`, of which 22 are unique. 10 are from 05:45 UTC. I fetched 14 more at 21:26-21:39 UTC with `permap_fetch.py 24 1850 Trauma`; that was read-only GETs.
- **Scripts:** `notes/tools/trauma/`.
  - `tr_an.py` gives our per-game timelines.
  - `top_an.py` does the same for the top teams.
  - `hot.py` gives factory usage for one team.
  - `king.py` gives king position and eat sources, in A-frame coordinates.
  - `open.py` traces the opening.
  - `trace.py` is an event dump for a box of tiles and a range of rounds.

## 1. The map

- 48x24 with `SYMMETRY xy`, which is a 180° rotation. B's tile is (47-x, 23-y), and N<->S and E<->W swap. **Every coordinate below is in A's frame.**
- The border is kelp all the way round, so nothing wraps.
- Starts, head first, len 4:
  - A: (4,15) and (4,2), both facing E.
  - B: (43,8) and (43,21).
- Pearls: 130 tiles have gap [1,200]. There are **12 hot tiles with gap [1,1]**, 6 per team. Nothing sits in between: no tile has a gap of 20 or less other than the hot ones.

Three zones per team:

| zone | tiles | pearls | access |
|---|---|---|---|
| **home pen** x 0-10, all y (264 tiles, fully open) | both starts | only 10 tiles: (0..4, 0) and (0..4, 23), gap [1,200] | **only 2 portals**: (10,0) E <-> (16,7) W, and (10,20) E <-> (26,22) W. The x=10\|11 edge is kelp everywhere else. |
| **maze** x 11-36 | 1-wide corridors | 122 tiles, [1,200] | shared with the enemy; centre (24,12) is 38 steps from our pen |
| **hot factory** | (11,8) (11,9) **(11,10) (11,11) (11,12) (11,13) (11,14) (12,14)** | the 6 bold tiles are hot [1,1] | a 1-wide **dead end**. The only way in is (12,8) W to (11,8), then S. The dead end is (12,14), whose only neighbour is W. |

- B's factory: (36,15) N to (35,9), dead end (35,9), mouth (35,15). B's pen is x 37-47.
- Distances:
  - (4,2) start to the first hot tile: 19 steps.
  - (4,15) start to the first hot tile: 32 steps.
  - Factory mouth (12,8) to our pen: **8 steps**, path (13,8) (14,8) (15,8) (15,9) (16,9) (16,8) (16,7), then W to (10,0).
  - Start to enemy start: 98 or more steps.
  - Maze tile to pen: median 43 steps, p90 72.
- **Pens are never invaded.** In 10 checked games, ours and the top teams', there were 3 enemy moves inside a pen in total.

## 2. How we do on Trauma

Current generation (24 games): 17-7. **All 7 losses were at round 500 on longest dragon.** None was an elimination.

| game | opp | first ≥10 (us / them) | final king (us / them) | where their king lived |
|---|---|---|---|---|
| v7 397223 | life is NP hard | 342 / 425 | 16 / 18 | pen at the end |
| v7 386381 | test-clone | 370 / **157** | 19 / **30** | **pen, one dragon all game** |
| v7 380703 | goblin gooners | never / **136** | 9 / **29** | **pen, the unsplit starter, 25 spawn eats** |
| v7 355732 | ANON_TOKYO | never / never | 8 / 9 | pen |
| ch5 403816 | usagi | 368 / 460 | 15 / 18 | pen (1,10) at r475 |
| ch8 416132 | uhhhhhhhh | 347 / 382 | 16 / 17 | pen at the end |
| ch8 416142 | Maccas | 376 / 409 | 16 / 25 | pen, fed from r425 |

Medians, wins against losses:
- Our first dragon ≥10: r379 / r370.
- Final king: 20 vs 11 in wins; 16 vs 18 in losses.
- Hot eats: 200 / 189 per game. Hot eats after r300: 41 / 23.

**What goes wrong:**
1. **Our king forms very late and in the wrong place.** Our longest dragon is 3-6 until about r330 in every game (`tr_an.py`), and it lives in the maze: (21..35, 1..19) in the king logs.
   - Top winners have a king ≥10 by r100-150. 龙虎豹 is at 9-10 by r100, 16 by r200, 21 by r300 and 45-60 by r499.
   - That king lives in the **home pen** from turn 0 (`king.py`: every 50-round bucket has it at x≤8).
   - Our 3 heavy losses were to opponents who did only this: one unsplit starter circling their pen, reaching 25-30.
2. **Our big dragons die in the maze.** Current generation: 27 deaths of dragons with L≥8. The locations are (27,12), (21,13), (24,19), (20,14), (33,9), (22,15), (30,2) and so on.
   - Worst case: ch8 416132 lost 4 dragons of L8-9 to head-ons between r357 and r416, at (27,12), (21,13) and (24,19), then lost 16 v 17.
   - In the pen they would have been safe.
3. **Our factory runs at half speed and stops late.**
   - Ours runs at 0.35-0.45 eats/round. It falls to 0-10 per 50 rounds after r300, because the unit cap blocks the escape-split and SPLIT_STOP is 350.
   - 龙虎豹 runs at **exactly 50 per 50 rounds from r50 to r500 (479/game)**. 中国人能飞 gets 334-366.
   - Our corridor deaths are HitSelf of L2-3 (46 of 53 in 416132). Theirs are HitWall of L2 at the dead end, which is part of the plan.
4. The opening splits **both** starters at r0. Our first unit reaches the factory at r30, against r18 for 龙虎豹.

## 3. How the top teams play it

Sources: 22 unique games, winners and losers. `top_an.py`, `king.py`, `hot.py`, `trace.py`.

- **King = one starter that never splits and never leaves the home pen.**
  - 龙虎豹 kept the (4,15) starter (id 1) as king in 3 of 3 games. It circled the pen perimeter, x 0-4, eating the (0..4,0) and (0..4,23) pearls plus feeder corpses.
  - Sabotage-d and 中国人能飞 move their king into the pen by r300 and keep it there.
  - King eat sources: 60-70% own corpses, the rest spawns (for example 32 corpse + 20 spawn).
- **The factory is a scripted 4-round cycle.** It gives 1 hot eat per round and exports one L2 dragon every 4 rounds (trace 423933 r100-108, mirrored to A's frame):

```
state S0 (round r):   X = len4 [(11,10),(11,11),(11,12),(11,13)], head (11,10) facing N
r   : X SPLIT 2  -> X=[(11,10),(11,11)] (exits: N,N,E); child C=[(11,13),(11,12)] facing S
      C moves S to (11,14), eats -> len3
r+1 : X moves N (11,9);   C moves E to (12,14) (dead end), eats -> len4
r+2 : X moves N (11,8);   C SPLIT 2 -> C=[(12,14),(11,14)] stays; child D=[(11,12),(11,13)] facing N
      D moves N to (11,11), eats -> len3
r+3 : X moves E (12,8) and leaves; C moves E into kelp and dies (HitWall, leaves 1 pearl on (12,14));
      D moves N to (11,10), eats -> len4  == S0 again at r+4
```

- The cycle eats (11,14), (12,14), (11,11) and (11,10) once each per 4 rounds. (11,12) and (11,13) are always covered by a body.
- Each cycle nets +1 unit (2 splits, 1 death). In 423933 there were 118 corridor deaths, 116 of them HitWall of L2.
- A newly split child acts later in the same round, as a new process. So every step above works from the dragon's current body alone and needs no memory.

- **The opening (龙虎豹, A frame):**
  - r0: the (4,2) starter does SPLIT 2. Its head half goes (7,2), (9,1), (10,0), then E through the portal to (16,7), (13,8), (11,8). It is at the factory by r18.
  - It eats the 6 hot pearls that piled up, reaching L8 at (12,14) by r24.
  - At the dead end it peels off SPLIT 2 once per round. The first two children walk out; the third rebounds and starts the cycle at r29. The L2 remnant dies at r28.
  - The (4,15) starter does not split. It walks N to (4,0), then around the pen: L7 at r50, L10 at r100.
- **Feeding pipeline:** the factory's L2 exports go through the mouth, then (16,7), then W to (10,0) into the pen. That is 8 steps.
  - 龙虎豹 has 51-53 deaths in its own pen before r300, and 49-87 after.
  - Near-king deaths are mostly HitSelf, i.e. deliberate suicides.
- **How pen kings die:** only by head-on at the portal arrival tiles, and **always against an ally** arriving blind through the portal.
  - 353379: L30 at (10,0) r390, rammed by its own L3.
  - 423943: L27 at (10,0) r350; the king moved E into the portal and hit its own L2.
  - 423953: L13 at (10,0).
  - 423923: L9 at (10,20).

## 4. Proposed behaviours

Ranked by expected value. Each is a flag in `bot/maps/trauma.hpp`. The helpers:
- `A(t)`: maps a tile to A's frame. For side B it is (47-x, 23-y).
- `dA(d)`: maps a direction the same way. For side B it is (d+2)%4.
- `inPen(t)`: A-frame x ≤ 10.
- `inFac(t)`: t is one of the 8 corridor tiles.
- Side comes from `w.myTeam` ('A' or 'B').

### T1: pen king from turn 0 (`TRA_PENKING`, score hook, plus a one-line declare in override)
**Fixes loss causes 1 and 2.**
- **Declare.** In `traumaOverride`, when `round <= 2`, `myLen >= 4`, and `A(myHead)` is (4,15) or (5,15): set `kingSelf = true` and return false. Only one starter per team matches. (5,15) covers the round after the first move.
  - `kingSelf` already blocks normal splitting, because `RP.kingDeclare = 1` on Trauma.
  - It also broadcasts the king sonar every turn (`iAmKing() && kingSelf`).
- **Stay in the pen.** Define `penKing = kingSelf || (myLen >= 8 && inPen(myHead))`. In `traumaScore`, for a pen king:
  - `inPen(myHead) && !inPen(t)`: **-400**. This is the portal E from (10,0) or (10,20).
  - `A(t)` is an arrival tile, (10,0) or (10,20): **-120**. `A(t)` is a neighbour of one, (9,0), (10,1), (9,20), (10,19) or (10,21): **-50**. Rationale: 4 of 4 observed pen-king deaths were ally head-ons on these tiles.
  - A pen king outside the pen (for example after a restart) gets **+6 × (penDist[myHead] - penDist[t])**. `penDist` is a static BFS through portals, like `schD` in `schooltime.hpp`.
- **Keep the pen's pearls for the king.**
  - A non-king dragon with `round < RP.feedStart`, not a feeder under T3, and `!inPen(myHead) && inPen(t)`: **-60**.
  - A non-king dragon inside the pen at `round < RP.feedStart`: **+3 × (exitDist[myHead] - exitDist[t])** toward the two arrival tiles. This moves the r0 split halves out.
- Expected result: goblin gooners and test-clone reached 29-30 with this and nothing else. That is more than our median final king in wins (20).

### T2: scripted hot factory (`TRA_FACTORY`, override hook)
**Fixes loss cause 3. It also supplies T3's feeders.**

The override runs only when `inFac(myHead)` or `A(myHead) == (12,8)`. In A-frame directions, for dragon `me` with length L:
1. **Head on (12,14) (dead end).**
   - If `L >= 4 && units < 64`: `SPLIT 2`. This peels the tail. With L≥6 it repeats every round, which is the bootstrap.
   - Otherwise: `emitMove(E)`, a deliberate HitWall that drops a pearl on (12,14).
2. **Heading S**, where `trail[1]` is N of the head, head x=11, y 8-13: `emitMove(S)`. At (11,14): `emitMove(E)`.
3. **Heading N** (`trail[1]` is S of the head):
   - At (11,10) with `L >= 4 && units < 63`: `SPLIT L-2`. The child takes the tail and heads S; the parent keeps 2 and leaves.
   - Otherwise: `emitMove(N)`, and at (11,8) `emitMove(E)`.
   - With `units >= 63` it just leaves, so the cycle pauses and never traps anyone.
4. **Entry** (score hook). Moving from (12,8) W onto (11,8):
   - **+40** when `L <= 3 && units <= 60 && round < 470`, and none of (11,8), (11,9), (11,10), (11,11) holds a visible segment. All are visible from (12,8).
   - **-500** when any of them holds a segment. A head-on inside the corridor kills both dragons.
   - A non-factory dragon moving onto (12,8) or (13,8) while (11,8)-(11,10) is busy: **-40**, so the exit stays clear.
5. **Opening rush.** At `round <= 3`, the len-2 head half of the (4,2) starter (`A(myHead)` x ≤ 6, y ≤ 3) gets **+8 × (facDist[myHead] - facDist[t])** until it reaches (11,9). The goal is r18 at the factory instead of r30.

Checks:
- The unit cap (64) is the only thing that can stall the cycle.
- The enemy never came near our factory in any game.
- Target: about 450 hot eats per game (we get 189-200 now), sustained after r300. That is **about +250 team length per game**, and 110+ L2 units available to T3.

### T3: factory exports feed the pen king (`TRA_PENFEED`, override and score)
**Turns T2's output into king length the way 龙虎豹 does.**
- **Who feeds.** A dragon is a feeder when its process began inside the factory: its first turn had `inFac(myHead)`. Keep a static `bool facBorn`, set on the process's first turn.
  - It must also have `round >= TRA_PF_START` (test 60 and 150), `myLen <= 3`, and `!penKing`.
  - For `units <= TRA_PF_RES` (test 16), feeders act as normal dragons instead.
- **Getting there.** Score: **+8 × (penDist[myHead] - penDist[t])**. The route is (12,8), then 8 steps through (16,7) W into (10,0).
  - Once in the pen with the king's head visible: pull toward the tile 2 ahead of the king, `step(step(kingHead, kingDir))`. `kingHead` and `kingDir` come from `segs`: the own-team head whose visible segment count is largest, or the `kingId` from sonar.
- **Dying.** In `traumaOverride`, when all of these hold:
  - `myHead` is 1-2 tiles straight ahead of the king's head, or directly beside it;
  - no enemy head is within 4;
  - the king is ≥ myLen + 2;
  
  then emit `emitMove((myDir+2)%4)`, a suicide into the neck. This matches the existing KING_V2 feed rule, but does not need `feedPhase()` or a king heard by sonar.
- **Why a separate rule.** The pen's kelp wall blocks sonar, so dragons in the maze never hear a pen king. The stock `shouldFeed()` path would never fire for them.
- Upper bound: 1 pearl per 4 rounds × about 400 rounds = +100 king length. 龙虎豹 realises about +30-40 of that.

### T4: late consolidation into the pen (`TRA_MERGE`, score only; optional, test after T1-T3)
- From `round >= 400`, a non-king dragon with `units > 4` and `myLen >= 4` gets **+5 × (penDist[myHead] - penDist[t])**, and feeds on arrival through the T3 rule, with the size condition relaxed to king ≥ myLen + 2.
- 400 is chosen because the median maze-to-pen distance is 43 steps and the p90 is 72.
- Evidence: at r450 in our losses, the non-king length left in the maze was 30-70. For example, 416142 had 14 units and 88 total, with a king of 16.
- Risk: blind arrivals queueing at (10,0) and (10,20). Cap it by accepting a merge target only when no own head is visible within 2 of the arrival tile.

### RP settings to sweep with these
- `PM_TRA_KS`: 275 (now) against 450. The later value keeps random second kings from being declared in the maze, where our L≥8 dragons die 1.1 times per game.
- `PM_TRA_FS`: 330 (now) against 250. This only affects the stock feed path.
- Keep `PM_TRA_SS` at the default 350. The factory is exempt anyway, because it splits through the override.

## 5. Test plan
- Measure each flag on its own, then together, on Trauma only. Use the same seeds as the other modules:
  - `tools/pool.py 'bot:-DTRA_PENKING=1' --pool variants/v8,variants/v10h --maps trauma --seeds 10 --jobs 6`, and the same for `TRA_FACTORY`, `TRA_PENFEED`, and the combination.
- Self-play is a fair test here. The pens never interact and the losses are king races, so local length at r500 is the metric.
- Also log per game: hot eats (expected about 450), king length at r100, r200, r300 and r499, and pen-king deaths at the arrival tiles.
- Guard run: devil and trophy against v10h, 12 games, as for the other modules.
