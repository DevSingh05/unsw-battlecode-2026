# Lever: budget-lookahead (REPLY_SEARCH)

Patch: `notes/levers/budget-lookahead.diff` (against `bot/main.cpp` and `bot/params.hpp`). Working copy: `notes/levers/budget-lookahead/src/bot/`. Every change sits behind a new flag that defaults to 0. With the flag off, play is identical to `bot/`: I decoded both replays on Default and Schooltime (seed 11) and every event matched except the CPU fields.

## 1. Where the per-turn points go today

I added `PROFILE_POINTS` (local only). It times each section on the sandbox clock, where 1 ms = 1M points, and appends one `LOG prof ...` line per turn. Sandbox runs, both sides = our bot (M = million points):

| map | size | total p50 / max | parse | analyse | bfsFrom (4 cands) | surviveDepth | stdout write |
|---|---|---|---|---|---|---|---|
| Default | 32x32 | 6.1 / 7.2M | 1.3 | 0.4 | 1.2 (max 1.7) | **0.02** | ~2.5 (fixed per write) |
| Schooltime | | 7.1 / 14.4M | 1.3 | 0.7 | 1.8 (max 6.4) | 0.02 | ~2.5 |
| Slithery | | 6.1 / 8.4M | 1.4 | 0.6 | 0.9 | 0.01 | ~2.5 |
| big_empty | 64x64 | 12.3 / 29.5M | 1.4 | 1.2 | 6.2 (max 23) | 0.02 | ~2.5 |
| gen g2026_16 | 64x64 | 17.1 / 38.9M | 1.4 | 1.7 | 8.8 (max 32) | 0.02 | ~2.5 |

- About 90% of the budget goes unused.
- The only cost that grows with map size is `bfsFrom`, mostly PEARL_ROUTE on 64x64 maps.
- The survival DFS is almost free: about 0.02M for all four candidates. It usually finds a full-depth path on its first branch.

**So the cheap place to spend spare budget is more survival searches, not more BFS.**

## 2. What REPLY_SEARCH does (PLAN.md Q8, extended)

It runs only for dragons with L >= `REPLY_MIN_LEN` (8), on each candidate step `t` that already has survival depth >= 2.

1. **Pick the enemies.** Take the enemy heads within Manhattan distance `REPLY_RADIUS` (3) of `t`, nearest first, at most `REPLY_MAX_ENEMIES` (3).
2. **List their replies.** A reply is any legal 1-step move: not kelp, the tile is free when the enemy moves, and it is not `t` itself. A reply onto `t` is the ram, which `threatAt` already prices.
3. **Check every joint combination** (at most 3^3 = 27):
   - Each reply tile becomes enemy body (`freeOther = len+2`).
   - Every tile the replied head can reach on its next move is banned for our 2nd step. Reach uses the same rule as `computeThreats`: visible length - 1, the THREAT_TAIL_UNKNOWN bump, and the king cap.
   - Re-run `surviveDepth(t)` with a 6000-node cap.
4. **Score the worst combination.**
   - `worst <= 1` means "forced": every 2nd step is threatened or lethal. That is the state that preceded 65 of the 111 big-dragon rams (notes/18, cause A).
   - Penalty = `REPLY_SHORT_PEN * min(shortfall, 10)` (12 per step), plus `REPLY_FORCED_PEN + REPLY_FORCED_PER_LEN * L` (40 + 3L) when forced.
   - The penalty is **capped at `REPLY_CAP_FRAC` (0.8) x the direct-threat penalty (25+4L)**.
5. **Keep it inside the budget.** No new reply check starts once `REPLY_BUDGET_M` (45M) points have been spent this turn, measured from after parse on the sandbox clock. A running check stops at 55M.

**Why the cap exists.** Without it, the first version moved 9 of 27 changed decisions from a threat-free "forced" tile onto a tile an enemy head could ram right away. From notes/18, P(rammed) is 97% for a visible L2-3 head one step away, but only ~27% for the "every step threatened" state, and KING_ESCAPE now has sprints and splits for that state. A forced tile must never rank below a tile that can be rammed now.

**Generality.** Nothing here depends on the map: no names, no tables, no known-map data. Only the visible heads, their visible lengths and the time-aware free map are used, so it works the same on unseen maps.

## 3. Mechanism evidence: the 111 real server rams

`notes/levers/budget-lookahead/replycheck.py` reuses the notes/18 harness (`notes/tools/rams/botview.py`):
- For each ram, it feeds our dragon's exact server views from R0-40 to R0 (tiles, bodies, sonar, echoes) to two native binaries with BOTDBG on.
- The binaries are `base` = `bot/` (v28 defaults, KING_ESCAPE on) and `cand` = base + `REPLY_SEARCH=1`.
- It then compares every decision.
- `analyze.py` summarises the results.

"Pre-ram" means the 3 decisions before the ram turn. "Ordinary" means decisions 6 or more turns before it. Those are still endgame turns with enemies nearby, so they make a fair over-caution control.

| config | pre-ram decisions changed | ordinary decisions changed | rams with a changed pre-ram decision | changed onto a directly threatened tile |
|---|---|---|---|---|
| R3, pens 40/3/12, no cap | 19 / 311 (6.1%) | 8 / 2065 (0.39%) | 16 (14 cause A) | 9 of 27 (bad) |
| R3, low pens 15/1.5/3 | 11 / 311 | 4 / 2065 | 11 | – |
| R4, max 4 enemies | 24 / 311 (7.7%) | 21 / 2065 (1.0%) | 21 | – |
| **R3, 40/3/12, cap 0.8 (shipped defaults)** | **12 / 311 (3.9%)** | **4 / 2065 (0.19%)** | **12 (11 of the 65 cause A)** | **0 of 16** |

With the shipped defaults, every changed decision (16, pre-ram and ordinary together) goes from a threat-free tile where some enemy reply leaves us no safe 2nd step to a threat-free tile whose worst reply still leaves full survival depth (12). Two examples:
- 512101 Default, L30, R0-1: S (forced) -> W (worst depth 12).
- 517225 Default, L18, R0-1: N (forced) -> W.

Across the pre-ram window the played move was forced in 48 of 311 decisions. In the other ~36 no unforced threat-free alternative existed, so a 1-ply check cannot help there; KING_ESCAPE still covers those at R0.

**Expected effect.**
- About 11 of 111 rams have a clean earlier avoidance. Rams run at ~0.48/game, so that is roughly 0.05 big-dragon losses per game.
- Decisions change on about 0.2% of ordinary big-dragon turns.
- This is a small, low-risk gain aimed at the king-loss failure mode (kings die 0.57/g vs 0.22 for top teams). Its value grows once kings exist on unseen maps.
- Radius 4 catches more rams (21), but it changes 5x as many ordinary decisions. I kept R3 as the default. `-DREPLY_RADIUS=4 -DREPLY_MAX_ENEMIES=4` is the next variant to try if R3 tests neutral-positive.

**Arena sanity** (4 single games, `--jobs 1`, vs v28 on Schooltime and Default, replays in `notes/levers/budget-lookahead/replays/`): 2-2, with the side deciding each game. That is the usual self-play pattern, and self-play rarely rams big dragons, so these games don't measure the effect. Real validation needs a pool/unseen run, or better a server A/B on Default and Schooltime (maps with many rams).

## 4. CPU cost

- **Measured**, sandbox, both sides REPLY_SEARCH=1 with the governor disabled (`REPLY_BUDGET_M=1000`):
  - The reply section never exceeded **0.40M points per turn**: big_empty 0.40, g2026_16 0.28, Schooltime 0.16, Slithery 0.17.
  - It fires on about 1-7% of turns.
  - Game-wide maxima were unchanged by it: 38.9M on 64x64, all from bfsFrom.
- **Governor check:** with `REPLY_BUDGET_M=0` the section never runs (0.00 on every turn). The sandbox `steady_clock` really does meter points, so the cap works on the judge.
- **Theoretical worst case:** 4 candidates x 27 combinations x 6000 nodes. The governor bounds it: no new check after 45M, a hard stop inside a candidate at 55M, then at most the last candidate's bfsFrom (up to ~8M on 64x64) and a 2.5M write. That is under ~70M even in the pathological case.
- **Typical cost:** +0.05M on turns where it fires.

## 5. Risks

- **Over-caution**, the old failure of blanket king penalties (KING_RAM_AVOID, corridor penalty). This one fires only when a specific reply forces us, changes 0.19% of ordinary decisions, and never trades onto a threatened tile.
- **Enemy model.**
  - Only 1-step replies are modelled. An enemy sprint reply (L3+, 2 steps) is not enumerated, but its next-turn reach is banned.
  - Enemies beyond radius 3 are treated as static.
  - The ban ignores our own new body, so it is slightly conservative.
- **Invisible heads:** these don't help with causes B (length underestimate), C (portals) or D (out of view). 0 of those 40 rams changed.
- **Clock:** the governor relies on the sandbox clock. If the judge ever ran on wall time instead, fast native CPUs would just run more checks, which is still bounded by the node cap.

## 6. Flags

| flag | default in patch | recommended test |
|---|---|---|
| `REPLY_SEARCH` | 0 | 1 |
| `REPLY_MIN_LEN` | 8 | 8 |
| `REPLY_RADIUS` / `REPLY_MAX_ENEMIES` | 3 / 3 | 3/3; then 4/4 |
| `REPLY_NODE_CAP` | 6000 | 6000 |
| `REPLY_FORCED_PEN` / `_PER_LEN` / `REPLY_SHORT_PEN` | 40 / 3 / 12 | as is |
| `REPLY_CAP_FRAC` | 0.8 | 0.8 (0.6 more timid-safe) |
| `REPLY_BUDGET_M` | 45 | 45 |
| `PROFILE_POINTS` | 0 | local profiling only (adds a LOG line per turn) |

## 7. Suggested test plan (main agent)

1. **Pool/unseen regression** with `bot:-DREPLY_SEARCH=1` vs v28 (gen, blind, lesson, ladder). Expect about 0.50 locally: self-play rarely has big dragons among small enemies. Accept if it doesn't regress.
2. **Server A/B** on Default + Schooltime vs about 10 peers. The mechanism metric is L>=8 rams/game (rerun `notes/tools/rams/rams.py` + `agg.py`), which should drop mainly in cause A.
3. **Mechanism re-check for any variant:**
   ```
   c++ -std=c++20 -O2 -DREPLY_SEARCH=1 [-D...] -o BIN notes/levers/budget-lookahead/src/bot/main.cpp
   python3 notes/levers/budget-lookahead/replycheck.py BASE_BIN BIN OUT.pkl
   python3 notes/levers/budget-lookahead/analyze.py OUT.pkl
   ```
   Run these from the project root. It takes about 5 minutes and plays no games.

Tools in `notes/levers/budget-lookahead/`:
- `mkvar.sh name "FLAG=V ..."` bakes flags into `builds/<name>/` for sandbox runs. It archives old builds and never deletes.
- `replycheck.py` and `analyze.py` are described in section 3.
