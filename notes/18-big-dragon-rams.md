# 18: Why our big dragons get rammed (28 Sep 2026)

**Question.** Our dragons of length 8 or more die head-to-head on an enemy's turn about 0.5 times per game. The killer is usually a length 2-3 kamikaze. What did the bot see at its last decision before the ram, what could it have done instead, and why didn't the threat model avoid the ram?

**Data.**
- 233 server games: `replays/v16` (ledger) plus `replays/ab_*` (summary).
- 111 rams of our L≥8 dragons by an enemy, 0.48 per game. Schooltime 43 (7 games), Default 42 (104 games), Autarky 11, Slithery 10, Trauma 5.
- By source: v16 64, ab_base 15, ab_v16_dt 14, ab_v16 8, ab_v18 4, ab_v19 4, ab_v20 1, ab_v21 1.

**Scripts** (`notes/tools/rams/`, read-only over replays):

| script | what it does |
|---|---|
| `rams.py` → `rams.pkl` | Rebuilds the board at our last decision with `simulate(stop=(R0,id))`. Checks every legal option against every enemy's true reach. The options are 4 steps, 2-3-step sprints, `SPLIT 2`, and reverse split `SPLIT L-2`. True reach is a BFS of len−1 steps over free tiles, with the enemy's own tail vacating. The script also reproduces `computeThreats()`. |
| `agg.py` | Assigns each ram to a cause category. |
| `escapes.py` | Finds which escape existed and was visible to the bot. |
| `botview.py` → `rams_bot_*.pkl` | Feeds our dragon's exact 7×7 inputs (40 warm-up turns, real sonar messages and echoes) to the compiled binary of the version that played, with BOTDBG on. It then parses the per-candidate scores. |
| `risk.py` → `risk.pkl` | Empirical P(rammed) for every L≥8 move (46k moves). |
| `trigger.py` → `trigger.pkl` | How often a proposed rule would fire (50k decisions). |

**Fidelity check.** The replayed bot reproduces the real action in 104 of 110 cases. `variants/v21` makes the same choice in 102 of 110, so **v21 still has every cause below**.

## Numbers

- **Killer length:** L2 29, L3 46, L4 18, L5+ 18. So 68% were L≤3.
- **Killer head at our decision:** Chebyshev distance 1 in 37 cases, 2 in 50, 3 in 7. Only 17 were farther or not yet born.
- **Killer steps on the ram:** 1 step 54, 2 steps 37, 3+ steps 19.
- **Turn order:** the killer had a lower id (acted next round) in 30 rams and a higher id (same round) in 81. This does not matter: every enemy gets exactly one move between two of our turns, and each one sees our new head.
- **When:** 96 of 111 at r≥350. Every ram followed a plain 1-step move. We never split or sprinted on the ram turn.
- **Portals:** the killer crossed a portal on the ram 7 times.
- **Risk calibration** (`risk.py`, P(rammed | an enemy can reach our new head)):

| enemy can reach our new head with | P(rammed) |
|---|---|
| 1 step, L2-3, visible | **33/34 (97%)** |
| 1 step, any length | 64% |
| 2 steps, L3 | 33-60% |
| 2 steps, L4-5 | 23-25% |
| 3 steps, L4-5 | 10-14% |
| 3 steps, L6+ | ≤6% |
| 4+ steps | 0.2% |
| no enemy can reach | 12 / 44,893 |

Small enemies next to us ram every time. The current flat penalty (`25+4L`) treats this as a mild risk.

## Why the threat model didn't avoid it (`agg.py`)

| cause | rams | bot knew? | an escape existed |
|---|---|---|---|
| **A. All legal 1-step moves threatened** (the bot's own model agrees; replayed scores: 56 of 65 had best < −100 but depth ≥ 4) | **65** | yes | 44 |
| B. Enemy length underestimated: its tail is out of view, so `enemyVisibleLength` is 2 and reach is 1, while the true length is 3-8 | **21** | no | 12 |
| C. Unseen head across a portal (the killer crossed 6, we crossed blind 4, both v16/base only; KING_PORTAL_PENALTY since v19 covers ours) | 10 | no | 8 (plain step) |
| D. Head just outside the 7×7 view (2 of them with the body visible) | 4 | no | 3 |
| Chosen threatened tile while a bot-safe step existed (the alternatives had depth 2-5, so this was correct) | 4 | yes | – |
| Other: not reproduced by the model (4), newborn split child (2), BFS mismatch (1) | 7 | | |

**The threat penalty is not too small.** In only 4 rams did the bot pick a threatened tile over a bot-safe one, and those alternatives were dead ends. The real gaps are:
- **A.** When every step is threatened, the bot has no escape action.
  - Splitting is gated by `!threatened` (main.cpp ~2150).
  - The reverse split needs `bestDepth < 4` (`trapped`, ~2287), and in these cases depth was fine.
  - Sprints are never considered for fleeing.
- **B.** Reach is capped by the enemy's *visible* length.

Escapes available in the 65 A-cases, first by cost. A case counts only if the option is truly safe, has room (flood area ≥ L+3), and the bot's own model sees it as safe:

| escape | cases |
|---|---|
| 1-step | 1 |
| **2-step sprint (cost 1)** | **30** |
| SPLIT 2 / hold | 1 |
| **reverse split L−2** (tail in view) | **9** |
| 3-step sprint (cost 2) | 7 |
| nothing | 21 |

**Trigger rate** (`trigger.py`): "every legal step flagged by the current model" happens at 238 of 50,236 L≥8 decisions (about 1 per game), and 65 of those were rammed (27%). An escape that costs 1-2 segments there is cheap compared with losing L8-37.

## Fix 1: `KING_ESCAPE` (default 0). Estimate: ~35-45 of 111 rams (A + part of B)

**Where:** `bot/main.cpp` `decide()`, just before `// ---- trapped` (~2287), after the 1-step loop, where `threatAt`, `best`, `bestD` are known.

**Rule.** Fire only if `myLen >= KING_MIN_LEN`, the best 1-step candidate has `threatAt > 0`, and every legal 1-step tile is threatened.
- **Candidate 1, 2-step sprints (cost 1).** Try all `DIRC[a]DIRC[b]` pairs.
  - Simulate our body properly: step 2 is checked against the body after step 1, and the tail drops 2 segments.
  - The landing tile needs `threatAt == 0`, `surviveDepth ≥ wantDepth/2`, and `bfsFrom` area ≥ myLen.
  - Score it the same way as a step, minus `ESC_SPRINT_COST * (steps-1)`.
- **Candidate 2, reverse split.** Use `SPLIT myLen-2` if `tailHasExit(myLen-2)` and `threatAt[trail.back()] == 0`, and no visible enemy head is within `wrapDist ≤ 2` of the tail.
- **Candidate 3, 3-step sprints (cost 2).** Only if nothing above works.
- **Otherwise** keep the step, as now.

```cpp
#if KING_ESCAPE
if (myLen >= KING_MIN_LEN && bestD >= 0 && threatAt[step(myHead, bestD)] > 0) {
    bool allThr = true;
    for (int d = 0; d < 4; d++) { int t = step(myHead, d);
        if (t >= 0 && !(occId[t] >= 0 && freeT[t] > 1) && threatAt[t] == 0) allThr = false; }
    if (allThr) {
        std::string bestSeq; double bs = -1e18;
        for (int n = 2; n <= 3 && bestSeq.empty(); n++)          // 2-step first, 3-step only if needed
            for (int code = 0; code < (n == 2 ? 16 : 64); code++) {
                int dirs[3] = {code & 3, (code >> 2) & 3, (code >> 4) & 3};
                int t = simulateSprint(dirs, n);                  // -1 if any step dies (own body per-step, kelp, occupied)
                if (t < 0 || threatAt[t] > 0) continue;
                double p; int area; bfsFrom(t, p, area, 3 * myLen + 30);
                int dep = surviveDepth(t, SURVIVE_DEPTH);
                if (area < myLen || dep < SURVIVE_DEPTH / 2) continue;
                double s = 10.0 * p + dep - ESC_SPRINT_COST * (n - 1);
                if (s > bs) { bs = s; bestSeq.clear(); for (int k = 0; k < n; k++) bestSeq += DIRC[dirs[k]]; }
            }
        if (!bestSeq.empty()) { out += "MOVE " + bestSeq + "\n"; pending.clear(); /* push tiles to pending */ return; }
        int tail = trail.size() == (size_t)myLen ? trail.back() : -1;
        if (tail >= 0 && units < w.unitLimit && tailHasExit(myLen - 2) && threatAt[tail] == 0) {
            out += "SPLIT " + std::to_string(myLen - 2) + "\n"; pending.clear(); pendingSplit = true; kingSelf = false; return;
        }
    }
}
#endif
```

**Notes.**
- `simulateSprint` can reuse the per-step logic of the existing sprint ram (`tryRam`, ~1949).
- `threatAt` is computed on the pre-move board. That is fine: an enemy that can reach a tile 2 away through our current head's area is blocked by our body anyway.
- `ESC_SPRINT_COST` should be about 15.
- Also lift the `!threatened` gate for this path only.

**Estimate.** Of the 65 A-cases, 30 have a 2-sprint escape, 9 a reverse split and 7 a 3-sprint, all bot-visible. Assume about 80% of those escapes survive the next move. That gives ~35 A-rams saved, plus 4-8 from B once Fix 2 flags them.

**Cost.** About 1 segment roughly once per game. Also check the reverse-split crown hand-off (`kingSelf=false`, the same as in the trapped split).

## Fix 2: `THREAT_TAIL_UNKNOWN` (default 0). Estimate: ~8-12 rams (B)

**Where:** `computeThreats()` (~1744-1745).

When an enemy's tail isn't in view, its length is at least `vis`, possibly more. The rule:
- Take the enemy's segments. If none of them is a visible tail (the same tail test as the TAIL_THREAT block), use reach `max(vis-1, UNK_MIN_REACH)`.
- Set `UNK_MIN_REACH` to 2.

```cpp
int vis = enemyVisibleLength(s.id);
int reach = std::max(1, vis - 1);
#if THREAT_TAIL_UNKNOWN
if (myLen >= KING_MIN_LEN && !enemyTailVisible(s.id)) reach = std::max(reach, UNK_MIN_REACH);   // 2
#endif
reach = std::min(reach, maxReach);
```

`enemyTailVisible(id)`: some segment of `id` has no same-id segment pointing into it, and all four of its neighbours are visible. This factors out the existing check in the TAIL_THREAT loop (~1776-1786).

**Numbers.**
- With the rule (UNK_MIN_REACH=3 tested; 2 not run on these rams), our chosen tile is flagged in 19 of 21 B-rams.
- It is cheap. At the value 2 it newly flags our chosen move in 50 of 50k decisions, and 13 of those were rammed (26%). Only 22 of the 50 had an unflagged alternative.
- At 3 it flags 206 decisions (20 rammed). Too timid, so use 2.
- Most B-cases then fall into "all steps threatened", so the saves need Fix 1. Alone, it saves ~4 (plain-step escapes).

## Fix 3: `KING_PORTAL_MOUTH` (default 0). Estimate: ~5 rams (C, killer crossed)

**Where:** the scoring loop in `decide()`, next to `if (portalExit[t])` (~2255).

An enemy head can come out of a portal next to us without ever being in view.

**Rule.** For `myLen >= KING_MIN_LEN`, penalise a landing tile `t` when one of its edges is a portal whose far side is out of view. We know the far tile (`u = step(t,d) != w.plainStep(t,d) && !visible[u]`). A head there moves onto `t` in one step.

```cpp
#if KING_PORTAL_MOUTH
if (myLen >= KING_MIN_LEN) for (int d2 = 0; d2 < 4; d2++) {
    int u = step(t, d2);
    if (u >= 0 && u != w.plainStep(t, d2) && !visible[u]) { score -= KING_PORTAL_MOUTH_PEN; break; }   // ~40
}
#endif
```

**Numbers.**
- In 6 rams the killer came through a portal; in 5 of those (4 on Default) a plain-step escape existed.
- The "we crossed blind" variant (4 rams) is already covered by `KING_PORTAL_PENALTY=100` since v19.
- Keep `PM_POR_KPORTAL`-style overrides off on Portals, where the module routes through portals on purpose.

## Not worth it / notes

- **Raising the threat penalty** would fix at most 4 rams: the bot already avoided every threatened tile that had a safe alternative with room.
- **KING_THREAT_REACH=4** is not binding. No ram needed more than 4 steps from a visible head, and 4+ step reach gives only 0.2-0.3% real risk.
- **KING_RAM_AVOID** (0) and the KING_V2 keep-distance are proximity penalties. They don't help when every step is equally threatened.
- **Schooltime** (43 rams in 7 games, 33 of them category A) is where Fix 1 matters most. Big dragons walk the crowded yard (SCH_YKING pull). Consider also capping the yard pull when ≥2 enemy heads are within 3.
- **Test plan.**
  - Mechanism: rerun `rams.py` + `agg.py` on the new batch. Rams per game of L≥8 should fall from 0.48, and category A should shrink.
  - Watch L≥8 sprint/split counts in the endgame (cost side).
  - Server A/B on Default + Schooltime.
